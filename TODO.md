# JobBright Core Pipeline TODO List (Focus: Resume -> Match -> Tailor -> Apply)

**Legend:**
*   ⬜ = Not Started
*   🚧 = In Progress / Blocked
*   ✅ = Done

---

## 1. Resume Intake & Processing

*   🚧 **Frontend Parsing (`usePdfParser.ts`):** Verify PDF parsing extracts necessary text items reliably.
*   ✅ **Backend Preprocessing (`resume_tailoring.py`):** Implemented basic `_preprocess_text_items` to sort text items by coordinates (Y, X) before joining.
*   ✅ **API Endpoint (`/api/v1/resumes/parse-and-tailor`):** API route implemented in `api/resumes.py` to receive data, call `resume_tailoring.py`, and save `structured_data`.
*   ✅ **LLM Parsing (`resume_tailoring.py`):** Basic LLM call implemented to parse raw text to `StructuredResume`.
*   🚧 **LLM Parsing Quality & Tuning:** Test and tune the LLM parsing prompt (`_parse_resume_with_llm`) for accuracy and robustness across different resume formats.
*   ✅ **LLM Tailoring (`resume_tailoring.py`):** Basic LLM calls implemented to tailor objective, skills, experience based on job description (`tailor_content`).
*   🚧 **LLM Tailoring Quality & Tuning:** Test and tune the LLM tailoring prompts for relevance and quality. Ensure it handles cases where structured data fields are missing. Needs integration testing with job descriptions.
*   ✅ **DB Storage:** `structured_data` JSONB column added and basic CRUD operations exist.
*   ✅ **Error Handling & Logging (`resume_tailoring.py`):** Added more detailed logging throughout parsing and tailoring functions (including truncated prompts/responses). Error handling relies on try/except blocks and returning specific failure messages in the objective.
*   ✅ **Frontend Integration (`ProfileImport.tsx`):** Frontend component implements calls to `/upload` and `/parse-and-tailor` APIs and handles basic state. Needs verification (part of #12).

## 2. Job Scraping & Matching

*   ✅ **Scraping Implementation:** Basic scrapers for Greenhouse/Lever (API) and potentially Indeed (Playwright via `sites.yml`) exist.
*   ✅ **Scraping Robustness & Scheduling:** Individual scrapers and `run_scrapers` in `scraping.py` include basic try/except error handling. Scheduling is configured via Celery Beat in `celery_app.py` (runs `run_all_scrapers_task` every 6 hours).
*   ✅ **Job Embedding:** Jobs seem to be getting embeddings generated (`crud/job.py`).
*   ✅ **Qdrant Indexing:** Logic exists to index jobs with embeddings (`matching.py`, `tasks.py`).
*   🚧 **Qdrant Setup:** Ensure Qdrant instance is running and accessible (`infra/docker-compose.yml` or cloud).
*   🚧 **Matching Effectiveness (`matching.py`):** Refactored `search_similar_jobs` to return full `Job` objects instead of just IDs. Further evaluation/tuning of embeddings or search parameters may be needed. Ensure it correctly uses resume embeddings against job embeddings.

## 3. Application Triggering & Quota Management

*   ✅ **Matching-to-Application Logic:** Implemented Celery task `process_user_job_matches` (`tasks.py`) that:
    *   Takes `user_id`, `resume_id`. Fetches resume embedding. Calls `matching.search_similar_jobs`.
    *   Checks for existing applications (`crud.application.get_application_by_details`).
    *   Checks user's auto-apply quota (`autosubmit.check_user_quota`).
    *   Creates `Application` records (`crud.application.create_application`).
    *   Triggers `tasks.trigger_auto_apply` via `.delay()` for each new application.
*   ✅ **Quota Check (Safeguard in apply_to_job_async):** `autosubmit.apply_to_job_async` contains a safeguard check.
*   ✅ **Quota Logic Refinement:** Verified `check_user_quota` in `autosubmit.py` correctly reflects tier limits (Free: 50/month count, Pro/Elite: returns 99999).

## 4. Tailored PDF Generation

*   ✅ **PDF Generator Service (`pdf_generator.py`):** Service created to generate PDF from `StructuredResume` using `reportlab`.
*   ✅ **Schema Mapping & Verification:** Verified `StructuredResumePdfGenerator` correctly maps fields from the `StructuredResume` Pydantic model to ReportLab logic. (Some schema fields like `website`, `keywords`, `education.highlights` are defined but not currently rendered).
*   ✅ **Styling & ATS Friendliness:** Styles in `resume_pdf_styles.py` use standard fonts (Calibri) and clear sectioning, generally ATS-friendly. Potential minor risks: uses a two-column table for layout (single-column flow is safer) and has very narrow margins (0.1 inch).

## 5. Auto-Application Execution (`browser-use` Agent)

*   ✅ **Integration:** `autosubmit.py` now generates/selects the correct PDF (original or tailored) and includes its path in the agent prompt.
*   ✅ **Agent Prompt Refinement:** Reviewed `task_prompt` in `autosubmit.py`. It includes clear instructions for navigation, filling profile info, using the correct resume path, handling standard/EEOC questions, and skipping complex ones. Further refinement will depend on real-world testing.
*   ✅ **Agent Success Monitoring:** `autosubmit.py` inspects `AgentHistoryList` (`is_done()`, `has_errors()`, `final_result()`, `errors()`), logs outcomes, and updates `Application` status/notes accordingly. This provides data for monitoring (e.g., via DB queries or log analysis).
*   ✅ **Basic Artifacts (Screenshot):** Screenshot URL from the agent run is saved to the `Application` record via S3 upload logic.
*   ✅ **Error Telemetry:** Added `sentry-sdk` to requirements, added `SENTRY_DSN` to config, initialized SDK in `celery_app.py`, and added `sentry_sdk.capture_exception()` calls in `autosubmit.py` error handling.

## 6. Core Infrastructure (Pipeline Minimum)

*   ✅ **Database Setup:** PostgreSQL service (`db`) defined in `docker-compose.yml`. Backend/worker configured to connect. Schema application handled by backend entrypoint (`alembic upgrade head`).
*   ✅ **Vector DB Setup:** Qdrant service (`qdrant`) defined in `docker-compose.yml`. Backend/worker configured to connect.
*   ✅ **AWS S3 Setup:** Settings (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION_NAME`, `S3_BUCKET_NAME`) are defined in `config.py` to load from environment. Code in `api/resumes.py` and `services/autosubmit.py` uses these settings. Actual credentials must be provided in the environment.
*   ✅ **Celery Setup:** Redis service (`redis`) defined in `docker-compose.yml` as broker/backend. Celery worker service (`worker`) defined. Backend/worker configured to connect.
*   ✅ **Configuration (`core/config.py`):** Ensure all necessary settings (DB URLs, API keys, S3 creds, Qdrant info, Azure OpenAI creds) are loaded correctly.

## 7. Testing (Core Pipeline Focus)

*   ✅ **Unit/Integration Tests:** Basic tests added for:
    *   `resume_tailoring.py` (✅ Added tests for preprocessing, parsing failures, tailoring failures).
    *   `pdf_generator.py` (✅ Added basic tests for file creation).
    *   `matching.py` (✅ Added basic unit tests with mocks).
    *   `autosubmit.py` (✅ Added basic unit tests for quota check and initial error handling).
    *   Quota checking logic before task queuing (✅ Added basic tests in `test_tasks.py`).
*   ⬜ **End-to-End Tests:** Create E2E tests covering the main flow: Resume Upload -> Tailoring -> Matching -> Application Trigger -> Auto-Submit Attempt (mocking the browser agent's final result).

---
*Removed sections related to non-core features (Gamification, VisaPulse, Slack, etc.), deprecated items, advanced infrastructure (Observability, Compliance, RBAC beyond basic needs), and manual tasks.*

### Backend Startup Warnings (To Investigate)
- [ ] Qdrant: `UserWarning: Api key is used with an insecure connection.` (See `services/matching.py:29`) - Investigate if HTTPS/secure connection is needed/possible.
- [ ] PDF Generation: `WARNING [root] Could not import resume_pdf_styles or fonts from open_source_reuse: No module named 'open_source_reuse'. Using basic styles.` - Ensure `open_source_reuse` is installed correctly or remove dependency.
- [ ] Resume Ingestion: `WARNING [app.services.resume_optimizer] unoconv command not found.` - Install `unoconv` and LibreOffice or find alternative for doc conversion.
- [ ] Resume Parsing: `WARNING [app.services.resume_optimizer] spaCy model 'en_core_web_sm' not found.` - Download the model (`python -m spacy download en_core_web_sm`).

## 8. Frontend Dashboard Functionality

*   ⬜ **User Data Display:** Fetch and display real user data (plan, quota, stats) in the header and "Auto Apply Progress" card (`dashboard/page.tsx`).
*   ⬜ **Preferences Card:** Implement the "Preferences" card to fetch and save user job search criteria via API calls (`dashboard/page.tsx`).
*   ⬜ **Resumes Card:** Make the "Resumes" card fully functional: fetch existing resumes, handle uploads/deletes via API calls (`dashboard/page.tsx`).
*   ⬜ **Activity Log Card:** Connect the "Activity Log" card to fetch real activity data from the backend API (`dashboard/page.tsx`, `ActivityLogViewer`).
*   ⬜ **Header Actions:** Connect the "Upgrade", "Help", and "User Profile" buttons in the header to their respective actions/pages.
