import uuid # For generating unique S3 keys
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List

from app.core.config import settings # Absolute import

from app import crud, schemas # Import crud and schemas
from app.models.user import User # Import User model specifically
from app.schemas.resume import ResumeParseRequest, ResumeParseResponse, BasicInfo, StructuredResume # Absolute import
from app.db.session import get_db # Absolute import
from app.api.users import get_current_user # Absolute import for dependency
from app.services import profile_import # Absolute import
from app.services import resume_tailoring # Absolute import
import logging # Import logging

logger = logging.getLogger(__name__) # Add logger

router = APIRouter()

@router.post("/upload", response_model=schemas.Resume)
async def upload_resume(
    *, 
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user) # Use imported User type
):
    """
    Upload a resume PDF, save it to S3, extract text,
    and save metadata to the database for the current user.
    """
    if file.content_type != 'application/pdf':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only PDF is allowed."
        )

    # --- S3 Upload ---
    s3_key = None
    if settings.S3_BUCKET_NAME and settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION_NAME
        )
        # Generate a unique key for the S3 object
        file_extension = ".pdf" # Enforce pdf
        unique_id = uuid.uuid4()
        # Sanitize filename slightly (optional)
        safe_filename = "".join(c if c.isalnum() or c in ('-', '_', '.') else '_' for c in file.filename.replace(file_extension, ''))
        s3_key = f"resumes/{current_user.id}/{unique_id}_{safe_filename}{file_extension}"

        try:
            logger.info(f"Uploading resume for user {current_user.id} to s3://{settings.S3_BUCKET_NAME}/{s3_key}")
            # Reset file pointer before reading for upload
            await file.seek(0)
            s3_client.upload_fileobj(
                Fileobj=file.file, # Access the underlying file-like object
                Bucket=settings.S3_BUCKET_NAME,
                Key=s3_key,
                ExtraArgs={'ContentType': 'application/pdf'}
            )
            logger.info(f"Successfully uploaded resume to S3 key: {s3_key}")
        except (NoCredentialsError, PartialCredentialsError):
            logger.error(f"S3 credentials not found or incomplete. Cannot upload resume for user {current_user.id}.")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="S3 storage configuration error.")
        except ClientError as e:
            logger.error(f"S3 ClientError during resume upload for user {current_user.id}: {e}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to upload resume to storage.")
        except Exception as e:
            logger.error(f"Unexpected error during S3 upload for user {current_user.id}: {e}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred during file upload.")
    else:
        logger.error(f"S3 storage is not configured. Cannot upload resume for user {current_user.id}.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Resume storage is not configured.")

    # --- Text Extraction (after successful upload) ---
    try:
        # Reset file pointer again before reading for text extraction
        await file.seek(0)
        # Assuming parse_pdf_to_text can handle the UploadFile object directly
        # If not, might need to save temporarily or read content differently
        resume_text = profile_import.parse_pdf_to_text(file)
    except ValueError as e:
        logger.error(f"Error parsing PDF content for user {current_user.id}, S3 key {s3_key}: {e}")
        # Note: File is already uploaded. Decide on cleanup or keep S3 object? For now, raise error.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error parsing PDF content: {e}"
        )
    except Exception as e:
        logger.error(f"Unexpected error during PDF parsing for user {current_user.id}, S3 key {s3_key}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred during PDF parsing.")

    if not resume_text.strip():
        logger.warning(f"Could not extract text from PDF for user {current_user.id}, S3 key {s3_key}. Saving resume entry with empty content.")
        # Decide if this is an error or if we allow storing the file without text
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Could not extract text from PDF."
        )
        
        # Keep resume_text empty if extraction failed but upload succeeded
        resume_text = ""
        # raise HTTPException(
        #     status_code=status.HTTP_400_BAD_REQUEST,
        #     detail="Could not extract text from PDF."
        # )

    # --- Database Record Creation ---
    resume_in = schemas.ResumeCreate(filename=file.filename, content=resume_text) # Pass text content
    # Pass the S3 key separately to the CRUD function
    new_resume = crud.resume.create_resume(
        db=db,
        resume_in=resume_in,
        owner_id=current_user.id,
        original_filepath=s3_key # Pass the S3 key here
    )
    logger.info(f"Created resume DB record ID {new_resume.id} for user {current_user.id} with S3 key {s3_key}")
    return new_resume

