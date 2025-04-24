import uuid # Import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud # Import crud
from app.schemas.user import User as UserSchema, UserUpdate, UserCreate # Import UserCreate as well
from app.models.user import User as UserModel # Import User model specifically and alias it
from app.db.session import get_db # Absolute import
# Import the renamed Supabase dependency function and TokenPayload
from app.core.security import get_current_token_payload, TokenPayload # Absolute import

router = APIRouter()

# --- Dependency to get current user model, creating if not found ---

async def get_current_active_user(
    # Use the renamed dependency to get the full token payload
    token_payload: TokenPayload = Depends(get_current_token_payload),
    db: Session = Depends(get_db)
) -> UserModel: # Use the aliased UserModel type
    """
    Dependency that verifies Supabase token, gets the user payload,
    fetches the corresponding user from the database, OR creates the user
    if they don't exist locally but have a valid token.
    Raises 401/403 if token invalid/expired (handled by get_current_token_payload).
    Raises 400 if email is missing from token when creating user.
    Raises 400 if user is inactive.
    """
    # 1. Try to find the user by Supabase ID from the token payload
    user = crud.user.get_user_by_supabase_id(db, supabase_id=token_payload.sub)

    # 2. If user not found, create them
    if not user:
        print(f"User with Supabase ID {token_payload.sub} not found locally. Attempting to create.") # Add print for debugging
        # Ensure email exists in the token (needed for UserCreate)
        if not token_payload.email:
             # This shouldn't happen if security.py enforces email, but check just in case
             raise HTTPException(
                 status_code=status.HTTP_400_BAD_REQUEST,
                 detail="Cannot create user, email missing from token payload."
             )

        # Extract full name from metadata if available
        full_name = token_payload.user_metadata.get("full_name") if token_payload.user_metadata else None

        # Create the user schema
        user_create_data = UserCreate(
            supabase_user_id=token_payload.sub,
            email=token_payload.email,
            full_name=full_name
            # Add any other default fields required by UserCreate or your model
        )

        # Create user in the database
        try:
             user = crud.user.create_user(db=db, user=user_create_data)
             print(f"Successfully created local user for Supabase ID {token_payload.sub}") # Add print for debugging
        except Exception as e:
            # Handle potential database errors during creation
            print(f"Error creating local user for Supabase ID {token_payload.sub}: {e}") # Add print for debugging
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create local user record.",
            )

    # 3. Check if the user (found or created) is active
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")

    return user


# --- User Endpoints ---

@router.get("/me", response_model=UserSchema) # Use the aliased UserSchema
async def read_users_me(
    # This dependency now provides the user model fetched via Supabase ID
    current_user: UserModel = Depends(get_current_active_user) # Use the aliased UserModel type
):
    """Fetch the profile of the currently logged-in user."""
    return current_user

@router.put("/me", response_model=UserSchema) # Use the imported alias
async def update_user_me(
    *,
    db: Session = Depends(get_db),
    user_in: UserUpdate, # Use the imported UserUpdate schema
    current_user: UserModel = Depends(get_current_active_user) # Use the aliased UserModel type
):
    """Update the profile of the currently logged-in user."""
    # The dependency already fetched the current_user model
    user = crud.user.update_user(db=db, db_user=current_user, user_in=user_in)
    return user

# Add other user endpoints here later (e.g., get specific user by ID for admins)
