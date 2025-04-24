import uuid # For UUID type hint
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from pydantic import BaseModel, EmailStr # Import EmailStr
import logging

from .config import settings # Assuming settings are loaded here

logger = logging.getLogger(__name__)

# Supabase config (ensure SUPABASE_JWT_SECRET is in your settings/.env)
SUPABASE_JWT_SECRET = settings.SUPABASE_JWT_SECRET
# Optionally add SUPABASE_URL to settings if you want to validate issuer
# SUPABASE_ISSUER = f"{settings.SUPABASE_URL}/auth/v1"
ALGORITHMS = ["HS256"] # Supabase uses HS256

class TokenPayload(BaseModel):
    sub: uuid.UUID # Subject (Supabase User ID as UUID)
    email: EmailStr | None = None # Add email, make optional initially
    user_metadata: dict | None = None # Add user_metadata, make optional
    # exp: int | None = None # Example: If expiration check needed separate from jwt.decode
    # aud: str | None = None # Example: If audience check needed separate from jwt.decode

# Scheme for bearer token authentication
token_auth_scheme = HTTPBearer()


async def verify_token(token: HTTPAuthorizationCredentials = Depends(token_auth_scheme)) -> TokenPayload:
    """
    Verifies the Supabase JWT token using the shared secret.
    Decodes the token, validates standard claims if needed.
    Returns the token payload on success.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_value = token.credentials

    if not SUPABASE_JWT_SECRET:
        logger.error("SUPABASE_JWT_SECRET is not configured in settings.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication secret not configured."
        )

    try:
        payload = jwt.decode(
            token_value,
            SUPABASE_JWT_SECRET,
            algorithms=ALGORITHMS,
            # Optionally add audience and issuer validation if needed
            audience="authenticated", # Default Supabase audience (Uncommented)
            # issuer=SUPABASE_ISSUER, # Keep issuer commented unless specifically needed and configured
            options={"verify_exp": True} # Default: verify expiration
        )

        # Extract claims
        user_id_str: str | None = payload.get("sub")
        email_str: str | None = payload.get("email") # Extract email
        user_meta: dict | None = payload.get("user_metadata") # Extract metadata

        # --- Validate Subject (User ID) ---
        if user_id_str is None:
            logger.warning("Token payload missing 'sub' (user ID) claim.")
            raise credentials_exception
        try:
            user_id_uuid = uuid.UUID(user_id_str)
        except ValueError:
             logger.warning(f"Token 'sub' claim is not a valid UUID: {user_id_str}")
             raise credentials_exception

        # --- Validate Email (Optional but recommended for user creation) ---
        # If email is strictly required downstream (like for user creation), enforce it here:
        if email_str is None:
             logger.warning("Token payload missing 'email' claim.")
             # Depending on use case, you might allow tokens without email or raise error:
             # raise credentials_exception # Uncomment if email is mandatory

        # --- Create TokenPayload ---
        # Pydantic will validate EmailStr format if email_str is provided
        token_data = TokenPayload(
            sub=user_id_uuid,
            email=email_str,
            user_metadata=user_meta
        )

    except JWTError as e:
        logger.warning(f"JWTError during Supabase token validation: {e}")
        # Distinguish between expired and other invalid reasons if desired
        if "expired" in str(e).lower():
             raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            ) from e
        raise credentials_exception from e
    except Exception as e:
        # Catch unexpected errors during decoding/validation
        logger.error(f"Unexpected error during Supabase token validation: {e}")
        raise credentials_exception from e

    return token_data

# --- FastAPI Dependency (Renamed) ---
async def get_current_token_payload(token_payload: TokenPayload = Depends(verify_token)) -> TokenPayload:
    """
    FastAPI dependency that verifies the Supabase token and returns the full TokenPayload.
    Use this in your path operations to protect endpoints and get user info.
    Example: payload: TokenPayload = Depends(get_current_token_payload)
    """
    return token_payload
