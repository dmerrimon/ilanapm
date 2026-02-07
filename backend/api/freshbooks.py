"""
FreshBooks OAuth and billing API endpoints.

Provides endpoints for:
- OAuth authorization flow
- Invoice retrieval
- Invoice PDF access
"""

from fastapi import APIRouter, HTTPException, Query, Request, Response
from fastapi.responses import RedirectResponse, StreamingResponse
from typing import Optional
import logging
from urllib.parse import quote
from io import BytesIO

from services.freshbooks_service import freshbooks_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth/freshbooks", tags=["freshbooks"])
billing_router = APIRouter(prefix="/portal/customer/billing", tags=["billing"])


# ============================================================================
# OAuth Endpoints
# ============================================================================

@router.get("/authorize")
async def initiate_oauth(org_id: str = Query(..., description="Organization ID to associate with FreshBooks account")):
    """
    Initiate OAuth flow by redirecting user to FreshBooks authorization page.

    Args:
        org_id: Organization ID to link FreshBooks account to

    Returns:
        Redirect to FreshBooks authorization page
    """
    if not freshbooks_service.is_configured():
        raise HTTPException(
            status_code=503,
            detail="FreshBooks integration is not configured. Contact support."
        )

    # Use org_id as state parameter for CSRF protection
    auth_url = freshbooks_service.get_authorization_url(state=org_id)

    logger.info(f"Initiating OAuth flow for organization: {org_id}")
    return RedirectResponse(url=auth_url)


@router.get("/callback")
async def oauth_callback(
    code: Optional[str] = Query(None, description="Authorization code from FreshBooks"),
    state: Optional[str] = Query(None, description="State parameter (org_id)"),
    error: Optional[str] = Query(None, description="Error from FreshBooks"),
    error_description: Optional[str] = Query(None, description="Error description")
):
    """
    Handle OAuth callback from FreshBooks.

    This endpoint receives the authorization code and exchanges it for an access token.
    The access token is then stored and associated with the organization.

    Returns:
        Redirect to billing page with success/error message
    """
    # Check for OAuth errors
    if error:
        logger.error(f"OAuth error: {error} - {error_description}")
        # Redirect to billing page with error (URL encode parameters)
        encoded_error = quote(str(error))
        encoded_description = quote(str(error_description or ''))
        return RedirectResponse(
            url=f"https://app.seleen.io/billing?error={encoded_error}&message={encoded_description}",
            status_code=302
        )

    if not code or not state:
        raise HTTPException(
            status_code=400,
            detail="Missing authorization code or state parameter"
        )

    org_id = state

    try:
        # Exchange code for access token
        token_data = await freshbooks_service.exchange_code_for_token(code)

        # Get user identity and account_id
        access_token = token_data["access_token"]
        identity = await freshbooks_service.get_identity(access_token)
        account_id = freshbooks_service.extract_account_id(identity)

        if not account_id:
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve account_id from FreshBooks"
            )

        # Store account_id with token data
        token_data["account_id"] = account_id
        freshbooks_service.store_token(org_id, token_data)

        logger.info(f"Successfully completed OAuth flow for organization: {org_id}")

        # Redirect to billing page with success message
        return RedirectResponse(
            url="https://app.seleen.io/billing?freshbooks_connected=true",
            status_code=302
        )

    except Exception as e:
        logger.error(f"Failed to complete OAuth flow: {e}")
        encoded_message = quote(str(e))
        return RedirectResponse(
            url=f"https://app.seleen.io/billing?error=oauth_failed&message={encoded_message}",
            status_code=302
        )


@router.get("/status")
async def check_freshbooks_status(org_id: str = Query(..., description="Organization ID")):
    """
    Check if FreshBooks is connected for an organization.

    Args:
        org_id: Organization ID

    Returns:
        Connection status and account information
    """
    token_data = freshbooks_service.get_token(org_id)

    if not token_data:
        return {
            "connected": False,
            "account_id": None
        }

    return {
        "connected": True,
        "account_id": token_data.get("account_id"),
        "expires_at": token_data.get("expires_at")
    }


@router.post("/disconnect")
async def disconnect_freshbooks(org_id: str = Query(..., description="Organization ID")):
    """
    Disconnect FreshBooks account for an organization.

    Args:
        org_id: Organization ID

    Returns:
        Success message
    """
    token_data = freshbooks_service.get_token(org_id)

    if not token_data:
        raise HTTPException(
            status_code=404,
            detail="No FreshBooks connection found for this organization"
        )

    # Remove token from storage
    freshbooks_service._tokens.pop(org_id, None)

    logger.info(f"Disconnected FreshBooks for organization: {org_id}")

    return {"success": True, "message": "FreshBooks account disconnected"}


# ============================================================================
# Billing/Invoice Endpoints
# ============================================================================

