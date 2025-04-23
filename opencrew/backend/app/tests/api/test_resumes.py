# opencrew/backend/app/tests/api/test_resumes.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from typing import Dict, Any, Generator # Import Generator
import io
import uuid # Import the uuid module
import json # Import json for the validation error test

# Correct imports based on project structure
# Import specific crud modules with aliases
from app.crud import user as crud_user
from app.crud import resume as crud_resume
from app.core.config import settings
from app.schemas.user import UserCreate # Direct schema import
from app.schemas.resume import ResumeCreate, ResumeParseRequest, StructuredResume, BasicInfo, SkillItem, PdfTextItem # Direct schema imports, add SkillItem, PdfTextItem
from app.models.user import User # Direct model import
from app.models.resume import Resume # Direct model import
# from app.db.session import get_db # Not strictly needed here if client fixture handles override well
from app.api.users import get_current_active_user # Import the correct dependency function
from app.main import app # Import app to potentially get API prefix

# --- Helper Fixtures ---

@pytest.fixture(scope="function")
def test_user(db: Session) -> User: # Use direct model import
    """Fixture to create a test user in the database."""
    # Use a fixed, valid UUID string for consistency
    user_email = "testuser.resumeapi@example.com" # Make email specific to avoid collisions
    user_supabase_id_str = "d8a8c8e0-0b3a-4b1e-8f7a-9d6f9b8e1c7b" # Example valid UUID
    user_supabase_id_uuid = uuid.UUID(user_supabase_id_str)

    # Check if user already exists
    # Use the UUID type for supabase_id comparison if the CRUD function expects it
    # Pass the UUID object to the CRUD function
    db_user = crud_user.get_user_by_supabase_id(db, supabase_id=user_supabase_id_uuid)
    if db_user:
        # Ensure user is in the current session if needed, or just return
        # db.expunge(db_user) # If using different sessions, detach first
        # return db.merge(db_user) # Merge into current session
         return db_user


    # Create user if not exists
    user_in = UserCreate( # Use direct schema import
        email=user_email,
        # Use the UUID object when creating the user
        supabase_user_id=user_supabase_id_uuid,
        # Add other required fields from your UserCreate schema if any
        full_name="Test Resume User",
        subscription_tier="free", # Assuming default tier
        # stripe_customer_id=None, # Example optional field
        # stripe_subscription_id=None,
        # stripe_subscription_status=None
    )
    return crud_user.create_user(db=db, user=user_in) # Use imported alias, corrected arg name


@pytest.fixture(scope="function")
def authenticated_client(client: TestClient, test_user: User, db: Session) -> Generator[TestClient, Any, None]: # Use direct model import
    """
    Fixture to provide a TestClient with overridden authentication dependency.
    """
    # Define the override function
    def override_get_current_user():
         # Use the user created (and potentially merged) by the test_user fixture
        return test_user

    # Apply the override using the actual dependency function used in the router
    app.dependency_overrides[get_current_active_user] = override_get_current_user # Use correct dependency function name

    yield client # Important: yield the client so override is active during test

    # Clean up the override after the test function finishes
    del app.dependency_overrides[get_current_active_user] # Use correct dependency function name


# --- Test Cases Start Here ---