@router.get("/", response_model=List[schemas.Resume])
def read_resumes(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user) # Use imported User type
):
    """Retrieve resumes for the current user."""
    resumes = crud.resume.get_resumes_by_owner(db, owner_id=current_user.id, skip=skip, limit=limit)
    return resumes

@router.get("/{resume_id}", response_model=schemas.Resume)
def read_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # Use imported User type
):
    """Retrieve a specific resume by ID."""
    db_resume = crud.resume.get_resume(db, resume_id=resume_id)
    if db_resume is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    if db_resume.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this resume")
    return db_resume

@router.put("/{resume_id}", response_model=schemas.Resume)
def update_existing_resume(
    resume_id: int,
    resume_in: schemas.ResumeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # Use imported User type
):
    """Update a specific resume."""
    db_resume = crud.resume.get_resume(db, resume_id=resume_id)
    if db_resume is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    if db_resume.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this resume")
    updated_resume = crud.resume.update_resume(db=db, db_resume=db_resume, resume_in=resume_in)
    return updated_resume

@router.delete("/{resume_id}", response_model=schemas.Resume)
def delete_existing_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # Use imported User type
):
    """Delete a specific resume."""
    db_resume = crud.resume.get_resume(db, resume_id=resume_id)
    if db_resume is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    if db_resume.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this resume")
    deleted_resume = crud.resume.delete_resume(db=db, resume_id=resume_id)
    # The CRUD function already returns the deleted object or None
    if deleted_resume is None: # Should not happen if checks above passed, but good practice
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found during deletion")
    return deleted_resume 


# --- Endpoint for Structured PDF Parsing and Tailoring --- 

@router.post("/parse-and-tailor", response_model=ResumeParseResponse)
async def parse_and_tailor_resume(
    *, 
    db: Session = Depends(get_db),
    parse_request: schemas.ResumeParseRequest, # Use the new input schema
    current_user: User = Depends(get_current_user) # Use imported User type
):
    """
    Receives parsed PDF text items from the frontend,
    triggers backend processing/tailoring,
    and returns a structured ATS-friendly resume.
    """
    logger.info(f"Received request to parse/tailor resume for user {current_user.id}. Job ID: {parse_request.job_id}")
    logger.info(f"Received {len(parse_request.text_items)} text items.")
    
    try:
        # Call the new service function (currently uses placeholder logic)
        structured_resume = resume_tailoring.process_and_tailor_resume(
            text_items=parse_request.text_items,
            job_description=parse_request.job_description
            # TODO: Potentially fetch job description from DB using job_id if not provided directly
        )
        
        # --- Save/Update Structured Data ---
        resume_id_to_update = parse_request.resume_id # Access directly from the updated schema

        if resume_id_to_update is not None: # Check if ID was provided
            db_resume = crud.resume.get_resume(db, resume_id=resume_id_to_update, owner_id=current_user.id)
            if db_resume:
                logger.info(f"Updating structured data for resume ID: {resume_id_to_update}")
                update_schema = schemas.ResumeUpdate(structured_data=structured_resume)
                crud.resume.update_resume(db=db, db_resume=db_resume, resume_in=update_schema)
            else:
                logger.warning(f"Resume ID {resume_id_to_update} not found for user {current_user.id}. Structured data not saved.")
                # Optionally, could create a new resume record here if desired
        else:
             logger.warning("No resume_id provided in the request. Structured data not saved.")
             # Handle cases where no ID is given - perhaps create a new default resume?

        return schemas.ResumeParseResponse(
            structured_resume=structured_resume,
            message="Resume processed and tailored successfully (using placeholder logic)."
        )
        
    except Exception as e:
        logger.exception(f"Error during parse_and_tailor_resume for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process and tailor resume: {e}"
        )
