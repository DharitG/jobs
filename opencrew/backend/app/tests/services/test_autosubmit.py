import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timedelta

# Assume services, models, schemas, etc., are importable
from app.services import autosubmit
from app.models.user import User, SubscriptionTier
from app.models.application import Application, ApplicationStatus
from app.models.job import Job
from app.models.resume import Resume
from app.db.session import SessionLocal # For mocking

# --- Mock Data ---

def create_mock_user(id=1, tier=SubscriptionTier.FREE, **kwargs) -> User:
    """Helper to create a mock User object."""
    defaults = {
        "id": id,
        "email": f"user{id}@test.com",
        "hashed_password": "hashed_password",
        "is_active": True,
        "is_superuser": False,
        "subscription_tier": tier,
        "stripe_customer_id": f"cus_{id}",
        "first_name": "Test",
        "last_name": f"User{id}",
        "phone_number": "111-222-3333",
        "linkedin_url": f"linkedin.com/in/testuser{id}",
        # Add other fields as needed
    }
    defaults.update(kwargs)
    return User(**defaults)

def create_mock_application(id=1, user_id=1, job_id=1, resume_id=1, status=ApplicationStatus.PENDING_TRIGGER, **kwargs) -> Application:
    """Helper to create a mock Application object."""
    defaults = {
        "id": id,
        "user_id": user_id,
        "job_id": job_id,
        "resume_id": resume_id,
        "status": status,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        # Add related objects if needed for tests, but often mocked separately
        "user": create_mock_user(id=user_id),
        "job": Job(id=job_id, url="http://test.com/job", title="Mock Job"),
        "resume": Resume(id=resume_id, owner_id=user_id, content="Mock content", original_filepath=f"resumes/{user_id}/mock_resume.pdf"),
    }
    defaults.update(kwargs)
    # Manually set relationships if not done by constructor/mocking framework
    if 'user' in defaults: defaults['user'].id = user_id
    if 'job' in defaults: defaults['job'].id = job_id
    if 'resume' in defaults: defaults['resume'].id = resume_id; defaults['resume'].owner_id = user_id
    return Application(**defaults)

# Mock DB Session
mock_db_session = MagicMock(spec=SessionLocal)

# --- Tests for check_user_quota ---

def test_check_user_quota_free_tier_no_apps():
    """Test free tier quota with no applications this month."""
    mock_user = create_mock_user(tier=SubscriptionTier.FREE)
    mock_db_session.query.return_value.filter.return_value.scalar.return_value = 0 # No apps found

    quota = autosubmit.check_user_quota(db=mock_db_session, user=mock_user)

    assert quota == 50
    mock_db_session.query.assert_called_once() # Check that query was made

def test_check_user_quota_free_tier_some_apps():
    """Test free tier quota with some applications this month."""
    mock_user = create_mock_user(tier=SubscriptionTier.FREE)
    mock_db_session.query.return_value.filter.return_value.scalar.return_value = 15 # 15 apps found

    quota = autosubmit.check_user_quota(db=mock_db_session, user=mock_user)

    assert quota == 35 # 50 - 15

def test_check_user_quota_free_tier_limit_reached():
    """Test free tier quota when the limit is reached/exceeded."""
    mock_user = create_mock_user(tier=SubscriptionTier.FREE)
    mock_db_session.query.return_value.filter.return_value.scalar.return_value = 50 # 50 apps found
    quota = autosubmit.check_user_quota(db=mock_db_session, user=mock_user)
    assert quota == 0

    mock_db_session.query.return_value.filter.return_value.scalar.return_value = 60 # 60 apps found
    quota = autosubmit.check_user_quota(db=mock_db_session, user=mock_user)
    assert quota == 0 # Should not go below 0

def test_check_user_quota_pro_tier():
    """Test pro tier quota (should be effectively unlimited)."""
    mock_user = create_mock_user(tier=SubscriptionTier.PRO)
    # DB query should NOT be called for pro/elite
    mock_db_session.query.reset_mock()

    quota = autosubmit.check_user_quota(db=mock_db_session, user=mock_user)

    assert quota > 1000 # Check it's the large number indicating unlimited
    mock_db_session.query.assert_not_called()

def test_check_user_quota_elite_tier():
    """Test elite tier quota (should be effectively unlimited)."""
    mock_user = create_mock_user(tier=SubscriptionTier.ELITE)
    mock_db_session.query.reset_mock()

    quota = autosubmit.check_user_quota(db=mock_db_session, user=mock_user)

    assert quota > 1000
    mock_db_session.query.assert_not_called()

# --- Tests for apply_to_job_async ---

@pytest.mark.asyncio
@patch('app.services.autosubmit.check_user_quota')
@patch('app.services.autosubmit.boto3.client')
@patch('app.services.autosubmit.tempfile.NamedTemporaryFile')
@patch('app.services.autosubmit.StructuredResumePdfGenerator')
@patch('app.services.autosubmit.Agent')
@patch('app.services.autosubmit.ChatOpenAI')
async def test_apply_to_job_quota_exceeded(
    mock_chat_openai, mock_agent_class, mock_pdf_gen_class, mock_tempfile, mock_s3_client, mock_check_quota):
    """Test apply_to_job_async when user quota is exceeded."""
    mock_db = MagicMock(spec=SessionLocal)
    mock_application = create_mock_application(id=99, status=ApplicationStatus.PENDING_TRIGGER)
    mock_db.query.return_value.filter.return_value.first.return_value = mock_application
    
    # Simulate quota check returning 0
    mock_check_quota.return_value = 0

    await autosubmit.apply_to_job_async(db=mock_db, application_id=99)

    # Assertions
    mock_check_quota.assert_called_once_with(db=mock_db, user=mock_application.user)
    # Ensure application status is updated to ERROR
    assert mock_application.status == ApplicationStatus.ERROR
    assert "quota exceeded" in mock_application.notes.lower()
    # Ensure no S3/Agent operations were attempted
    mock_s3_client.assert_not_called()
    mock_agent_class.assert_not_called()
    mock_db.commit.assert_called_once() # Should commit the status update

@pytest.mark.asyncio
async def test_apply_to_job_application_not_found():
    """Test apply_to_job_async when application ID does not exist."""
    mock_db = MagicMock(spec=SessionLocal)
    mock_db.query.return_value.filter.return_value.first.return_value = None # Simulate not found

    # Use patch context managers if mocks are only needed here
    with patch('app.services.autosubmit.check_user_quota') as mock_check_quota, \
         patch('app.services.autosubmit.Agent') as mock_agent_class:
        
        await autosubmit.apply_to_job_async(db=mock_db, application_id=101)

        # Assertions
        mock_db.query.assert_called_once()
        mock_check_quota.assert_not_called() # Should exit before quota check
        mock_agent_class.assert_not_called()
        mock_db.commit.assert_not_called() # Should not commit if app not found

# TODO: Add more tests for apply_to_job_async:
# - Success case (mocking agent success, S3 upload, PDF generation etc.)
# - Missing resume S3 key scenario.
# - PDF generation failure scenario (should fall back to original).
# - Agent execution failure scenario.
# - Agent history parsing failure scenario.
# - S3 download/upload failure scenarios.
# - File cleanup verification.