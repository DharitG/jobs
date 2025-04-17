import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from pydantic import BaseModel
import logging

from .config import settings # Assuming settings are loaded here

logger = logging.getLogger(__name__)

# Reusable HTTP client
client = httpx.AsyncClient()

# Auth0 config (replace with your actual values in .env or config)
AUTH0_DOMAIN = settings.AUTH0_DOMAIN
API_AUDIENCE = settings.AUTH0_API_AUDIENCE
ALGORITHMS = ["RS256"]

# Simple cache for JWKS to avoid fetching it on every request
jwks_cache = None

class TokenPayload(BaseModel):
    sub: str # Subject (Auth0 User ID)
    # Add other claims you might need, e.g., scope, permissions
    # scope: str | None = None

# Scheme for bearer token authentication
token_auth_scheme = HTTPBearer()

async def get_jwks():
    """Fetches the JSON Web Key Set (JWKS) from Auth0."""
    global jwks_cache
    # Use cache if available
    if jwks_cache:
        return jwks_cache

    jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
    try:
        response = await client.get(jwks_url)
        response.raise_for_status()
        jwks_cache = response.json()
        return jwks_cache
    except httpx.RequestError as e:
        logger.error(f"Error requesting JWKS from {jwks_url}: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not connect to authentication service to get keys.",
        )
    except httpx.HTTPStatusError as e:
        logger.error(f"Error response from JWKS endpoint {jwks_url}: {e.response.status_code} - {e.response.text}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Received error from authentication service when getting keys.",
        )
    except Exception as e:
        logger.error(f"Unexpected error fetching JWKS: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while fetching authentication keys.",
        )


async def verify_token(token: HTTPAuthorizationCredentials = Depends(token_auth_scheme)) -> TokenPayload:
    """
    Verifies the Auth0 JWT token.
    Fetches JWKS, decodes the token, validates claims.
    Returns the token payload on success.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_value = token.credentials

    try:
        jwks = await get_jwks()
        unverified_header = jwt.get_unverified_header(token_value)
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"],
                }
                break
        if not rsa_key:
             logger.error(f"Unable to find appropriate key in JWKS for kid: {unverified_header.get('kid')}")
             raise credentials_exception

        payload = jwt.decode(
            token_value,
            rsa_key,
            algorithms=ALGORITHMS,
            audience=API_AUDIENCE,
            issuer=f"https://{AUTH0_DOMAIN}/",
        )
        # Extract subject (user ID)
        auth0_sub: str | None = payload.get("sub")
        if auth0_sub is None:
            logger.warning("Token payload missing 'sub' claim.")
            raise credentials_exception

        # You could add scope/permission checks here if needed
        # token_scopes = payload.get("scope", "").split()
        # if required_scopes and not all(s in token_scopes for s in required_scopes):
        #     raise HTTPException(...)

        token_data = TokenPayload(sub=auth0_sub) # Add other fields if needed

    except JWTError as e:
        logger.warning(f"JWTError during token validation: {e}")
        raise credentials_exception from e
    except Exception as e:
        # Catch unexpected errors during decoding/validation
        logger.error(f"Unexpected error during token validation: {e}")
        raise credentials_exception from e

    return token_data

# --- FastAPI Dependency ---
async def get_current_user_auth0_sub(token_payload: TokenPayload = Depends(verify_token)) -> str:
    """
    FastAPI dependency that verifies the token and returns the Auth0 subject ID.
    Use this in your path operations to protect endpoints and get the user's ID.
    Example: current_user_sub: str = Depends(get_current_user_auth0_sub)
    """
    # You could potentially fetch the full user object from DB here if needed frequently
    # user = crud.user.get_user_by_auth0_sub(db, auth0_sub=token_payload.sub)
    # if not user:
    #     raise HTTPException(status_code=404, detail="User not found in DB")
    # return user # Return full user model
    return token_payload.sub # Return just the sub for now
