import pytest
from unittest.mock import patch, MagicMock

# Assume tasks and dependencies are importable
from app.workers import tasks
from app.models.job import Job
from app.models.resume import Resume
from app.models.user import User, SubscriptionTier
from app.schemas.application import ApplicationCreate # Import the schema used
from app.db.session import SessionLocal # For mocking Session type

# --- Mock Data ---

MOCK_USER_ID = 1
MOCK_RESUME_ID = 10
MOCK_JOB_ID_1 = 101
MOCK_JOB_ID_2 = 102

mock_resume_with_embedding = Resume(
    id=MOCK_RESUME_ID,
    owner_id=MOCK_USER_ID,
    content="resume text",
    embedding=[0.1] * 384, # Example embedding size
    original_filepath="path/to/resume.pdf"
)

mock_job_1 = Job(id=MOCK_JOB_ID_1, title="Job 1", company_name="Comp A")
mock_job_2 = Job(id=MOCK_JOB_ID_2, title="Job 2", company_name="Comp B")

mock_matched_jobs = [mock_job_1, mock_job_2]

# --- Test Cases ---

@patch('app.workers.tasks.SessionLocal')
@patch('app.workers.tasks.crud.resume.get_resume')
@patch('app.workers.tasks.matching.search_similar_jobs')
@patch('app.workers.tasks.crud.application.get_application_by_details')
@patch('app.workers.tasks.autosubmit.check_user_quota')
@patch('app.workers.tasks.crud.application.create_application')
@patch('app.workers.tasks.trigger_auto_apply.delay')
def test_process_user_job_matches_quota_exceeded(
    mock_trigger_delay, mock_create_app, mock_check_quota, mock_get_app_details,
    mock_search_jobs, mock_get_resume, mock_session_local):
    """
    Test process_user_job_matches when user quota is exceeded for all matched jobs.
    """
    # Setup Mocks
    mock_db_instance = MagicMock(spec=SessionLocal)
    mock_session_local.return_value = mock_db_instance
    mock_get_resume.return_value = mock_resume_with_embedding
    mock_search_jobs.return_value = mock_matched_jobs
    mock_get_app_details.return_value = None # Assume no existing applications
    mock_check_quota.return_value = (False, "Quota Exceeded") # Simulate quota check failing

    # Execute Task
    tasks.process_user_job_matches(user_id=MOCK_USER_ID, resume_id=MOCK_RESUME_ID)

    # Assertions
    mock_get_resume.assert_called_once_with(mock_db_instance, resume_id=MOCK_RESUME_ID, owner_id=MOCK_USER_ID)
    mock_search_jobs.assert_called_once_with(db=mock_db_instance, resume_embedding=mock_resume_with_embedding.embedding, user_id=MOCK_USER_ID)
    assert mock_get_app_details.call_count == len(mock_matched_jobs) # Check existing app for each match
    assert mock_check_quota.call_count == len(mock_matched_jobs) # Check quota for each match
    mock_create_app.assert_not_called() # No applications should be created
    mock_trigger_delay.assert_not_called() # No triggers should be sent
    mock_db_instance.commit.assert_not_called() # No successful commit expected
    mock_db_instance.close.assert_called_once() # Session should always be closed


