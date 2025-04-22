import uuid # For UUID type hint
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from pydantic import BaseModel
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
    # Add other standard JWT claims if needed for validation (e.g., iss, aud, exp)
    # exp: int | None = None
    # iss: str | None = None
    # aud: str | None = None # Often 'authenticated' for Supabase

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
            # audience="authenticated", # Default Supabase audience
            # issuer=SUPABASE_ISSUER,
            options={"verify_exp": True} # Default: verify expiration
        )

        # Extract subject (user ID) and validate its type
        user_id_str: str | None = payload.get("sub")
        if user_id_str is None:
            logger.warning("Token payload missing 'sub' (user ID) claim.")
            raise credentials_exception

        try:
            user_id_uuid = uuid.UUID(user_id_str)
        except ValueError:
             logger.warning(f"Token 'sub' claim is not a valid UUID: {user_id_str}")
             raise credentials_exception

        # You could add role/permission checks here based on payload['user_role'] or custom claims if set up in Supabase

        token_data = TokenPayload(sub=user_id_uuid)

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

# --- FastAPI Dependency ---
async def get_current_supabase_user_id(token_payload: TokenPayload = Depends(verify_token)) -> uuid.UUID:
    """
    FastAPI dependency that verifies the Supabase token and returns the user ID (UUID).
    Use this in your path operations to protect endpoints and get the user's ID.
    Example: current_user_id: uuid.UUID = Depends(get_current_supabase_user_id)
    """
    # You could fetch the full user object from DB here using the ID if needed
    # user = crud.user.get_user_by_supabase_id(db, supabase_id=token_payload.sub) ...
    return token_payload.sub
