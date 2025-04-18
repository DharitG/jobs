from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ... import crud, models, schemas
from ...db.session import get_db
from ...core.security import get_current_user_auth0_sub # Import the new Auth0 dependency

router = APIRouter()

# --- Dependency to get current user model from Auth0 sub ---

async def get_current_active_user(
    current_user_sub: str = Depends(get_current_user_auth0_sub),
    db: Session = Depends(get_db)
) -> models.User:
    """
    Dependency that verifies Auth0 token, gets the sub,
    and fetches the corresponding user from the database.
    Raises 404 if user not found in DB for a valid token sub.
    Raises 400 if user is inactive.
    """
    user = crud.user.get_user_by_auth0_sub(db, auth0_sub=current_user_sub)
    if not user:
        # This case might indicate an issue, e.g., user deleted from DB but token still valid
        # Or potentially a user created in Auth0 but not yet synced/created in our DB.
        # Depending on the flow, you might want to auto-create the user here.
        # For now, treat it as an error.
        raise HTTPException(status_code=404, detail="User not found in database.")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


# --- User Endpoints ---

@router.get("/me", response_model=schemas.User)
async def read_users_me(
    current_user: models.User = Depends(get_current_active_user)
):
    """Fetch the profile of the currently logged-in user."""
    return current_user

@router.put("/me", response_model=schemas.User)
async def update_user_me(
    *,
    db: Session = Depends(get_db),
    user_in: schemas.UserUpdate,
    current_user: models.User = Depends(get_current_active_user)
):
    """Update the profile of the currently logged-in user."""
    # The dependency already fetched the current_user model
    user = crud.user.update_user(db=db, db_user=current_user, user_in=user_in)
    return user

# Add other user endpoints here later (e.g., get specific user by ID for admins)