# We will mock S3 and parsing in the actual test implementation
@pytest.mark.asyncio
async def test_upload_resume_success(authenticated_client: TestClient, db: Session, test_user: User, mocker): # Use direct model import
    """Tests successful resume upload, mocking S3 and parsing."""
    # Mock S3 client
    mock_s3 = mocker.patch("app.api.resumes.boto3.client")
    mock_s3_instance = mock_s3.return_value
    mock_s3_instance.upload_fileobj.return_value = None # Mock successful upload

    # Mock PDF parsing
    mock_parse = mocker.patch("app.api.resumes.profile_import.parse_pdf_to_text")
    mock_parse.return_value = "This is the extracted resume text."

    # Mock settings temporarily if S3 checks are strict before boto3 call
    # mocker.patch.object(settings, 'S3_BUCKET_NAME', 'test-bucket')
    # mocker.patch.object(settings, 'AWS_ACCESS_KEY_ID', 'test-key')
    # mocker.patch.object(settings, 'AWS_SECRET_ACCESS_KEY', 'test-secret')

    # Prepare a dummy file
    file_content = b"%PDF-1.4\nFake PDF content for testing."
    file = ("test_resume.pdf", io.BytesIO(file_content), "application/pdf")


    # Make the request using the authenticated client
    # Use client directly, assuming TestClient handles async/await internally
    response = authenticated_client.post(
        "/resumes/upload",
        files={"file": file}
    )

    # --- Assertions ---
    assert response.status_code == 200 # Assuming 200 OK on success based on your code

    data = response.json()
    assert data["filename"] == "test_resume.pdf"
    # assert data["content"] == "This is the extracted resume text." # Verify parsed content is stored (or part of it)
    assert data["owner_id"] == test_user.id # Check ownership
    assert data["original_filepath"] is not None # Check S3 key was generated
    assert data["original_filepath"].startswith(f"resumes/{test_user.id}/")
    assert data["original_filepath"].endswith("_test_resume.pdf")

    # Verify DB record
    db.refresh(test_user) # Refresh to see relationships if needed
    db_resume = db.query(Resume).filter(Resume.id == data["id"]).first() # Use direct model import
    assert db_resume is not None
    assert db_resume.filename == "test_resume.pdf"
    assert db_resume.content == "This is the extracted resume text."
    assert db_resume.owner_id == test_user.id
    assert db_resume.original_filepath == data["original_filepath"]
    assert db_resume.structured_data is None # Check initial state

    # Verify mocks were called
    mock_s3.assert_called_once()
    # Check specific S3 args if necessary:
    # upload_args, upload_kwargs = mock_s3_instance.upload_fileobj.call_args
    # assert upload_kwargs['Bucket'] == settings.S3_BUCKET_NAME
    # assert upload_kwargs['Key'] == data["original_filepath"]
    mock_parse.assert_called_once()


@pytest.mark.asyncio
async def test_upload_resume_invalid_type(authenticated_client: TestClient):
    """Tests uploading a non-PDF file."""
    file_content = b"This is not a PDF."
    file = ("test_resume.txt", io.BytesIO(file_content), "text/plain")

    response = authenticated_client.post(
        "/resumes/upload",
        files={"file": file}
    )

    assert response.status_code == 400 # Bad Request
    assert "Invalid file type" in response.json()["detail"]


@pytest.mark.asyncio
async def test_upload_resume_s3_failure(authenticated_client: TestClient, mocker):
    """Tests failure during S3 upload."""
    # Mock S3 client to raise an error
    mock_s3 = mocker.patch("app.api.resumes.boto3.client")
    mock_s3_instance = mock_s3.return_value
    from botocore.exceptions import ClientError
    mock_s3_instance.upload_fileobj.side_effect = ClientError({"Error": {"Code": "AccessDenied", "Message": "Access Denied"}}, "UploadObject")

    # Prepare dummy file
    file_content = b"%PDF-1.4\nFake PDF"
    file = ("fail_resume.pdf", io.BytesIO(file_content), "application/pdf")

    response = authenticated_client.post(
        "/resumes/upload",
        files={"file": file}
    )

    assert response.status_code == 500 # Internal Server Error
    assert "Failed to upload resume" in response.json()["detail"]


@pytest.mark.asyncio
async def test_upload_resume_parsing_failure(authenticated_client: TestClient, mocker):
    """Tests failure during PDF parsing."""
    # Mock S3 client (assume upload succeeds)
    mock_s3 = mocker.patch("app.api.resumes.boto3.client")
    mock_s3_instance = mock_s3.return_value
    mock_s3_instance.upload_fileobj.return_value = None

    # Mock PDF parsing to raise an error
    mock_parse = mocker.patch("app.api.resumes.profile_import.parse_pdf_to_text")
    mock_parse.side_effect = ValueError("Failed to parse PDF content") # Example error

    # Prepare dummy file
    file_content = b"%PDF-1.4\nFake PDF"
    file = ("bad_resume.pdf", io.BytesIO(file_content), "application/pdf")

    response = authenticated_client.post(
        "/resumes/upload",
        files={"file": file}
    )

    # Your code raises 400 for ValueError during parsing
    assert response.status_code == 400
    assert "Error parsing PDF content" in response.json()["detail"]


