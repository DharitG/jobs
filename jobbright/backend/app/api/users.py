from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from pydantic import ValidationError

from ... import crud, models, schemas
from ...core.config import settings
from ...core import security # Although not directly used here, often needed for permissions
from ...db.session import get_db
from .auth import oauth2_scheme # Re-use the scheme from auth
from ...core.security import decode_access_token # Need to decode token to get user

router = APIRouter()

# --- Dependency to get current user --- 

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    """Dependency to get the current user from the token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except Exception: # Catch broad exceptions from decode (JWTError, ExpiredSignatureError)
        raise credentials_exception
    
    user = crud.user.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    # Optional: Check if user is active
    # if not user.is_active:
    #     raise HTTPException(status_code=400, detail="Inactive user")
    return user

# --- User Endpoints --- 

@router.get("/me", response_model=schemas.User)
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    """Fetch the profile of the currently logged-in user."""
    return current_user

@router.put("/me", response_model=schemas.User)
async def update_user_me(
    *, 
    db: Session = Depends(get_db), 
    user_in: schemas.UserUpdate, 
    current_user: models.User = Depends(get_current_user)
):
    """Update the profile of the currently logged-in user."""
    user = crud.user.update_user(db=db, db_user=current_user, user_in=user_in)
    return user

# Add other user endpoints here later (e.g., get specific user by ID for admins)
# @router.put("/me", response_model=schemas.User)
# async def update_user_me(...):
#    ... 