from sqlalchemy.orm import Session
from datetime import datetime, timedelta, date

from .. import models, schemas
# from ..core.security import get_password_hash, verify_password # Removed for Auth0

def get_user(db: Session, user_id: int) -> models.User | None:
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> models.User | None:
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_auth0_sub(db: Session, auth0_sub: str) -> models.User | None:
    """Gets a user by their Auth0 subject ID."""
    return db.query(models.User).filter(models.User.auth0_sub == auth0_sub).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Creates a user based on Auth0 info (no password)."""
    # hashed_password = get_password_hash(user.password) # Removed for Auth0
    db_user = models.User(
        email=user.email,
        auth0_sub=user.auth0_sub,
        full_name=user.full_name
        # Initialize streak fields? Default is 0 and None in model.
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, db_user: models.User, user_in: schemas.UserUpdate) -> models.User:
    """Updates user profile information (e.g., full_name)."""
    user_data = user_in.model_dump(exclude_unset=True)
    # Password update logic removed for Auth0

    for field, value in user_data.items():
        setattr(db_user, field, value)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_streak(db: Session, db_user: models.User) -> models.User:
    """
    Updates the user's daily streak based on the current time and last update.
    This should be called when a user performs an action that counts towards the streak (e.g., logs in, completes a task).
    """
    now = datetime.utcnow()
    today = now.date()

    if db_user.last_streak_update:
        last_update_date = db_user.last_streak_update.date()
        yesterday = today - timedelta(days=1)

        if last_update_date == today:
            # Already updated today, do nothing
            pass
        elif last_update_date == yesterday:
            # Continued streak
            db_user.current_streak += 1
            db_user.last_streak_update = now
        else:
            # Streak broken
            db_user.current_streak = 1 # Start new streak
            db_user.last_streak_update = now
    else:
        # First time activity contributing to streak
        db_user.current_streak = 1
        db_user.last_streak_update = now

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# Optional: Delete functions can be added here later
# def delete_user(...):

# Authentication helper removed as Auth0 handles authentication
# def authenticate_user(...):