@patch('app.workers.tasks.SessionLocal')
@patch('app.workers.tasks.crud.resume.get_resume')
@patch('app.workers.tasks.matching.search_similar_jobs')
@patch('app.workers.tasks.crud.application.get_application_by_details')
@patch('app.workers.tasks.autosubmit.check_user_quota')
@patch('app.workers.tasks.crud.application.create_application')
@patch('app.workers.tasks.trigger_auto_apply.delay')
def test_process_user_job_matches_happy_path(
    mock_trigger_delay, mock_create_app, mock_check_quota, mock_get_app_details,
    mock_search_jobs, mock_get_resume, mock_session_local):
    """
    Test process_user_job_matches happy path where quota is available and apps are created/triggered.
    """
    # Setup Mocks
    mock_db_instance = MagicMock(spec=SessionLocal)
    mock_session_local.return_value = mock_db_instance
    mock_get_resume.return_value = mock_resume_with_embedding
    mock_search_jobs.return_value = mock_matched_jobs
    mock_get_app_details.return_value = None # Assume no existing applications
    mock_check_quota.return_value = (True, "Quota Available") # Simulate quota check passing

    # Mock the return value of create_application
    mock_new_app_1 = MagicMock(id=1001)
    mock_new_app_2 = MagicMock(id=1002)
    mock_create_app.side_effect = [mock_new_app_1, mock_new_app_2]

    # Execute Task
    tasks.process_user_job_matches(user_id=MOCK_USER_ID, resume_id=MOCK_RESUME_ID)

    # Assertions
    mock_get_resume.assert_called_once()
    mock_search_jobs.assert_called_once()
    assert mock_get_app_details.call_count == len(mock_matched_jobs)
    assert mock_check_quota.call_count == len(mock_matched_jobs)
    assert mock_create_app.call_count == len(mock_matched_jobs) # App created for each match
    # Check arguments passed to create_application for the first call
    create_call_args_list = mock_create_app.call_args_list
    assert create_call_args_list[0][1]['user_id'] == MOCK_USER_ID
    assert isinstance(create_call_args_list[0][1]['application'], ApplicationCreate)
    assert create_call_args_list[0][1]['application'].resume_id == MOCK_RESUME_ID
    assert create_call_args_list[0][1]['application'].job_id == MOCK_JOB_ID_1

    assert mock_trigger_delay.call_count == len(mock_matched_jobs) # Trigger sent for each new app
    # Check arguments passed to trigger_auto_apply.delay for the first call
    trigger_call_args_list = mock_trigger_delay.call_args_list
    assert trigger_call_args_list[0][1]['application_id'] == mock_new_app_1.id
    assert trigger_call_args_list[1][1]['application_id'] == mock_new_app_2.id

    mock_db_instance.close.assert_called_once()


@patch('app.workers.tasks.SessionLocal')
@patch('app.workers.tasks.crud.resume.get_resume')
@patch('app.workers.tasks.matching.search_similar_jobs')
@patch('app.workers.tasks.crud.application.get_application_by_details')
@patch('app.workers.tasks.autosubmit.check_user_quota')
@patch('app.workers.tasks.crud.application.create_application')
@patch('app.workers.tasks.trigger_auto_apply.delay')
def test_process_user_job_matches_some_existing_apps(
    mock_trigger_delay, mock_create_app, mock_check_quota, mock_get_app_details,
    mock_search_jobs, mock_get_resume, mock_session_local):
    """
    Test process_user_job_matches when some applications already exist.
    """
     # Setup Mocks
    mock_db_instance = MagicMock(spec=SessionLocal)
    mock_session_local.return_value = mock_db_instance
    mock_get_resume.return_value = mock_resume_with_embedding
    mock_search_jobs.return_value = mock_matched_jobs
    # Simulate first app exists, second doesn't
    mock_get_app_details.side_effect = [MagicMock(), None]
    mock_check_quota.return_value = (True, "Quota Available") # Quota available for the second app

    mock_new_app_2 = MagicMock(id=1002)
    mock_create_app.return_value = mock_new_app_2 # Only called once for the second job

    # Execute Task
    tasks.process_user_job_matches(user_id=MOCK_USER_ID, resume_id=MOCK_RESUME_ID)

    # Assertions
    assert mock_get_app_details.call_count == len(mock_matched_jobs)
    assert mock_check_quota.call_count == 1 # Only called for the second job
    assert mock_create_app.call_count == 1 # Only called for the second job
    # Check args for the single call
    create_call_args_list = mock_create_app.call_args_list
    assert create_call_args_list[0][1]['application'].job_id == MOCK_JOB_ID_2

    assert mock_trigger_delay.call_count == 1 # Only called for the second job
    trigger_call_args_list = mock_trigger_delay.call_args_list
    assert trigger_call_args_list[0][1]['application_id'] == mock_new_app_2.id

    mock_db_instance.close.assert_called_once()


# TODO: Add tests for:
# - Resume not found
# - Resume has no embedding
# - matching.search_similar_jobs returns empty list
# - crud.application.create_application raises an exception
# - trigger_auto_apply.delay raises an exception (and status update)