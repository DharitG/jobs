# JobBright TODO List

**Legend:**
*   ⬜ = Not Started
*   🚧 = In Progress / Blocked
*   ✅ = Done

---

## 1. Core Focus: Auto-Apply & Supporting Systems

This section covers the primary development focus, including the auto-apply mechanism and the systems it directly relies upon (scraping, matching, resume optimization, core UI).

### Auto-Apply Service (`services/autosubmit.py`)
*   🚧 **Adapter Pattern (Form Policy):** Implement handling for site-specific quirks (EEOC modals, file uploads, scrolling). Needs site-specific examples.
*   🚧 **CAPTCHA Strategy (Tier 2 - Auto-solve):** Implement `CaptchaGate.solve` using services like 2Captcha/Anti-Captcha. Requires external service integration.
*   ⬜ **CAPTCHA Strategy (Tier 3 - AI-solve):** Implement OCR/simple math solving for basic CAPTCHAs. Requires additional libraries/setup.
*   ⬜ **CAPTCHA Strategy (Tier 4 - Human-loop):** Implement escalation to a human review queue. Requires external service/tooling.
*   🚧 **Error Telemetry & Artifacts:** Fully integrate error reporting (e.g., Sentry) and artifact storage (e.g., S3). Currently placeholders.
*   ⬜ **Self-Healing & Testing:** Implement nightly synthetic runs, golden-path tests in CI. Requires CI setup.
*   🚧 **Pro/Elite Tier Logic:** Refine unlimited quota logic (Pro) and implement actual throttling heuristics (Elite). Currently placeholders.
*   ⬜ **Complete Adapter Implementations:** Finish detailed logic for Greenhouse, Lever, Indeed, Workday adapters (custom questions, EEOC handling, specific form policies).
*   ⬜ **Full Human Emulation:** Implement robust fingerprinting, header rotation, proxy management.
*   ⬜ **Advanced Submission Verification:** Explore network hooks or email watching for more reliable success confirmation.

### Job Scraping (`services/scraping.py`, `crawler/job_crawler.py`)
*   🚧 **Scraping Implementation:** Fully implement and test Indeed (Playwright), Greenhouse (API), and Lever (API) adapters.
*   ⬜ **Scraping Robustness:** Implement ToS checks/fallbacks, improve error handling, and establish a maintenance strategy for changing website structures.
*   ⬜ **Scheduling:** Implement job scheduling for the crawler (e.g., using Celery Beat).

### Job Matching (`services/matching.py`)
*   🚧 **Matching Effectiveness:** Evaluate and potentially improve semantic matching quality (e.g., different embedding models, fine-tuning, better text extraction from source).

### Resume Optimization (`services/resume_optimizer.py`, `api/optimize.py`)
*   🚧 **Parsing Robustness:** Improve DOCX parsing logic (`is_likely_heading`, `get_paragraph_type`, handle tables/columns) for better accuracy. Address `unoconv` dependency/alternatives.
*   🚧 **Patching Formatting Preservation:** Enhance `apply_patches_to_docx` to perform run-level edits to better preserve inline formatting.
*   🚧 **Keyword Analysis Quality:** Consider using semantic embeddings instead of/alongside TF-IDF. Refine term relevance scoring.
*   🚧 **AI Rewrite Quality:** Test and tune the OpenAI prompt in `generate_rewrite_suggestion` for better results.
*   ⬜ **Database Integration:** Define and implement storage for file paths (original, converted, modified, exported) and diffs, likely extending `models/resume.py` or adding new models. Update CRUD operations.
*   ⬜ **Configuration:** Move hardcoded values (temp paths, API keys, model names) to `core/config.py`.
*   🚧 **Error Handling & Logging:** Add more robust error handling and detailed logging throughout the service and API.
*   ⬜ **Frontend Integration:** Develop UI components to interact with the `/optimize/*` API endpoints.

### Core Frontend (Dashboard & Related)
*   🚧 **Application Pipeline Dashboard (`app/dashboard/page.tsx`, `components/PipelineBoard.tsx`):** Polish UI, ensure reliable data fetching/updates from backend (tRPC `application.list` & `updateStatus`), handle edge cases and loading/error states.
*   🚧 **Limited GPT Resume Edits UI (`components/ResumeEditModal.tsx`):** Connect UI to backend resume optimization API endpoints. Resolve any TS path alias issues.

---

## 2. Near-Term Features (Partially Implemented)

Features with some backend structure or UI components already started.

