import os
import logging
from datetime import datetime
from typing import Optional
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

logger = logging.getLogger(__name__)

AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID")
AZURE_CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
JWKS_URL = f"https://login.microsoftonline.com/{AZURE_TENANT_ID}/discovery/v2.0/keys"

security = HTTPBearer()


class AuthService:
    """Service for handling Azure AD JWT authentication."""

    def __init__(self):
        self.issuer = f"https://login.microsoftonline.com/{AZURE_TENANT_ID}/v2.0"
        self.audience = AZURE_CLIENT_ID

    async def validate_token(self, credentials: HTTPAuthorizationCredentials) -> dict:
        """Validate the JWT token from the Authorization header."""
        token = credentials.credentials
        try:
            payload = jwt.decode(
                token,
                key=self._get_signing_key(token),
                algorithms=["RS256"],
                audience=self.audience,
                issuer=self.issuer
            )
            
            if datetime.utcfromtimestamp(payload["exp"]) < datetime.utcnow():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired"
                )
            
            return payload
            
        except JWTError as e:
            logger.warning(f"JWT validation failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )

    def _get_signing_key(self, token: str) -> str:
        """Retrieve the signing key from Azure AD JWKS endpoint."""
        # Simplified for POC - in production, fetch from JWKS_URL
        return os.getenv("JWT_SIGNING_KEY", "default-dev-key")

    def get_user_id(self, payload: dict) -> Optional[str]:
        """Extract user ID from the token payload."""
        return payload.get("oid") or payload.get("sub")