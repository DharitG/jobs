# JobBright TODO List

Based on `vision.md`.

**Legend:**
*   ✅ = Done
*   ⬜ = Not Started / In Progress
*   🚧 = In Progress / Blocked

---

## 1. Initial Setup & Scaffolding (from "Next steps" & "Repo/file-layout")

*   ⬜ Register `jobbright.ai` (Manual Task)
*   ⬜ Create wait-list page on Vercel (Manual Task, `shadcn/ui` suggested)
*   ✅ Spin up repo scaffold (`jobbright/` directory created)
*   ⬜ Book 5 international-student focus calls (Manual Task)
*   ⬜ Draft Privacy Policy & ToS (Manual Task, use template, add AI disclosure)

### Backend Scaffolding (`backend/`)
*   ✅ Create `backend/` directory
*   ✅ Create `backend/app/` directory
*   ✅ Create `backend/app/__init__.py`
*   ✅ Create `backend/app/main.py` (Basic FastAPI app)
*   ✅ Create `backend/app/core/` directory
*   ✅ Create `backend/app/core/__init__.py`
*   ✅ Create `backend/app/core/config.py` (Pydantic settings)
*   ✅ Create `backend/app/core/security.py` (Password/JWT utils)
*   ✅ Create `backend/app/api/` directory
*   ✅ Create `backend/app/api/__init__.py`
*   ✅ Create `backend/app/api/auth.py` (Token endpoint implemented)
*   ✅ Create `backend/app/api/users.py`
*   ✅ Create `backend/app/api/jobs.py`
*   ✅ Create `backend/app/api/subs.py`
*   ✅ Create `backend/app/api/visa.py`
*   ✅ Create `backend/app/models/` directory
*   ✅ Create `backend/app/models/__init__.py`
*   ✅ Create `backend/app/models/user.py` (SQLAlchemy model)
*   ✅ Create `backend/app/models/job.py`
*   ✅ Create `backend/app/models/resume.py`
*   ✅ Create `backend/app/models/payment.py`
*   ✅ Create `backend/app/schemas/` directory
*   ✅ Create `backend/app/schemas/__init__.py`
*   ✅ Create `backend/app/schemas/user.py` (Pydantic schemas)
*   ✅ Create `backend/app/schemas/job.py`
*   ✅ Create `backend/app/schemas/token.py` (For auth responses)
*   ✅ Create `backend/app/schemas/resume.py`
*   ✅ Create `backend/app/schemas/payment.py`
*   ✅ Create `backend/app/services/` directory
*   ✅ Create `backend/app/services/__init__.py`
*   ✅ Create `backend/app/services/scraping.py`
*   ✅ Create `backend/app/services/matching.py` (Initial snippet added)
*   ✅ Create `backend/app/services/autosubmit.py`
*   ✅ Create `backend/app/services/emailer.py`
*   ✅ Create `backend/app/workers/` directory
*   ✅ Create `backend/app/workers/__init__.py`
*   ✅ Create `backend/app/workers/tasks.py` (Celery/RQ tasks)
*   ✅ Create `backend/app/db/` directory
*   ✅ Create `backend/app/db/__init__.py`
*   ✅ Create `backend/app/db/session.py` (SQLAlchemy engine/session)
*   ✅ Create `backend/app/db/base.py` (Model imports for Alembic)
*   ✅ Create `backend/app/crud/` directory
*   ✅ Create `backend/app/crud/__init__.py`
*   ✅ Create `backend/app/crud/user.py` (Basic User CRUD functions)
*   ✅ Create `backend/app/crud/job.py`
*   ✅ Create `backend/app/crud/resume.py`
*   ✅ Create `backend/app/tests/` directory
*   ✅ Create `backend/app/tests/__init__.py`
*   ✅ Create `backend/Dockerfile` (Empty)
*   ✅ Create `backend/requirements.txt` (Initial dependencies added)

### Frontend Scaffolding (`frontend/`)
*   ✅ Create `frontend/` directory
*   ✅ Create `frontend/src/` directory
*   ✅ Create `frontend/src/pages/` directory
*   ✅ Create `frontend/src/pages/index.tsx` (Empty)
*   ✅ Create `frontend/src/pages/dashboard.tsx` (Empty)
*   ✅ Create `frontend/src/pages/pricing.tsx` (Empty)
*   ✅ Create `frontend/src/components/` directory
*   ✅ Create `frontend/src/components/JobCard.tsx` (Empty)
*   ✅ Create `frontend/src/components/ProgressMeter.tsx` (Empty)
*   ✅ Create `frontend/src/components/VisaPulse.tsx` (Empty)
*   ✅ Create `frontend/src/hooks/` directory
*   ✅ Create `frontend/src/styles/` directory
*   ✅ Create `frontend/src/styles/global.css` (Empty)
*   ✅ Create `frontend/Dockerfile` (Empty)
*   ✅ Create `frontend/vite.config.ts` (Empty)
*   ✅ Setup base React/Next.js project (`create-t3-app` suggested)

