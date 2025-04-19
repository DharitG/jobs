from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Query
from fastapi.responses import FileResponse # Added for PDF export
from pathlib import Path
import logging
from typing import Literal # Added for query parameter validation

# Assuming your project structure allows this import path
from app.services import resume_optimizer
from app.schemas.optimize import ( # Added Patch schemas
    IngestResponse, ParseRequest, ParsedResume,
    KeywordAnalysisRequest, KeywordAnalysisResponse,
    RewriteRequest, RewriteResponse,
    Patch, ApplyPatchRequest, ApplyPatchResponse, # Added patch schemas
    DiffRequest, DiffResponse # Added diff schemas
)
# Import dependencies needed for authentication if required later
# from app.api.users import get_current_active_user
# from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post(
    "/ingest",
    response_model=IngestResponse,
    summary="Ingest and Convert Resume",
    description="Accepts an uploaded resume file (PDF, DOC, DOCX, etc.), "
                "converts it to DOCX format using unoconv, and returns the path "
                "to the converted file.",
    tags=["Resume Optimization"] # Add a tag for OpenAPI docs
)
async def ingest_resume(
    file: UploadFile = File(..., description="The resume file to upload."),
    # Uncomment if authentication is needed
    # current_user: User = Depends(get_current_active_user)
):
    """
    Ingest endpoint:
    - Receives an uploaded file.
    - Calls the conversion service.
    - Returns the path to the converted DOCX file.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided.")

    # Basic content type check (can be expanded)
    allowed_content_types = [
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        # Add other types unoconv might support if needed
    ]
    # Note: Content-Type header can be spoofed, but it's a basic check.
    # More robust validation might involve checking file magic numbers.
    if file.content_type not in allowed_content_types:
         logger.warning(f"Rejected file '{file.filename}' with unsupported content type: {file.content_type}")
         # Allow conversion attempt anyway, unoconv might handle it
         # raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")


    logger.info(f"Received file for ingestion: {file.filename} ({file.content_type})")
    # Add user info to log if auth is enabled: logger.info(f"User {current_user.email} uploading {file.filename}")

    try:
        converted_path: Path = await resume_optimizer.convert_to_docx(file)
        # Convert Path object to string for the response model
        converted_path_str = str(converted_path.resolve())

        # In a real application, you might store metadata about this conversion
        # (original filename, user ID, converted path/ID, timestamp) in your database.

        return IngestResponse(
            message="File successfully ingested and converted to DOCX.",
            converted_file_path=converted_path_str
        )
    except HTTPException as e:
        # Re-raise HTTPExceptions from the service layer
        raise e
    except Exception as e:
        logger.exception(f"Unexpected error during ingestion of {file.filename}: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred during file ingestion.")


@router.post(
    "/parse",
    response_model=ParsedResume,
    summary="Parse Converted Resume DOCX",
    description="Takes the path to a DOCX file (previously converted via /ingest), "
                "parses its content into a structured format (sections, items), "
                "and returns the structured data.",
    tags=["Resume Optimization"]
)
async def parse_resume_structure(
    request: ParseRequest,
    # Uncomment if authentication is needed
    # current_user: User = Depends(get_current_active_user)
):
    """
    Parse endpoint:
    - Receives the path to the converted DOCX file.
    - Calls the parsing service function.
    - Returns the structured resume data.
    """
    docx_path = Path(request.docx_file_path)
    logger.info(f"Received request to parse DOCX: {docx_path}")
    # Add user info: logger.info(f"User {current_user.email} parsing {docx_path.name}")

    # Basic validation: Check if the path seems plausible (e.g., is absolute, exists)
    # More robust validation might check if it's within an allowed directory
    if not docx_path.is_absolute():
         logger.error(f"Parsing rejected: Path is not absolute: {docx_path}")
         raise HTTPException(status_code=400, detail="Invalid file path provided (must be absolute).")
    if not docx_path.exists():
        logger.error(f"Parsing rejected: File not found at path: {docx_path}")
        raise HTTPException(status_code=404, detail="Converted DOCX file not found at the specified path.")
    if not docx_path.is_file():
         logger.error(f"Parsing rejected: Path is not a file: {docx_path}")
         raise HTTPException(status_code=400, detail="Invalid file path provided (not a file).")
    # Security check: Ensure the path is within the expected directory to prevent path traversal
    try:
        docx_path.relative_to(resume_optimizer.CONVERTED_DOCX_DIR)
    except ValueError:
        logger.error(f"Parsing rejected: Path is outside the allowed directory: {docx_path}")
        raise HTTPException(status_code=400, detail="Invalid file path provided (access denied).")


    try:
        parsed_data: ParsedResume = resume_optimizer.parse_docx_to_structure(docx_path)
        return parsed_data
    except FileNotFoundError as e:
        # Should be caught by checks above, but handle defensively
        logger.error(f"File not found during parsing service call: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception(f"Unexpected error during parsing of {docx_path.name}: {e}")
        # Use the exception message from the service if it's specific
        detail = f"An unexpected error occurred during file parsing: {str(e)}"
        if "Failed to parse DOCX file" in str(e):
             detail = str(e) # Propagate specific parsing error
        raise HTTPException(status_code=500, detail=detail)


@router.post(
    "/keyword-analysis",
    response_model=KeywordAnalysisResponse,
    summary="Analyze Keyword Gaps",
    description="Compares a job description against a parsed resume structure "
                "to identify potentially missing keywords or phrases using TF-IDF.",
    tags=["Resume Optimization"]
)
async def analyze_keywords(
    request: KeywordAnalysisRequest,
    # Uncomment if authentication is needed
    # current_user: User = Depends(get_current_active_user)
):
    """
    Keyword Analysis endpoint:
    - Receives job description text and parsed resume data.
    - Calls the keyword gap analysis service function.
    - Returns a list of missing terms with scores.
    """
    logger.info("Received request for keyword analysis.")
    # Add user info: logger.info(f"User {current_user.email} analyzing keywords.")

    if not request.job_description:
        raise HTTPException(status_code=400, detail="Job description cannot be empty.")
    if not request.parsed_resume or not request.parsed_resume.sections:
         raise HTTPException(status_code=400, detail="Parsed resume data cannot be empty.")

    try:
        analysis_result: KeywordAnalysisResponse = resume_optimizer.analyze_keyword_gaps(request)
        return analysis_result
    except Exception as e:
        logger.exception(f"Unexpected error during keyword analysis: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred during keyword analysis: {str(e)}")


@router.post(
    "/rewrite",
    response_model=RewriteResponse,
    summary="Generate Rewrite Suggestion",
    description="Uses an LLM (OpenAI) to rewrite a specific resume item (e.g., bullet point) "
                "to incorporate missing keywords.",
    tags=["Resume Optimization"]
)
async def suggest_rewrite(
    request: RewriteRequest,
    # Uncomment if authentication is needed
    # current_user: User = Depends(get_current_active_user)
):
    """
    Rewrite endpoint:
    - Receives the original resume item and keywords to inject.
    - Calls the LLM rewrite service function.
    - Returns the suggested rewritten text.
    """
    logger.info("Received request for rewrite suggestion.")
    # Add user info: logger.info(f"User {current_user.email} requesting rewrite.")

    if not request.original_item or not request.original_item.content:
        raise HTTPException(status_code=400, detail="Original resume item content cannot be empty.")
    if not request.missing_terms:
         raise HTTPException(status_code=400, detail="Missing terms list cannot be empty.")

    try:
        rewrite_result: RewriteResponse = resume_optimizer.generate_rewrite_suggestion(request)
        return rewrite_result
    except HTTPException as e:
        # Re-raise HTTPExceptions from the service layer (e.g., OpenAI config error, API error)
        raise e
    except Exception as e:
        logger.exception(f"Unexpected error during rewrite suggestion: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred during rewrite suggestion: {str(e)}")


@router.post(
    "/apply-patches",
    response_model=ApplyPatchResponse,
    summary="Apply Patches to DOCX",
    description="Applies a list of text replacement patches to the original DOCX file "
                "and saves the result as a new modified DOCX file.",
    tags=["Resume Optimization"]
)
async def apply_patches(
    request: ApplyPatchRequest,
    # Uncomment if authentication is needed
    # current_user: User = Depends(get_current_active_user)
):
    """
    Apply Patches endpoint:
    - Receives the original DOCX path and a list of patches.
    - Calls the patch application service function.
    - Returns the path to the modified DOCX file.
    """
    logger.info(f"Received request to apply {len(request.patches)} patches to {request.original_docx_path}")
    # Add user info: logger.info(f"User {current_user.email} applying patches.")

    original_path = Path(request.original_docx_path)

    # --- Input Validation ---
    if not request.patches:
        raise HTTPException(status_code=400, detail="Patches list cannot be empty.")
    if not original_path.is_absolute():
         logger.error(f"Patch application rejected: Path is not absolute: {original_path}")
         raise HTTPException(status_code=400, detail="Invalid original file path provided (must be absolute).")
    if not original_path.exists():
        logger.error(f"Patch application rejected: File not found at path: {original_path}")
        raise HTTPException(status_code=404, detail="Original DOCX file not found at the specified path.")
    if not original_path.is_file():
         logger.error(f"Patch application rejected: Path is not a file: {original_path}")
         raise HTTPException(status_code=400, detail="Invalid original file path provided (not a file).")
    # Security check
    try:
        original_path.relative_to(resume_optimizer.CONVERTED_DOCX_DIR)
    except ValueError:
        logger.error(f"Patch application rejected: Path is outside the allowed directory: {original_path}")
        raise HTTPException(status_code=400, detail="Invalid original file path provided (access denied).")
    # --- End Validation ---

    try:
        # Note: apply_patches_to_docx is synchronous, run in thread pool
        # If it becomes IO-bound (unlikely for local save), make it async
        # For now, FastAPI handles running sync functions in a thread pool
        modified_path: Path = resume_optimizer.apply_patches_to_docx(request)
        modified_path_str = str(modified_path.resolve())

        return ApplyPatchResponse(
            message="Patches applied successfully.",
            modified_docx_path=modified_path_str
        )
    except FileNotFoundError as e:
        # Should be caught by checks above, but handle defensively
        logger.error(f"File not found during patch service call: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception(f"Unexpected error during patch application for {original_path.name}: {e}")
        # Use the exception message from the service if it's specific
        detail = f"An unexpected error occurred during patch application: {str(e)}"
        if "Failed to apply patches" in str(e):
             detail = str(e) # Propagate specific error
        raise HTTPException(status_code=500, detail=detail)


@router.post(
    "/diff",
    response_model=DiffResponse,
    summary="Calculate Resume Diff",
    description="Calculates the difference between the structured representation of two DOCX files "
                "(original vs. modified) using deepdiff.",
    tags=["Resume Optimization"]
)
async def calculate_diff(
    request: DiffRequest,
    # Uncomment if authentication is needed
    # current_user: User = Depends(get_current_active_user)
):
    """
    Diff endpoint:
    - Receives paths to the original and modified DOCX files.
    - Calls the diff calculation service function.
    - Returns the diff object.
    """
    logger.info(f"Received request to calculate diff between {request.original_docx_path} and {request.modified_docx_path}")
    # Add user info: logger.info(f"User {current_user.email} calculating diff.")

    original_path = Path(request.original_docx_path)
    modified_path = Path(request.modified_docx_path)

    # --- Input Validation ---
    if not original_path.is_absolute() or not modified_path.is_absolute():
         logger.error(f"Diff rejected: Paths must be absolute.")
         raise HTTPException(status_code=400, detail="Invalid file paths provided (must be absolute).")
    if not original_path.exists():
        logger.error(f"Diff rejected: Original file not found at path: {original_path}")
        raise HTTPException(status_code=404, detail="Original DOCX file not found at the specified path.")
    if not modified_path.exists():
        logger.error(f"Diff rejected: Modified file not found at path: {modified_path}")
        raise HTTPException(status_code=404, detail="Modified DOCX file not found at the specified path.")
    if not original_path.is_file() or not modified_path.is_file():
         logger.error(f"Diff rejected: One or both paths are not files.")
         raise HTTPException(status_code=400, detail="Invalid file paths provided (not files).")

    # Security checks
    allowed_dirs = [resume_optimizer.CONVERTED_DOCX_DIR] # Only allow files in our working dir
    try:
        original_path.relative_to(resume_optimizer.CONVERTED_DOCX_DIR)
        modified_path.relative_to(resume_optimizer.CONVERTED_DOCX_DIR)
    except ValueError:
        logger.error(f"Diff rejected: Paths are outside the allowed directory.")
        raise HTTPException(status_code=400, detail="Invalid file paths provided (access denied).")
    # --- End Validation ---

    try:
        # Note: calculate_resume_diff is synchronous
        diff_result: DiffResponse = resume_optimizer.calculate_resume_diff(request)

        # Here, instead of returning the diff directly, you would typically store
        # diff_result.diff (e.g., as JSON) in a database linked to the resume versions
        # and return a confirmation or a diff ID.
        # For now, we return the calculated diff as per the schema.

        return diff_result
    except FileNotFoundError as e:
        # Should be caught by checks above, but handle defensively
        logger.error(f"File not found during diff service call: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception(f"Unexpected error during diff calculation: {e}")
        detail = f"An unexpected error occurred during diff calculation: {str(e)}"
        if "Failed to calculate resume diff" in str(e):
             detail = str(e) # Propagate specific error
        raise HTTPException(status_code=500, detail=detail)

@router.post(
    "/diff",
    response_model=DiffResponse,
    summary="Calculate Resume Diff",
    description="Calculates the difference between the structured representation of two DOCX files "
                "(original vs. modified) using deepdiff.",
    tags=["Resume Optimization"]
)
async def calculate_diff(
    request: DiffRequest,
    # Uncomment if authentication is needed
    # current_user: User = Depends(get_current_active_user)
):
    """
    Diff endpoint:
    - Receives paths to the original and modified DOCX files.
    - Calls the diff calculation service function.
    - Returns the diff object.
    """
    logger.info(f"Received request to calculate diff between {request.original_docx_path} and {request.modified_docx_path}")
    # Add user info: logger.info(f"User {current_user.email} calculating diff.")

    original_path = Path(request.original_docx_path)
    modified_path = Path(request.modified_docx_path)

    # --- Input Validation ---
    if not original_path.is_absolute() or not modified_path.is_absolute():
         logger.error(f"Diff rejected: Paths must be absolute.")
         raise HTTPException(status_code=400, detail="Invalid file paths provided (must be absolute).")
    if not original_path.exists():
        logger.error(f"Diff rejected: Original file not found at path: {original_path}")
        raise HTTPException(status_code=404, detail="Original DOCX file not found at the specified path.")
    if not modified_path.exists():
        logger.error(f"Diff rejected: Modified file not found at path: {modified_path}")
        raise HTTPException(status_code=404, detail="Modified DOCX file not found at the specified path.")
    if not original_path.is_file() or not modified_path.is_file():
         logger.error(f"Diff rejected: One or both paths are not files.")
         raise HTTPException(status_code=400, detail="Invalid file paths provided (not files).")

    # Security checks
    allowed_dirs = [resume_optimizer.CONVERTED_DOCX_DIR] # Only allow files in our working dir
    try:
        original_path.relative_to(resume_optimizer.CONVERTED_DOCX_DIR)
        modified_path.relative_to(resume_optimizer.CONVERTED_DOCX_DIR)
    except ValueError:
        logger.error(f"Diff rejected: Paths are outside the allowed directory.")
        raise HTTPException(status_code=400, detail="Invalid file paths provided (access denied).")
    # --- End Validation ---

    try:
        # Note: calculate_resume_diff is synchronous
        diff_result: DiffResponse = resume_optimizer.calculate_resume_diff(request)

        # Here, instead of returning the diff directly, you would typically store
        # diff_result.diff (e.g., as JSON) in a database linked to the resume versions
        # and return a confirmation or a diff ID.
        # For now, we return the calculated diff as per the schema.

        return diff_result
    except FileNotFoundError as e:
        # Should be caught by checks above, but handle defensively
        logger.error(f"File not found during diff service call: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception(f"Unexpected error during diff calculation: {e}")
        detail = f"An unexpected error occurred during diff calculation: {str(e)}"
        if "Failed to calculate resume diff" in str(e):
             detail = str(e) # Propagate specific error
        raise HTTPException(status_code=500, detail=detail)

@router.get(
    "/export",
    response_class=FileResponse, # Return the file directly
    summary="Export Optimized Resume as PDF",
    description="Exports a DOCX file (typically one modified by /apply-patches) "
                "to the specified PDF format ('designer' or 'ats').",
    tags=["Resume Optimization"]
)
async def export_resume_pdf(
    docx_file_path: str = Query(..., description="Absolute path to the DOCX file to export."),
    variant: Literal['designer', 'ats'] = Query(..., description="Type of PDF to generate ('designer' or 'ats')."),
    # Uncomment if authentication is needed
    # current_user: User = Depends(get_current_active_user)
):
    """
    Export endpoint:
    - Receives the path to the DOCX file and the desired variant.
    - Calls the appropriate export service function.
    - Returns the generated PDF file.
    """
    logger.info(f"Received request to export '{docx_file_path}' as '{variant}' PDF.")
    # Add user info: logger.info(f"User {current_user.email} exporting PDF.")

    docx_path = Path(docx_file_path)

    # --- Input Validation ---
    if not docx_path.is_absolute():
         logger.error(f"Export rejected: Path is not absolute: {docx_path}")
         raise HTTPException(status_code=400, detail="Invalid DOCX file path provided (must be absolute).")
    if not docx_path.exists():
        logger.error(f"Export rejected: File not found at path: {docx_path}")
        raise HTTPException(status_code=404, detail="DOCX file not found at the specified path.")
    if not docx_path.is_file():
         logger.error(f"Export rejected: Path is not a file: {docx_path}")
         raise HTTPException(status_code=400, detail="Invalid DOCX file path provided (not a file).")
    # Security check - ensure it's one of the files we could have generated
    allowed_dirs = [resume_optimizer.CONVERTED_DOCX_DIR] # Add other potential dirs if needed
    is_allowed = any(docx_path.relative_to(d) for d in allowed_dirs if docx_path.is_relative_to(d)) # Python 3.9+
    # Fallback for older Python:
    # is_allowed = False
    # for d in allowed_dirs:
    #     try:
    #         docx_path.relative_to(d)
    #         is_allowed = True
    #         break
    #     except ValueError:
    #         pass
    if not is_allowed:
        logger.error(f"Export rejected: Path is outside allowed directories: {docx_path}")
        raise HTTPException(status_code=400, detail="Invalid file path provided (access denied).")
    # --- End Validation ---

    try:
        if variant == 'designer':
            pdf_path = resume_optimizer.export_designer_pdf(docx_path)
        elif variant == 'ats':
            # Note: export_ats_pdf is synchronous
            pdf_path = resume_optimizer.export_ats_pdf(docx_path)
        else:
            # Should be caught by Literal validation, but handle defensively
            raise HTTPException(status_code=400, detail="Invalid variant specified. Use 'designer' or 'ats'.")

        # Return the file as a response
        # Use the original filename stem for the download filename if desired
        download_filename = f"{docx_path.stem}_{variant}.pdf"
        return FileResponse(path=pdf_path, media_type='application/pdf', filename=download_filename)

    except FileNotFoundError as e:
        logger.error(f"File not found during export service call: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException as e:
         # Re-raise HTTPExceptions from the service layer (e.g., unoconv errors)
         raise e
    except Exception as e:
        logger.exception(f"Unexpected error during PDF export of {docx_path.name} (variant: {variant}): {e}")
        detail = f"An unexpected error occurred during PDF export: {str(e)}"
        if "PDF conversion failed" in str(e) or "ATS-friendly PDF export" in str(e):
             detail = str(e) # Propagate specific error
        raise HTTPException(status_code=500, detail=detail)