*   🚧 **Daily Streak Gamification (`components/DailyStreak.tsx`):** Implement backend logic and connect frontend component via tRPC.
*   🚧 **VisaPulse (`services/visa_alerts.py`, `components/VisaPulse.tsx`):** Implement actual visa alert logic in the backend service. Ensure frontend correctly displays data and handles interactions (e.g., lawyer chat button).
*   🚧 **GPT-4o Resume/Cover Letter Rewriting:** Implement backend service logic and connect `ResumeEditModal.tsx` or new components.
*   🚧 **Interview Flash-Cards (`components/InterviewFlashCard.tsx`):** Implement backend LLM Q&A generation and connect frontend component via tRPC.
*   🚧 **Priority Support Chat Bot (`components/SupportChatTrigger.tsx`):** Integrate with a third-party chat/support service.
*   🚧 **VisaPulse In-app Lawyer Chat (`components/VisaPulse.tsx`):** Implement backend logic/integration for connecting users (if planned).
*   🚧 **Mock Interview Scheduling (`components/MockInterviewScheduler.tsx`):** Implement backend scheduling logic and connect frontend component via tRPC.
*   🚧 **Slack Alerts (`components/SlackAlertSettings.tsx`):** Implement backend integration for sending Slack notifications and connect frontend component via tRPC.
*   🚧 **Stripe Integration (`api/subs.py`, `pages/pricing.tsx`, tRPC `subscription` router):** Fully implement subscription creation, status checking, webhook handling. Connect frontend checkout flow and annual billing toggle. Implement paywall/upgrade prompts based on subscription status.
*   🚧 **Personal Success Coach (`components/SuccessCoachSection.tsx`):** Implement backend logic for assigning/managing coaches and connect frontend component via tRPC.
*   🚧 **Guaranteed Résumé Review (`components/ResumeReviewSubmit.tsx`):** Implement backend workflow for managing submissions/feedback and connect frontend component via tRPC.
*   🚧 **Referral Credits System (`components/ReferralSection.tsx`):** Implement backend logic for tracking referrals/credits and connect frontend component via tRPC.
*   🚧 **Mini-milestones/Confetti/Badges (`components/MilestoneBadge.tsx`):** Implement backend triggers and connect frontend component via tRPC.
*   🚧 **Affiliate Rev-share Tracking (`components/AffiliateDashboard.tsx`):** Implement backend logic and connect frontend component via tRPC.

---

## 3. Foundational Backend & Infrastructure

Core underlying systems, operational tasks, and compliance.

*   ⬜ **RBAC:** Implement Role-Based Access Control using Auth0 roles/permissions, protecting relevant API endpoints.
*   🚧 **Configuration Management:** Ensure all secrets and environment-specific settings are loaded via `core/config.py` and not hardcoded.
*   🚧 **Infrastructure (`infra/docker-compose.yml`):** Refine Docker Compose for robustness, potentially add health checks for Qdrant.
*   ⬜ **Deployment Pipeline:** Configure CI/CD (e.g., GitHub Actions to Render/AWS).
*   ⬜ **Managed Services:** Setup and configure managed Postgres/Redis/Qdrant for production.
*   ⬜ **Observability:** Setup Prometheus + Grafana (or Render Metrics), Logging Aggregation, Sentry Error Tracking.
*   ⬜ **Audit Logging:** Implement basic audit logging for critical actions.
*   ⬜ **Compliance:** Implement GDPR/CCPA Data Deletion endpoint/logic. Verify PII encryption at rest. Implement Scraper ToS Checks/API fallback.
*   ⬜ **Security Hardening:** Review dependencies, secrets management, implement rate limiting, configure firewalls. Conduct security audit before launch.

---

## 4. Testing

*   ⬜ **Backend Unit/Integration Tests:** Write comprehensive Pytest tests for core services (autosubmit, optimize, matching, scraping), CRUD operations, security, and API endpoints.
*   🚧 **Frontend Unit Tests (`vitest`):** Complete unit tests for remaining components and hooks. Ensure adequate coverage.
*   ⬜ **End-to-End Tests:** Write E2E tests (e.g., Cypress, Playwright) for critical user flows (signup, login, applying, optimizing resume, upgrading subscription).

---

## 5. Manual / Non-Coding Tasks

*   ⬜ Register `jobbright.ai` domain.
*   ⬜ Create wait-list page on Vercel (if needed).
*   ⬜ Book 5 international-student focus calls.
*   ⬜ Draft Privacy Policy & ToS (incl. AI disclosure).