### Infra Scaffolding (`infra/`)
*   ✅ Create `infra/` directory
*   ✅ Create `infra/docker-compose.yml` (Empty)
*   ✅ Create `infra/terraform/` directory (Empty)

### Other Scaffolding
*   ✅ Create `scripts/` directory
*   ✅ Create `scripts/seed_db.py` (Empty)
*   ✅ Create `README.md` (Basic content)

---

## 2. Backend Development (Core Features - MVP Week 1-3)

### Auth & Users
*   ✅ Implement FastAPI app setup (`main.py`)
*   ✅ Implement Pydantic settings (`core/config.py`)
*   ✅ Implement DB Session management (`db/session.py`)
*   ⬜ ~~Implement Password Hashing & JWT (`core/security.py`)~~ (Using Auth0)
*   ⬜ Define User DB Model (`models/user.py`) - (Needs update: Remove password, add Auth0 `sub`)
*   ⬜ Define User Pydantic Schemas (`schemas/user.py`) - (Needs update: Remove password)
*   ⬜ Implement User CRUD operations (`crud/user.py`) - (Needs update: Adapt for Auth0 `sub`, remove password handling)
*   ⬜ ~~Implement Token generation endpoint (`api/auth.py`)~~ (Handled by Auth0)
*   ⬜ Implement Auth0 Backend Token Validation Middleware
*   ⬜ ~~Integrate Auth router (`main.py`)~~ (Replaced by middleware)
*   ⬜ ~~Implement User registration endpoint (`api/auth.py`)~~ (Handled by Auth0)
*   ✅ Implement User profile endpoints (`api/users.py` - e.g., get current user, update)
    *   ✅ Implement GET `/users/me` endpoint (Needs Auth0 protection)
    *   ✅ Implement PUT `/users/me` endpoint (Needs Auth0 protection)
*   ⬜ Implement Role-based access control (RBAC) foundation (Can leverage Auth0 roles/permissions)
*   ⬜ ~~Implement Google Sign-in (backend)~~ (Handled by Auth0)

### Profile & Resumes
*   ✅ Define Resume DB Model (`models/resume.py`)
*   ✅ Define Resume Pydantic Schemas (`schemas/resume.py`)
*   ✅ Implement Resume CRUD operations (`crud/resume.py`)
*   ✅ Implement Profile Import logic (LinkedIn PDF parsing) (`services/profile_import.py`, `api/resumes.py`)

### Jobs & Matching
*   ✅ Define Job DB Model (`models/job.py`)
*   ✅ Define Job Pydantic Schemas (`schemas/job.py`)
*   ✅ Implement Job CRUD operations (`crud/job.py`)
*   ✅ Implement Job Board Scraper Service (`services/scraping.py` - Placeholders)
    *   ⬜ Indeed adapter
    *   ⬜ Greenhouse adapter
    *   ⬜ Lever adapter
*   ✅ Implement Job Matching Engine (`services/matching.py` - Basic structure, needs integration)
        *   ✅ Integrate SentenceTransformer model (basic load)
        *   ✅ Integrate Qdrant client (basic connection)
        *   ✅ Implement embedding generation for resumes & JDs (Basic func exists, integrated in CRUD)
        *   ✅ Implement job ranking logic (Basic func exists)
        *   ⬜ Implement Qdrant indexing for jobs/resumes
        *   ⬜ Implement Qdrant search for job matching

### Application Tracking & Auto-Apply
*   ✅ Define Application/Tracking Model (`models/application.py`)
*   ✅ Define Application Pydantic Schemas (`schemas/application.py`)
*   ✅ Implement Application CRUD operations (`crud/application.py`)
*   ✅ Implement Application API endpoints (`api/applications.py`)
*   ⬜ Implement backend logic for Application Pipeline state
*   ⬜ Implement Auto-apply service (`services/autosubmit.py`)
    *   🚧 Setup Playwright/browser automation (Initial structure created)
    *   🚧 Implement background task queuing (`workers/tasks.py` - Celery app and task defined)
    *   🚧 Implement rate limiting/quota logic for free tier (50/mo) (User tier added, quota check func created)

### Database
*   ✅ Setup Alembic for migrations (Manual setup)
*   ✅ Create initial migration script(s) (Manual creation: 0001_create_users_table.py)
*   ✅ Create migration script for resumes/jobs (Manual creation: 0002_...)
*   ✅ Configure database connection in `docker-compose.yml` (Basic service defined)

---

## 3. Frontend Development (Core Features - MVP Week 1-3)

*   ✅ Setup base UI library (e.g., `shadcn/ui`)
*   ✅ Implement basic layout (Navbar, Footer)
*   ✅ Implement Sign-in/Sign-up flow using Auth0 SDK (Replaces previous form impl.)
*   ⬜ ~~Implement Google Sign-in flow (frontend)~~ (Handled by Auth0 SDK)
*   ✅ Implement Profile Import UI (connect to backend) - (Basic component created, API connection pending)
*   ⬜ Implement Application Pipeline Dashboard (`pages/dashboard.tsx`, `components/ProgressMeter.tsx`)
    *   ✅ Create dashboard page structure (`app/dashboard/page.tsx`)
    *   ✅ Create basic `ProgressMeter.tsx` component
    *   ✅ Implement `PipelineBoard.tsx` component (Kanban)
    *   ✅ Integrate `JobCard.tsx` into PipelineBoard
    *   ✅ Add drag-and-drop functionality
    *   🚧 Connect dashboard components to backend data (Frontend hook added, blocked by backend tRPC procedure `application.list`)
