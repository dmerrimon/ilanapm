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
import json

from database.connection import get_db_connection

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
        Store access token for an organization in database.

        Args:
            org_id: Organization ID to associate token with
            token_data: Token data from OAuth flow
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()

                # Insert or update token
                cursor.execute("""
                    INSERT INTO freshbooks_tokens
                    (org_id, access_token, refresh_token, account_id, expires_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(org_id) DO UPDATE SET
                        access_token = excluded.access_token,
                        refresh_token = excluded.refresh_token,
                        account_id = excluded.account_id,
                        expires_at = excluded.expires_at,
                        updated_at = CURRENT_TIMESTAMP
                """, (
                    org_id,
                    token_data.get("access_token"),
                    token_data.get("refresh_token"),
                    token_data.get("account_id"),
                    token_data.get("expires_at")
                ))

                logger.info(f"Stored access token in database for organization: {org_id}")
        except Exception as e:
            logger.error(f"Failed to store token in database: {e}")
            raise

    def get_token(self, org_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve stored access token for an organization from database.

        Args:
            org_id: Organization ID

        Returns:
            Token data if found, None otherwise
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT access_token, refresh_token, account_id, expires_at
                    FROM freshbooks_tokens
                    WHERE org_id = ?
                """, (org_id,))

                row = cursor.fetchone()

                if row:
                    # Handle both dict (PostgreSQL) and tuple (SQLite) row types
                    if isinstance(row, dict):
                        return {
                            "access_token": row["access_token"],
                            "refresh_token": row["refresh_token"],
                            "account_id": row["account_id"],
                            "expires_at": row["expires_at"]
                        }
                    else:
                        return {
                            "access_token": row[0],
                            "refresh_token": row[1],
                            "account_id": row[2],
                            "expires_at": row[3]
                        }

                return None
        except Exception as e:
            logger.error(f"Failed to retrieve token from database: {e}")
            return None

    def delete_token(self, org_id: str) -> None:
        """
        Delete stored access token for an organization from database.

        Args:
            org_id: Organization ID
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM freshbooks_tokens
                    WHERE org_id = ?
                """, (org_id,))

                logger.info(f"Deleted access token from database for organization: {org_id}")
        except Exception as e:
            logger.error(f"Failed to delete token from database: {e}")
            raise

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

    async def download_invoice_pdf(
        self,
        access_token: str,
        account_id: str,
        invoice_id: str
    ) -> bytes:
        """
        Download invoice PDF from FreshBooks.

        FreshBooks doesn't have a direct PDF download endpoint, so we need to:
        1. Get the invoice data
        2. Use the browser-accessible PDF URL with authentication

        Args:
            access_token: Valid FreshBooks access token
            account_id: Account ID from identity endpoint
            invoice_id: Invoice ID

        Returns:
            PDF file content as bytes

        Raises:
            httpx.HTTPError: If download fails
        """
        # FreshBooks PDF download URL (requires authentication)
        pdf_url = f"https://my.freshbooks.com/invoice/{account_id}-{invoice_id}.pdf"

        async with httpx.AsyncClient(follow_redirects=True) as client:
            # Try to download PDF with bearer token
            response = await client.get(
                pdf_url,
                headers={"Authorization": f"Bearer {access_token}"},
            )

            # If that doesn't work, FreshBooks might use cookies for PDF access
            # In that case, we need to use their API endpoint
            if response.status_code != 200:
                # Alternative: Try using the accounting API to get PDF
                logger.warning(f"Direct PDF download failed with status {response.status_code}, trying API endpoint")

                # FreshBooks may have a PDF generation endpoint
                api_pdf_url = f"{self.API_BASE_URL}/accounting/account/{account_id}/invoices/invoices/{invoice_id}.pdf"
                response = await client.get(
                    api_pdf_url,
                    headers={"Authorization": f"Bearer {access_token}"},
                )

            response.raise_for_status()

            logger.info(f"Successfully downloaded PDF for invoice: {invoice_id}")
            return response.content

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
                # Preserve account_id from old token
                new_token_data["account_id"] = token_data.get("account_id")
                self.store_token(org_id, new_token_data)
                return new_token_data["access_token"]
            except httpx.HTTPError as e:
                logger.error(f"Failed to refresh token: {e}")
                return None

        return token_data["access_token"]

    async def get_customers(
        self,
        access_token: str,
        account_id: str
    ) -> Dict[str, Any]:
        """
        Fetch customers/clients from FreshBooks.

        Args:
            access_token: Valid FreshBooks access token
            account_id: Account ID from identity endpoint

        Returns:
            Customers response with list of clients

        Raises:
            httpx.HTTPError: If API call fails
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.API_BASE_URL}/accounting/account/{account_id}/users/clients",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            customers_data = response.json()

            logger.info(f"Successfully fetched customers for account: {account_id}")
            return customers_data

    def get_customer_mapping(self, org_id: str) -> Optional[Dict[str, Any]]:
        """
        Get FreshBooks customer mapping for an organization.

        Args:
            org_id: Portal organization ID

        Returns:
            Mapping data if found, None otherwise
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT org_id, freshbooks_customer_id, freshbooks_customer_name, created_at, updated_at
                    FROM freshbooks_customer_mapping
                    WHERE org_id = ?
                """, (org_id,))

                row = cursor.fetchone()

                if row:
                    # Handle both dict (PostgreSQL) and tuple (SQLite) row types
                    if isinstance(row, dict):
                        return {
                            "org_id": row["org_id"],
                            "freshbooks_customer_id": row["freshbooks_customer_id"],
                            "freshbooks_customer_name": row["freshbooks_customer_name"],
                            "created_at": row["created_at"],
                            "updated_at": row["updated_at"]
                        }
                    else:
                        return {
                            "org_id": row[0],
                            "freshbooks_customer_id": row[1],
                            "freshbooks_customer_name": row[2],
                            "created_at": row[3],
                            "updated_at": row[4]
                        }

                return None
        except Exception as e:
            logger.error(f"Failed to retrieve customer mapping: {e}")
            return None

    def get_all_customer_mappings(self) -> List[Dict[str, Any]]:
        """
        Get all FreshBooks customer mappings.

        Returns:
            List of all mappings
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT org_id, freshbooks_customer_id, freshbooks_customer_name, created_at, updated_at
                    FROM freshbooks_customer_mapping
                    ORDER BY created_at DESC
                """)

                rows = cursor.fetchall()
                mappings = []

                for row in rows:
                    # Handle both dict (PostgreSQL) and tuple (SQLite) row types
                    if isinstance(row, dict):
                        mappings.append({
                            "org_id": row["org_id"],
                            "freshbooks_customer_id": row["freshbooks_customer_id"],
                            "freshbooks_customer_name": row["freshbooks_customer_name"],
                            "created_at": row["created_at"],
                            "updated_at": row["updated_at"]
                        })
                    else:
                        mappings.append({
                            "org_id": row[0],
                            "freshbooks_customer_id": row[1],
                            "freshbooks_customer_name": row[2],
                            "created_at": row[3],
                            "updated_at": row[4]
                        })

                return mappings
        except Exception as e:
            logger.error(f"Failed to retrieve customer mappings: {e}")
            return []

    def set_customer_mapping(
        self,
        org_id: str,
        freshbooks_customer_id: str,
        freshbooks_customer_name: Optional[str] = None
    ) -> None:
        """
        Set or update FreshBooks customer mapping for an organization.

        Args:
            org_id: Portal organization ID
            freshbooks_customer_id: FreshBooks customer/client ID
            freshbooks_customer_name: Customer name for reference (optional)
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT INTO freshbooks_customer_mapping
                    (org_id, freshbooks_customer_id, freshbooks_customer_name, updated_at)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(org_id) DO UPDATE SET
                        freshbooks_customer_id = excluded.freshbooks_customer_id,
                        freshbooks_customer_name = excluded.freshbooks_customer_name,
                        updated_at = CURRENT_TIMESTAMP
                """, (org_id, freshbooks_customer_id, freshbooks_customer_name))

                logger.info(f"Set customer mapping: {org_id} → {freshbooks_customer_id}")
        except Exception as e:
            logger.error(f"Failed to set customer mapping: {e}")
            raise

    def delete_customer_mapping(self, org_id: str) -> None:
        """
        Delete FreshBooks customer mapping for an organization.

        Args:
            org_id: Portal organization ID
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM freshbooks_customer_mapping
                    WHERE org_id = ?
                """, (org_id,))

                logger.info(f"Deleted customer mapping for: {org_id}")
        except Exception as e:
            logger.error(f"Failed to delete customer mapping: {e}")
            raise


# Global service instance
freshbooks_service = FreshBooksService()
