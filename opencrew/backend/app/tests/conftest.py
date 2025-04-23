# opencrew/backend/app/tests/conftest.py
import sys
import os

# Add the project root (opencrew/backend) to the Python path
# This allows imports like `from app.main import app` to work correctly
# when pytest runs from the backend directory.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


# opencrew/backend/app/tests/conftest.py

import os
import pytest
from typing import Generator, Any

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool # Use StaticPool for SQLite in-memory

# Set environment variable for test database *before* importing settings/app
# NOTE: Using SQLite in-memory for simplicity. For full compatibility (e.g., JSONB),
# configure a separate PostgreSQL test database and update TEST_DATABASE_URL.
# Example: TEST_DATABASE_URL = "postgresql://test_user:test_password@localhost:5433/test_db"
TEST_DATABASE_URL = "sqlite:///:memory:"
os.environ['DATABASE_URL'] = TEST_DATABASE_URL
# Ensure other critical env vars are set if needed for app startup, or mock them.
# os.environ['SUPABASE_JWT_SECRET'] = 'test-secret' # Example if needed


# Now import app components that rely on settings
from app.main import app # Import your FastAPI app instance
from app.db.session import get_db # Import your dependency
from app.db.base import Base # Import your SQLAlchemy Base

# Create the SQLAlchemy engine for testing
# Use StaticPool for SQLite in-memory DB to ensure same connection is reused
# connect_args required for SQLite
engine = create_engine(
    TEST_DATABASE_URL,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False} # Required for SQLite
)

# Create a sessionmaker for testing
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def create_test_database():
    """
    Fixture to create and drop the test database schema once per session.
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db() -> Generator[Session, Any, None]:
    """
    Fixture to provide a transactional database session per test function.
    Rolls back changes after each test.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session # Provide the session to the test

    # Clean up: rollback transaction and close connection
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, Any, None]:
    """
    Fixture to provide a FastAPI TestClient with overridden DB dependency.
    """
    def override_get_db():
        try:
            yield db
        finally:
            # The 'db' fixture handles session closing/rollback
            pass

    # Override the dependency
    app.dependency_overrides[get_db] = override_get_db

    # Yield the TestClient
    with TestClient(app) as test_client:
        yield test_client

    # Clean up the override
    del app.dependency_overrides[get_db]