*   ✅ Implement Job listing/display (`components/JobCard.tsx`)
*   🚧 Connect Frontend API client to Backend endpoints (Dashboard connection started, blocked by backend)
*   ⬜ Implement state management (e.g., Zustand, Redux Toolkit)

---

## 4. Differentiators & Revenue Features (Week 4-12+)

### Free Tier Enhancements
*   ⬜ Implement Daily Streak Gamification (UI + Backend logic)
*   ⬜ Implement VisaPulse Backend Service (`services/visa_alerts.py`?)
*   ⬜ Implement VisaPulse UI (`components/VisaPulse.tsx`, 7-day history limit)
    *   ✅ Create basic `VisaPulse.tsx` component structure
    *   ⬜ Connect component to backend data/service
    *   ⬜ Implement 7-day history limit logic
*   ⬜ Implement Limited GPT Resume Edits (UI + Backend Integration)

### Pro Tier ($29/mo)
*   ⬜ Implement Unlimited Auto-apply (remove quota, ensure robust queueing)
*   ⬜ Integrate GPT-4o for Resume & Cover Letter Rewriting (Backend Service + UI)
*   ⬜ Implement Interview Flash-Cards (LLM Q&A Feature) (Backend Service + UI)
*   ⬜ Implement Priority Support Chat Bot (Integration)
*   ⬜ Develop Browser Extension for ATS Auto-fill (`Assisted Application`)
*   ⬜ Implement VisaPulse In-app Lawyer Chat (UI + Backend/Integration)
*   ⬜ Implement Mock Interview Scheduling Feature (UI + Backend)
*   ⬜ Implement Slack Alerts Feature (Backend Integration)
*   ⬜ Implement Stripe integration for Pro subscriptions (`models/payment.py`, `schemas/payment.py`, `api/subs.py`)
*   ⬜ Implement Paywall / Upgrade prompts in UI (`pages/pricing.tsx`)

### Elite Tier ($99/mo)
*   ⬜ Implement Personal Success Coach Feature (UI + Backend - Human/Agent Blend)
*   ⬜ Implement Guaranteed 24-hour Résumé Review Feature (UI + Backend workflow)
*   ⬜ Implement Custom Domain Email Alias Feature (Backend Service)
*   ⬜ Implement Auto-apply Throttling Heuristics (Backend logic in `services/autosubmit.py`)
*   ⬜ Implement "Warm Intro Finder" (Graph Search across external data) (Backend Service)
*   ⬜ Implement Stripe integration for Elite subscriptions
*   ⬜ Implement Annual Billing option / Discount logic

### Revenue Accelerators
*   ⬜ Implement Referral Credits system (UI + Backend logic)

---

## 5. Infrastructure & Operations

*   🚧 Configure `docker-compose.yml` for local development (Postgres, Redis, Qdrant, Backend, Worker defined)
*   ⬜ Configure Deployment Pipeline (e.g., GitHub Actions to Render/AWS)
*   ⬜ Setup Managed Postgres/Redis/Qdrant (Render/AWS/Cloud Provider)
*   ⬜ Setup Observability (Prometheus + Grafana)
*   ⬜ Setup Error Tracking (Sentry integration)
*   ⬜ Implement Audit Logging (`backend/services/audit.py`?)
*   ⬜ Implement GDPR/CCPA Data Deletion endpoint/logic
*   ⬜ Harden Security (Review dependencies, secrets management, rate limiting)

---

## 6. Growth & Persuasion Features

*   ⬜ Implement AIDA funnel copy on landing page (Content Task)
*   ⬜ Implement Loss-aversion timer for VisaPulse free tier (UI)
*   ⬜ Implement Mini-milestones/confetti/badges (UI + Backend triggers)
*   ⬜ Implement Affiliate rev-share tracking (Backend + UI for partners)
*   ⬜ Implement Risk-reversal offer logic/tracking (Backend)

---

## 7. Compliance, Risk & Ethics

*   ⬜ Implement ToS Checks/API fallback for Scrapers (`services/scraping.py`)
*   ⬜ Implement randomized intervals/human-like interaction in Auto-apply (`services/autosubmit.py`)
*   ⬜ Encrypt PII at rest (Verify DB configuration)
*   ⬜ Add Visa advice disclaimer in UI
*   ⬜ Conduct security audit before launch

---

## 8. Testing

*   ⬜ Setup Pytest framework
*   ⬜ Write unit tests for core backend logic (CRUD, security, services)
*   ⬜ Write integration tests for API endpoints
*   ⬜ Setup Frontend testing framework (e.g., Vitest, Cypress)
*   ⬜ Write unit tests for frontend components/hooks
*   ⬜ Write end-to-end tests for critical user flows 