import uuid # Import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas # Import crud and schemas
from app.models.user import User # Import User model specifically
from app.db.session import get_db # Absolute import
# Import the new Supabase dependency function
from app.core.security import get_current_supabase_user_id # Absolute import

router = APIRouter()

# --- Dependency to get current user model from Supabase ID ---

async def get_current_active_user(
    # Use the new dependency to get the Supabase user ID (UUID)
    current_user_id: uuid.UUID = Depends(get_current_supabase_user_id),
    db: Session = Depends(get_db)
) -> User: # Use the directly imported User type
    """
    Dependency that verifies Supabase token, gets the user ID (UUID),
    and fetches the corresponding user from the database.
    Raises 404 if user not found in DB for a valid token sub.
    Raises 400 if user is inactive.
    """
    # Use the updated CRUD function
    user = crud.user.get_user_by_supabase_id(db, supabase_id=current_user_id)
    if not user:
        # This case might indicate an issue, e.g., user deleted from DB but token still valid
        # Or potentially a user created in Supabase but not yet synced/created in our DB.
        # Depending on the flow, you might want to auto-create the user here.
        # For now, treat it as an error.
        raise HTTPException(status_code=404, detail="User not found in database.")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


# --- User Endpoints ---

@router.get("/me", response_model=schemas.User)
async def read_users_me(
    # This dependency now provides the user model fetched via Supabase ID
    current_user: User = Depends(get_current_active_user) # Use the directly imported User type
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