@billing_router.get("/invoices")
async def get_invoices(
    org_id: str = Query(..., description="Organization ID"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(15, ge=1, le=100, description="Invoices per page")
):
    """
    Get list of invoices from FreshBooks for an organization.

    Args:
        org_id: Organization ID
        page: Page number for pagination
        per_page: Number of invoices per page

    Returns:
        List of invoices with pagination info
    """
    # Ensure valid token
    access_token = await freshbooks_service.ensure_valid_token(org_id)

    if not access_token:
        raise HTTPException(
            status_code=401,
            detail="FreshBooks not connected. Please connect your FreshBooks account first."
        )

    token_data = freshbooks_service.get_token(org_id)
    account_id = token_data.get("account_id")

    if not account_id:
        raise HTTPException(
            status_code=500,
            detail="Account ID not found. Please reconnect your FreshBooks account."
        )

    try:
        # Fetch invoices from FreshBooks
        invoices_response = await freshbooks_service.get_invoices(
            access_token=access_token,
            account_id=account_id,
            page=page,
            per_page=per_page
        )

        # Extract invoice list and pagination info
        invoices_data = invoices_response.get("response", {}).get("result", {})
        invoices = invoices_data.get("invoices", [])
        total = invoices_data.get("total", 0)
        pages = invoices_data.get("pages", 1)

        # Transform invoices to match frontend interface
        transformed_invoices = []
        for invoice in invoices:
            transformed_invoices.append({
                "invoice_id": str(invoice.get("id", "")),
                "invoice_number": invoice.get("invoice_number", ""),
                "date": invoice.get("create_date", ""),
                "amount": float(invoice.get("amount", {}).get("amount", 0)),
                "status": invoice.get("v3_status", "").lower(),
                "period_start": invoice.get("date", ""),
                "period_end": invoice.get("due_date", ""),
                "pdf_url": freshbooks_service.get_invoice_pdf_url(
                    account_id=account_id,
                    invoice_id=str(invoice.get("id", ""))
                )
            })

        return {
            "invoices": transformed_invoices,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": pages
            }
        }

    except Exception as e:
        logger.error(f"Failed to fetch invoices: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch invoices from FreshBooks: {str(e)}"
        )


@billing_router.get("/invoices/{invoice_id}")
async def get_invoice(
    invoice_id: str,
    org_id: str = Query(..., description="Organization ID")
):
    """
    Get a single invoice by ID from FreshBooks.

    Args:
        invoice_id: Invoice ID
        org_id: Organization ID

    Returns:
        Invoice details
    """
    # Ensure valid token
    access_token = await freshbooks_service.ensure_valid_token(org_id)

    if not access_token:
        raise HTTPException(
            status_code=401,
            detail="FreshBooks not connected. Please connect your FreshBooks account first."
        )

    token_data = freshbooks_service.get_token(org_id)
    account_id = token_data.get("account_id")

    if not account_id:
        raise HTTPException(
            status_code=500,
            detail="Account ID not found. Please reconnect your FreshBooks account."
        )

    try:
        # Fetch invoice from FreshBooks
        invoice_response = await freshbooks_service.get_invoice(
            access_token=access_token,
            account_id=account_id,
            invoice_id=invoice_id
        )

        invoice = invoice_response.get("response", {}).get("result", {}).get("invoice", {})

        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")

        # Transform to match frontend interface
        transformed_invoice = {
            "invoice_id": str(invoice.get("id", "")),
            "invoice_number": invoice.get("invoice_number", ""),
            "date": invoice.get("create_date", ""),
            "amount": float(invoice.get("amount", {}).get("amount", 0)),
            "status": invoice.get("v3_status", "").lower(),
            "period_start": invoice.get("date", ""),
            "period_end": invoice.get("due_date", ""),
            "pdf_url": freshbooks_service.get_invoice_pdf_url(
                account_id=account_id,
                invoice_id=invoice_id
            ),
            "line_items": invoice.get("lines", [])
        }

        return transformed_invoice

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch invoice {invoice_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch invoice from FreshBooks: {str(e)}"
        )


@billing_router.get("/invoices/{invoice_id}/pdf")
async def download_invoice_pdf(
    invoice_id: str,
    org_id: str = Query(..., description="Organization ID")
):
    """
    Download invoice PDF directly from FreshBooks and stream it to the customer.

    This endpoint downloads the PDF using the stored access token and serves it
    directly to the customer without requiring them to have FreshBooks access.

    Args:
        invoice_id: Invoice ID
        org_id: Organization ID

    Returns:
        PDF file as streaming response
    """
    # Ensure valid token
    access_token = await freshbooks_service.ensure_valid_token(org_id)

    if not access_token:
        raise HTTPException(
            status_code=401,
            detail="FreshBooks not connected. Please connect your FreshBooks account first."
        )

    token_data = freshbooks_service.get_token(org_id)
    account_id = token_data.get("account_id")

    if not account_id:
        raise HTTPException(
            status_code=500,
            detail="Account ID not found. Please reconnect your FreshBooks account."
        )

    try:
        # Download PDF from FreshBooks
        pdf_content = await freshbooks_service.download_invoice_pdf(
            access_token=access_token,
            account_id=account_id,
            invoice_id=invoice_id
        )

        # Stream PDF to customer
        return StreamingResponse(
            BytesIO(pdf_content),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=invoice-{invoice_id}.pdf"
            }
        )

    except Exception as e:
        logger.error(f"Failed to download invoice PDF {invoice_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to download invoice PDF: {str(e)}"
        )