@pytest.mark.asyncio
async def test_read_resumes_empty(authenticated_client: TestClient):
    """Tests getting resumes when none exist for the user."""
    response = authenticated_client.get("/resumes/")

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_read_resumes_success(authenticated_client: TestClient, db: Session, test_user: User): # Use direct model import
    """Tests getting resumes when some exist for the user."""
    # Create some resumes directly using CRUD for setup
    resume1 = crud_resume.create_resume( # Use imported alias
        db=db,
        resume_in=ResumeCreate(filename="resume1.pdf", content="content1"), # Use direct schema import
        owner_id=test_user.id,
        original_filepath="s3://path/1"
    )
    resume2 = crud_resume.create_resume( # Use imported alias
        db=db,
        resume_in=ResumeCreate(filename="resume2.pdf", content="content2"), # Use direct schema import
        owner_id=test_user.id,
        original_filepath="s3://path/2"
    )
    # Create a resume for another user to ensure filtering works
    # Need a UUID for the other user as well
    other_user_supabase_id_str = "a1b2c3d4-e5f6-7890-1234-567890abcdef"
    other_user_supabase_id_uuid = uuid.UUID(other_user_supabase_id_str)
    other_user_in = UserCreate(email="other@e.com", supabase_user_id=other_user_supabase_id_uuid, full_name="Other") # Use direct schema import
    other_user = crud_user.create_user(db=db, user=other_user_in) # Corrected arg name
    crud_resume.create_resume( # Use imported alias
        db=db,
        resume_in=ResumeCreate(filename="other_resume.pdf", content="other"), # Use direct schema import
        owner_id=other_user.id,
        original_filepath="s3://path/other"
    )


    response = authenticated_client.get("/resumes/")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert {r["id"] for r in data} == {resume1.id, resume2.id}
    assert data[0]["filename"] == resume1.filename or data[1]["filename"] == resume1.filename


