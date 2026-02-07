"""
FreshBooks API integration service for invoice management and OAuth authentication.

This service handles:
- OAuth 2.0 authentication flow
- Access token management
- Account ID retrieval from identity endpoint
- Invoice fetching and PDF URL generation
"""

import os
import httpx
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class FreshBooksService:
    """Service for interacting with FreshBooks API."""

    # FreshBooks API endpoints
    AUTH_BASE_URL = "https://auth.freshbooks.com"
    API_BASE_URL = "https://api.freshbooks.com"

    def __init__(self):
        """Initialize FreshBooks service with credentials from environment."""
        self.client_id = os.getenv("FRESHBOOKS_CLIENT_ID")
        self.client_secret = os.getenv("FRESHBOOKS_CLIENT_SECRET")
        self.redirect_uri = os.getenv(
            "FRESHBOOKS_REDIRECT_URI",
            "https://ilanapm.onrender.com/api/v1/auth/freshbooks/callback"
        )

        # In-memory token storage (in production, use database or Redis)
        self._tokens: Dict[str, Dict[str, Any]] = {}

        if not self.client_id or not self.client_secret:
            logger.warning(
                "FreshBooks credentials not configured. "
                "Set FRESHBOOKS_CLIENT_ID and FRESHBOOKS_CLIENT_SECRET environment variables."
            )

    def is_configured(self) -> bool:
        """Check if FreshBooks service is properly configured."""
        return bool(self.client_id and self.client_secret)

    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """
        Generate OAuth authorization URL for user to authorize the app.

        Args:
            state: Optional state parameter for CSRF protection

        Returns:
            Authorization URL to redirect user to
        """
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
        }

        if state:
            params["state"] = state

        # Build query string
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self.AUTH_BASE_URL}/oauth/authorize?{query}"

    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token.

        Args:
            code: Authorization code from OAuth callback

        Returns:
            Token response containing access_token, refresh_token, expires_in

        Raises:
            httpx.HTTPError: If token exchange fails
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.AUTH_BASE_URL}/oauth/token",
                data={
                    "grant_type": "authorization_code",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "redirect_uri": self.redirect_uri,
                },
            )
            response.raise_for_status()
            token_data = response.json()

            # Calculate token expiry
            token_data["expires_at"] = (
                datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 3600))
            ).isoformat()

            logger.info("Successfully exchanged authorization code for access token")
            return token_data

    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh an expired access token.

        Args:
            refresh_token: Refresh token from previous token response

        Returns:
            New token response with fresh access_token

        Raises:
            httpx.HTTPError: If token refresh fails
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.AUTH_BASE_URL}/oauth/token",
                data={
                    "grant_type": "refresh_token",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "refresh_token": refresh_token,
                },
            )
            response.raise_for_status()
            token_data = response.json()

            # Calculate token expiry
            token_data["expires_at"] = (
                datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 3600))
            ).isoformat()

            logger.info("Successfully refreshed access token")
            return token_data

    def store_token(self, org_id: str, token_data: Dict[str, Any]) -> None:
        """
        Store access token for an organization.

        Args:
            org_id: Organization ID to associate token with
            token_data: Token data from OAuth flow
        """
        self._tokens[org_id] = token_data
        logger.info(f"Stored access token for organization: {org_id}")

    def get_token(self, org_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve stored access token for an organization.

        Args:
            org_id: Organization ID

        Returns:
            Token data if found, None otherwise
        """
        return self._tokens.get(org_id)

    async def get_identity(self, access_token: str) -> Dict[str, Any]:
        """
        Get user identity and account information from FreshBooks.

        This endpoint returns business_memberships which contain the account_id
        needed for making accounting API calls.

        Args:
            access_token: Valid FreshBooks access token

        Returns:
            Identity response with business_memberships containing account_id

        Raises:
            httpx.HTTPError: If API call fails
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.API_BASE_URL}/auth/api/v1/users/me",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            identity = response.json()

            logger.info("Successfully retrieved user identity from FreshBooks")
            return identity

    def extract_account_id(self, identity: Dict[str, Any]) -> Optional[str]:
        """
        Extract account_id from identity response.

        Args:
            identity: Response from /users/me endpoint

        Returns:
            Account ID if found, None otherwise
        """
        business_memberships = identity.get("response", {}).get("business_memberships", [])

        if not business_memberships:
            logger.warning("No business memberships found in identity response")
            return None

        # Get the first business (most users have only one)
        first_business = business_memberships[0].get("business", {})
        account_id = first_business.get("account_id")

        if account_id:
            logger.info(f"Extracted account_id: {account_id}")
        else:
            logger.warning("No account_id found in business membership")

        return account_id

    async def get_invoices(
        self,
        access_token: str,
        account_id: str,
        page: int = 1,
        per_page: int = 15
    ) -> Dict[str, Any]:
        """
        Fetch invoices from FreshBooks accounting API.

        Args:
            access_token: Valid FreshBooks access token
            account_id: Account ID from identity endpoint
            page: Page number for pagination
            per_page: Number of invoices per page

        Returns:
            Invoices response with list of invoices

        Raises:
            httpx.HTTPError: If API call fails
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.API_BASE_URL}/accounting/account/{account_id}/invoices/invoices",
                headers={"Authorization": f"Bearer {access_token}"},
                params={"page": page, "per_page": per_page},
            )
            response.raise_for_status()
            invoices_data = response.json()

            logger.info(f"Successfully fetched invoices for account: {account_id}")
            return invoices_data

    async def get_invoice(
        self,
        access_token: str,
        account_id: str,
        invoice_id: str
    ) -> Dict[str, Any]:
        """
        Fetch a single invoice by ID.

        Args:
            access_token: Valid FreshBooks access token
            account_id: Account ID from identity endpoint
            invoice_id: Invoice ID to fetch

        Returns:
            Invoice data

        Raises:
            httpx.HTTPError: If API call fails
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.API_BASE_URL}/accounting/account/{account_id}/invoices/invoices/{invoice_id}",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            invoice_data = response.json()

            logger.info(f"Successfully fetched invoice: {invoice_id}")
            return invoice_data

    def get_invoice_pdf_url(self, account_id: str, invoice_id: str) -> str:
        """
        Generate URL for downloading invoice PDF.

        Note: FreshBooks doesn't provide a direct API for PDF download.
        The PDF URL follows a standard pattern that can be accessed with proper authentication.

        Args:
            account_id: Account ID
            invoice_id: Invoice ID

        Returns:
            URL to download invoice PDF
        """
        # FreshBooks PDF URLs follow this pattern
        # Users can access this URL in their browser when logged in
        return f"https://my.freshbooks.com/invoice/{account_id}-{invoice_id}.pdf"

    async def ensure_valid_token(self, org_id: str) -> Optional[str]:
        """
        Ensure we have a valid access token for an organization.
        Automatically refreshes if expired.

        Args:
            org_id: Organization ID

        Returns:
            Valid access token if available, None if not authenticated
        """
        token_data = self.get_token(org_id)

        if not token_data:
            logger.warning(f"No token found for organization: {org_id}")
            return None

        # Check if token is expired
        expires_at = datetime.fromisoformat(token_data.get("expires_at", ""))
        if datetime.utcnow() >= expires_at - timedelta(minutes=5):
            # Token expired or about to expire, refresh it
            logger.info(f"Token expired for organization: {org_id}, refreshing...")
            try:
                new_token_data = await self.refresh_access_token(token_data["refresh_token"])
                self.store_token(org_id, new_token_data)
                return new_token_data["access_token"]
            except httpx.HTTPError as e:
                logger.error(f"Failed to refresh token: {e}")
                return None

        return token_data["access_token"]


# Global service instance
freshbooks_service = FreshBooksService()