@pytest.mark.asyncio
async def test_read_one_resume_success(authenticated_client: TestClient, db: Session, test_user: User): # Use direct model import
    """Tests getting a specific resume successfully."""
    resume = crud_resume.create_resume( # Use imported alias
        db=db,
        resume_in=ResumeCreate(filename="my_resume.pdf", content="my content"), # Use direct schema import
        owner_id=test_user.id,
        original_filepath="s3://path/my"
    )

    response = authenticated_client.get(f"/resumes/{resume.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == resume.id
    assert data["filename"] == resume.filename
    assert data["owner_id"] == test_user.id


@pytest.mark.asyncio
async def test_read_one_resume_not_found(authenticated_client: TestClient):
    """Tests getting a non-existent resume."""
    response = authenticated_client.get("/resumes/99999") # ID that doesn't exist
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_read_one_resume_forbidden(authenticated_client: TestClient, db: Session, test_user: User): # Use direct model import
    """Tests getting a resume belonging to another user."""
    # Create another user and their resume
    # Need a UUID for the other user as well
    other_user_supabase_id_str = "b2c3d4e5-f6a7-8901-2345-67890abcdef1"
    other_user_supabase_id_uuid = uuid.UUID(other_user_supabase_id_str)
    other_user_in = UserCreate(email="other2@e.com", supabase_user_id=other_user_supabase_id_uuid, full_name="Other2") # Use direct schema import
    other_user = crud_user.create_user(db=db, user=other_user_in) # Corrected arg name
    other_resume = crud_resume.create_resume( # Use imported alias
        db=db,
        resume_in=ResumeCreate(filename="forbidden.pdf", content="forbidden"), # Use direct schema import
        owner_id=other_user.id,
        original_filepath="s3://path/forbidden"
    )

    response = authenticated_client.get(f"/resumes/{other_resume.id}")

    # Expect 404 now because the get_resume CRUD filters by owner_id
    assert response.status_code == 404 # Not Found


@pytest.mark.asyncio
async def test_update_resume_success(authenticated_client: TestClient, db: Session, test_user: User): # Use direct model import
    """Tests updating a resume successfully."""
    resume = crud_resume.create_resume( # Use imported alias
        db=db,
        resume_in=ResumeCreate(filename="update_me.pdf", content="initial content"), # Use direct schema import
        owner_id=test_user.id,
        original_filepath="s3://path/update"
    )

    update_data = {"filename": "updated_name.pdf", "content": "updated content"}

    response = authenticated_client.put(
        f"/resumes/{resume.id}",
        json=update_data
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == resume.id
    assert data["filename"] == update_data["filename"]
    assert data["content"] == update_data["content"] # Check if content is returned/updated
    assert data["owner_id"] == test_user.id

    # Verify DB
    db.refresh(resume)
    assert resume.filename == update_data["filename"]
    assert resume.content == update_data["content"]


@pytest.mark.asyncio
async def test_update_resume_not_found(authenticated_client: TestClient):
    """Tests updating a non-existent resume."""
    update_data = {"filename": "wont_work.pdf"}
    response = authenticated_client.put("/resumes/99999", json=update_data)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_resume_forbidden(authenticated_client: TestClient, db: Session, test_user: User): # Use direct model import
    """Tests updating a resume belonging to another user."""
    # Need a UUID for the other user as well
    other_user_supabase_id_str = "c3d4e5f6-a7b8-9012-3456-7890abcdef12"
    other_user_supabase_id_uuid = uuid.UUID(other_user_supabase_id_str)
    other_user_in = UserCreate(email="other3@e.com", supabase_user_id=other_user_supabase_id_uuid, full_name="Other3") # Use direct schema import
    other_user = crud_user.create_user(db=db, user=other_user_in) # Corrected arg name
    other_resume = crud_resume.create_resume( # Use imported alias
        db=db,
        resume_in=ResumeCreate(filename="forbidden_update.pdf", content="forbidden"), # Use direct schema import
        owner_id=other_user.id,
        original_filepath="s3://path/forbidden_upd"
    )

    update_data = {"filename": "hacked.pdf"}
    response = authenticated_client.put(f"/resumes/{other_resume.id}", json=update_data)
    # Expect 404 now because the get_resume CRUD filters by owner_id before attempting update
    assert response.status_code == 404 # Not Found


@pytest.mark.asyncio
async def test_delete_resume_success(authenticated_client: TestClient, db: Session, test_user: User): # Use direct model import
    """Tests deleting a resume successfully."""
    resume = crud_resume.create_resume( # Use imported alias
        db=db,
        resume_in=ResumeCreate(filename="delete_me.pdf", content="delete content"), # Use direct schema import
        owner_id=test_user.id,
        original_filepath="s3://path/delete"
    )
    resume_id = resume.id # Store ID before deletion

    response = authenticated_client.delete(f"/resumes/{resume_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == resume_id
    assert data["filename"] == "delete_me.pdf"

    # Verify deletion in DB
    deleted_db_resume = db.query(Resume).filter(Resume.id == resume_id).first() # Use direct model import
    assert deleted_db_resume is None


@pytest.mark.asyncio
async def test_delete_resume_not_found(authenticated_client: TestClient):
    """Tests deleting a non-existent resume."""
    response = authenticated_client.delete("/resumes/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_resume_forbidden(authenticated_client: TestClient, db: Session, test_user: User): # Use direct model import
    """Tests deleting a resume belonging to another user."""
    # Need a UUID for the other user as well
    other_user_supabase_id_str = "d4e5f6a7-b8c9-0123-4567-890abcdef123"
    other_user_supabase_id_uuid = uuid.UUID(other_user_supabase_id_str)
    other_user_in = UserCreate(email="other4@e.com", supabase_user_id=other_user_supabase_id_uuid, full_name="Other4") # Use direct schema import
    other_user = crud_user.create_user(db=db, user=other_user_in) # Corrected arg name
    other_resume = crud_resume.create_resume( # Use imported alias
        db=db,
        resume_in=ResumeCreate(filename="forbidden_delete.pdf", content="forbidden"), # Use direct schema import
        owner_id=other_user.id,
        original_filepath="s3://path/forbidden_del"
    )

    response = authenticated_client.delete(f"/resumes/{other_resume.id}")
    # Expect 404 now because the remove_resume CRUD filters by owner_id
    assert response.status_code == 404 # Not Found

# --- Tests for /parse-and-tailor ---

# Define a sample structured resume for mocking the service output
SAMPLE_STRUCTURED_RESUME = StructuredResume( # Use direct schema import
    basic=BasicInfo(name="Test User", email="test@example.com", phone="123-456-7890", location="Test City"), # Use direct schema import; field name was basic, not basic_info? Check schema def
    summary="A tailored summary.",
    experiences=[],
    education=[],
    skills=[
        SkillItem(category="Testing Category", skills=["Tailored Skill 1", "Tailored Skill 2"])
    ] # Provide a list of SkillItem objects
)

@pytest.mark.asyncio
async def test_parse_and_tailor_success_no_resume_id(authenticated_client: TestClient, db: Session, test_user: User, mocker): # Use direct model import
    """Tests successful parse/tailor request without saving to a specific resume."""
    # Mock the tailoring service
    mock_tailor = mocker.patch("app.api.resumes.resume_tailoring.process_and_tailor_resume")
    mock_tailor.return_value = SAMPLE_STRUCTURED_RESUME

    # Create dummy PdfTextItem data matching the schema
    dummy_text_items = [
        PdfTextItem(text="Parsed item 1.", fontName="Helvetica", width=100.0, height=10.0, x=10.0, y=10.0, hasEOL=True),
        PdfTextItem(text="Parsed item 2.", fontName="Helvetica", width=100.0, height=10.0, x=10.0, y=25.0, hasEOL=True)
    ]
    request_data = ResumeParseRequest( # Use direct schema import
        text_items=dummy_text_items, # Use the list of PdfTextItem objects
        job_description="Software Engineer job description.",
        job_id=123, # Example job ID
        resume_id=None # Explicitly None
    )

    response = authenticated_client.post(
        "/resumes/parse-and-tailor",
        json=request_data.model_dump() # Use model_dump() for Pydantic v2
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] is not None
    # Compare dict representations for complex nested objects
    assert data["structured_resume"] == SAMPLE_STRUCTURED_RESUME.model_dump() # Use model_dump() for Pydantic v2

    # Verify service was called
    mock_tailor.assert_called_once() # Check call args separately if needed
    # Extract call args:
    call_args, call_kwargs = mock_tailor.call_args
    assert call_kwargs['text_items'] == dummy_text_items # Compare PdfTextItem lists
    assert call_kwargs['job_description'] == request_data.job_description

    # Verify no DB update attempted as resume_id was None


@pytest.mark.asyncio
async def test_parse_and_tailor_success_with_resume_id(authenticated_client: TestClient, db: Session, test_user: User, mocker): # Use direct model import
    """Tests successful parse/tailor request saving to an existing resume."""
     # Create a resume first
    resume = crud_resume.create_resume( # Use imported alias
        db=db,
        resume_in=ResumeCreate(filename="tailor_target.pdf", content="initial"), # Use direct schema import
        owner_id=test_user.id,
        original_filepath="s3://path/tailor"
    )

    # Mock the tailoring service
    mock_tailor = mocker.patch("app.api.resumes.resume_tailoring.process_and_tailor_resume")
    mock_tailor.return_value = SAMPLE_STRUCTURED_RESUME

    # Create dummy PdfTextItem data matching the schema
    dummy_text_items = [
        PdfTextItem(text="Item A.", fontName="Times", width=50.0, height=12.0, x=20.0, y=30.0, hasEOL=False),
        PdfTextItem(text="Item B.", fontName="Times", width=50.0, height=12.0, x=75.0, y=30.0, hasEOL=True)
    ]
    request_data = ResumeParseRequest( # Use direct schema import
        text_items=dummy_text_items, # Use the list of PdfTextItem objects
        job_description="Data Scientist job.",
        job_id=456,
        resume_id=resume.id # Provide the ID of the created resume
    )

    response = authenticated_client.post(
        "/resumes/parse-and-tailor",
        json=request_data.model_dump() # Use model_dump() for Pydantic v2
    )

    assert response.status_code == 200
    data = response.json()
    assert data["structured_resume"] == SAMPLE_STRUCTURED_RESUME.model_dump() # Use model_dump() for Pydantic v2

    # Verify service was called
    mock_tailor.assert_called_once()

    # Verify DB update
    db.refresh(resume)
    assert resume.structured_data is not None
    # Compare nested dicts carefully
    assert resume.structured_data["basic"]["name"] == SAMPLE_STRUCTURED_RESUME.basic.name # Field name is basic
    # Make sure skills are compared correctly (assuming model_dump provides comparable format)
    assert resume.structured_data["skills"] == [s.model_dump() for s in SAMPLE_STRUCTURED_RESUME.skills]


@pytest.mark.asyncio
async def test_parse_and_tailor_resume_not_found(authenticated_client: TestClient, db: Session, test_user: User, mocker): # Use direct model import
    """Tests parse/tailor request when resume_id does not exist."""
    # Mock the tailoring service (it should still be called)
    mock_tailor = mocker.patch("app.api.resumes.resume_tailoring.process_and_tailor_resume")
    mock_tailor.return_value = SAMPLE_STRUCTURED_RESUME

    # Create dummy PdfTextItem data matching the schema
    dummy_text_items = [
        PdfTextItem(text="Item X.", fontName="Arial", width=80.0, height=9.0, x=5.0, y=50.0, hasEOL=True)
    ]
    request_data = ResumeParseRequest( # Use direct schema import
        text_items=dummy_text_items, # Use the list of PdfTextItem objects
        job_description="Job desc.",
        job_id=789,
        resume_id=99999 # Non-existent ID
    )

    response = authenticated_client.post(
        "/resumes/parse-and-tailor",
        json=request_data.model_dump() # Use model_dump() for Pydantic v2
    )

    # The endpoint currently logs a warning but returns 200
    # Adjust assertion if behavior changes to return an error
    assert response.status_code == 200
    data = response.json()
    assert data["structured_resume"] == SAMPLE_STRUCTURED_RESUME.model_dump() # Use model_dump() for Pydantic v2
    # Verify service was called
    mock_tailor.assert_called_once()
    # Verify no DB update occurred (implicitly tested by checking logs or if an error was raised)

@pytest.mark.asyncio
async def test_parse_and_tailor_service_error(authenticated_client: TestClient, db: Session, test_user: User, mocker): # Use direct model import
    """Tests parse/tailor when the tailoring service raises an error."""
    # Mock the tailoring service to raise an exception
    mock_tailor = mocker.patch("app.api.resumes.resume_tailoring.process_and_tailor_resume")
    mock_tailor.side_effect = Exception("Tailoring service failed!")

    # Create dummy PdfTextItem data matching the schema
    dummy_text_items = [
        PdfTextItem(text="Item Z.", fontName="Courier", width=90.0, height=11.0, x=15.0, y=60.0, hasEOL=True)
    ]
    request_data = ResumeParseRequest( # Use direct schema import
        text_items=dummy_text_items, # Use the list of PdfTextItem objects
        job_description="Job.",
        job_id=101,
        resume_id=None
    )

    response = authenticated_client.post(
        "/resumes/parse-and-tailor",
        json=request_data.model_dump() # Use model_dump() for Pydantic v2
    )

    assert response.status_code == 500
    assert "Failed to process and tailor resume" in response.json()["detail"]
    assert "Tailoring service failed!" in response.json()["detail"]
    # Verify service was called
    mock_tailor.assert_called_once()