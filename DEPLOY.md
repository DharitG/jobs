# JobBright Deployment Guide (Using Render)

This guide provides step-by-step instructions for deploying the JobBright frontend and backend applications to Render.

**Assumptions:**
*   Your code is hosted on GitHub or GitLab.
*   You have registered the `jobbright.ai` domain (or your desired domain).

## Phase 0: Prerequisites - Accounts & API Keys

Before starting the deployment, ensure you have accounts and necessary keys/secrets from the following services:

1.  **Version Control:** GitHub or GitLab account connected to your local repository.
2.  **Hosting:** [Render](https://render.com/) account.
3.  **Authentication:** [Auth0](https://auth0.com/) account.
4.  **Payments (Optional but needed for Pro/Elite):** [Stripe](https://stripe.com/) account.
5.  **AI Features (Optional but needed):** [OpenAI](https://openai.com/) account (or other LLM provider).
6.  **Domain Registrar:** Access to manage DNS records for `jobbright.ai`.

**Action:** Sign up for these services if you haven't already.

## Phase 1: Service Setup & Key Generation

### 1.1. Auth0 Setup

*   **Log in to Auth0 Dashboard.**
*   **Create Application (Frontend):**
    *   Go to `Applications` -> `Applications` -> `Create Application`.
    *   Choose `Single Page Web Applications` (SPA). Give it a name (e.g., "JobBright Frontend").
    *   Go to the `Settings` tab for this application.
    *   Note down the **Domain** and **Client ID**. These are needed for the frontend.
    *   Configure URLs:
        *   **Allowed Callback URLs:** `http://localhost:3000/api/auth/callback`, `https://jobbright.ai/api/auth/callback` (Replace `jobbright.ai` with your actual domain). Add others if needed (e.g., Render preview URLs `https://your-frontend-service-pr-123.onrender.com/api/auth/callback`).
        *   **Allowed Logout URLs:** `http://localhost:3000`, `https://jobbright.ai`. Add others as needed.
        *   **Allowed Web Origins:** `http://localhost:3000`, `https://jobbright.ai`. Add others as needed.
        *   **Allowed Origins (CORS):** `http://localhost:3000`, `https://jobbright.ai`. Add others as needed.
    *   Scroll down to `Application Properties`. Note down the **Client Secret**. This is needed for the frontend's backend (Next.js server-side).
    *   Save changes.
*   **Create API (Backend):**
    *   Go to `Applications` -> `APIs` -> `Create API`.
    *   Give it a name (e.g., "JobBright Backend API").
    *   Set the **Identifier** (also called Audience). This should be a unique URL, but doesn't have to be publicly accessible (e.g., `https://api.jobbright.ai`). Note this down; it's the `AUTH0_API_AUDIENCE` for the backend.
    *   Leave the signing algorithm as `RS256`.
    *   Click `Create`.
*   **(Optional) Enable RBAC:**
    *   In your API settings (`Applications` -> `APIs` -> Your API), go to the `Settings` tab.
    *   Scroll down to `RBAC Settings`.
    *   Enable `Enable RBAC` and `Add Permissions in the Access Token`.
*   **(Optional) Create M2M Application (for programmatic access, e.g., testing):**
    *   Go to `Applications` -> `Applications` -> `Create Application`.
    *   Choose `Machine to Machine Applications`. Name it (e.g., "JobBright Backend M2M").
    *   Authorize it to access your "JobBright Backend API" (created above) and grant necessary permissions (if using RBAC).
    *   Note down its **Domain**, **Client ID**, and **Client Secret** if needed for scripts/tests.

### 1.2. Stripe Setup

*   **Log in to Stripe Dashboard.**
*   Go to `Developers` -> `API keys`.
*   Note down the **Publishable key** (starts with `pk_...`) - needed for the frontend.
*   Reveal and note down the **Secret key** (starts with `sk_...`) - needed for the backend.
*   **(Optional) Setup Webhooks:** Go to `Developers` -> `Webhooks`. You'll need to add an endpoint later pointing to your deployed backend (e.g., `https://your-backend-service.onrender.com/api/webhooks/stripe`) to handle events like successful payments.

### 1.3. OpenAI Setup

*   **Log in to OpenAI Platform.**
*   Go to `API keys`.
*   Create a new secret key. Give it a name (e.g., "JobBright Backend Key").
*   Copy the key immediately and store it securely. This is needed for the backend.

## Phase 2: Render Service Creation

*   **Log in to Render Dashboard.**
*   Connect your GitHub/GitLab account if you haven't already.

### 2.1. Create Managed Services

Create the following managed services first:

1.  **PostgreSQL:**
    *   Click `New` -> `PostgreSQL`.
    *   Choose a name (e.g., `jobbright-db`), select a region, choose a plan.
    *   Click `Create Database`.
    *   Once created, go to its page and note down the **Internal Connection String**. This will be your `DATABASE_URL` for the backend/worker.
2.  **Redis:**
    *   Click `New` -> `Redis`.
    *   Choose a name (e.g., `jobbright-redis`), select a region, choose a plan.
    *   Click `Create Redis`.
    *   Once created, note down the **Internal Connection URL**. This will be your `CELERY_BROKER_URL` and `CELERY_RESULT_BACKEND`.
3.  **Qdrant:**
    *   Click `New` -> `Qdrant`.
    *   Choose a name (e.g., `jobbright-qdrant`), select a region, choose a plan.
    *   Click `Create Qdrant Instance`.
    *   Once created, note down the **Internal Hostname** (e.g., `jobbright-qdrant.onrender.com`) and **Port** (usually 6333). These will be `QDRANT_HOST` and `QDRANT_PORT`.

### 2.2. Create Backend Services (API & Worker)

You need two services pointing to the *same* backend codebase but running different commands.

1.  **Backend API Service:**
    *   Click `New` -> `Private Service`.
    *   Connect your repository (`jobbright`).
    *   Choose a name (e.g., `jobbright-backend`). Select a region.
    *   **Runtime:** `Docker`.
    *   **Root Directory:** `opencrew/backend` (or wherever the backend Dockerfile is relative to the repo root).
    *   **Dockerfile Path:** `Dockerfile` (should be correct if Root Directory is set).
    *   **Plan:** Choose an appropriate instance type (consider RAM for Python/ML).
    *   Click `Create Private Service`.
2.  **Celery Worker Service:**
    *   Click `New` -> `Private Service`.
    *   Connect the *same* repository (`jobbright`).
    *   Choose a name (e.g., `jobbright-worker`). Select the same region.
    *   **Runtime:** `Docker`.
    *   **Root Directory:** `opencrew/backend`.
    *   **Dockerfile Path:** `Dockerfile`.
    *   **Start Command:** Override the Dockerfile CMD. Set this to: `celery -A app.workers.celery_app worker --loglevel=info -Q celery`
    *   **Plan:** Choose an appropriate instance type.
    *   Click `Create Private Service`.

### 2.3. Create Frontend Service

1.  **Frontend Web Service:**
    *   Click `New` -> `Web Service`.
    *   Connect your repository (`jobbright`).
    *   Choose a name (e.g., `jobbright-frontend`). Select a region.
    *   **Runtime:** `Node` (Render should detect Next.js).
    *   **Root Directory:** `opencrew/frontend`.
    *   **Build Command:** `npm install && npm run build` (or `yarn install && yarn build`).
    *   **Start Command:** `npm start` (or `yarn start`).
    *   **Plan:** Choose an appropriate instance type.
    *   Click `Create Web Service`.

## Phase 3: Environment Variable Configuration

Go to the `Environment` tab for each service created above and add the following variables. Use `Secret File` for multi-line secrets if needed. Mark sensitive values as `Secret`.

### 3.1. Backend API (`jobbright-backend`) Environment

*   `DATABASE_URL`: (Secret) The Internal Connection String from your Render PostgreSQL instance.
*   `CELERY_BROKER_URL`: (Secret) The Internal Connection URL from your Render Redis instance.
*   `CELERY_RESULT_BACKEND`: (Secret) The Internal Connection URL from your Render Redis instance.
*   `QDRANT_HOST`: The Internal Hostname from your Render Qdrant instance.
*   `QDRANT_PORT`: `6333` (or the port from your Render Qdrant instance).
*   `SECRET_KEY`: (Secret) Generate a strong random string (e.g., using `openssl rand -hex 32`).
*   `AUTH0_DOMAIN`: (Secret) Your Auth0 Domain (from Phase 1.1).
*   `AUTH0_API_AUDIENCE`: (Secret) Your Auth0 API Identifier (from Phase 1.1).
*   `STRIPE_SECRET_KEY`: (Secret) Your Stripe Secret key (from Phase 1.2).
*   `STRIPE_WEBHOOK_SECRET`: (Secret) Generate this after creating the webhook endpoint in Stripe pointing to `https://your-backend-service-url.onrender.com/api/webhooks/stripe`.
*   `OPENAI_API_KEY`: (Secret) Your OpenAI API key (from Phase 1.3).
*   `ENVIRONMENT`: `production`
*   *(Add any other backend-specific keys from `backend/.env`)*

### 3.2. Celery Worker (`jobbright-worker`) Environment

*   *(Add the **exact same** environment variables as the Backend API service above)*. The worker needs access to the database, Redis, Qdrant, and potentially other secrets/API keys depending on the tasks it runs.

### 3.3. Frontend (`jobbright-frontend`) Environment

*   `NEXT_PUBLIC_AUTH0_DOMAIN`: Your Auth0 Domain (from Phase 1.1).
*   `NEXT_PUBLIC_AUTH0_CLIENT_ID`: Your Auth0 Frontend Application Client ID (from Phase 1.1).
*   `AUTH0_SECRET`: (Secret) Generate a strong random string (e.g., `openssl rand -hex 32`). Used by `nextjs-auth0` SDK for session encryption.
*   `AUTH0_BASE_URL`: `https://jobbright.ai` (Your final production frontend URL).
*   `AUTH0_ISSUER_BASE_URL`: `https://YOUR_AUTH0_DOMAIN` (Replace with your Auth0 Domain).
*   `AUTH0_CLIENT_ID`: (Secret) Your Auth0 Frontend Application Client ID (same as `NEXT_PUBLIC_AUTH0_CLIENT_ID`).
*   `AUTH0_CLIENT_SECRET`: (Secret) Your Auth0 Frontend Application Client Secret (from Phase 1.1).
*   `NEXT_PUBLIC_API_URL`: The URL of your deployed Backend API service (e.g., `https://jobbright-backend.onrender.com`). Find this on the Render service page.
*   `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY`: Your Stripe Publishable key (from Phase 1.2).
*   *(Add any other frontend-specific keys from `frontend/.env.example`)*

**Important:** Ensure `Auto-Deploy` is enabled (usually default) on Render for your services if you want automatic deployments on pushes to your main branch.

## Phase 4: Deployment & Migrations

1.  **Trigger Deploy:** Push your latest code to the main branch of your repository. Render should automatically start building and deploying all services.
2.  **Monitor Builds:** Watch the build logs in the Render dashboard for each service. Troubleshoot any build errors (e.g., missing dependencies, Dockerfile issues).
3.  **Run Initial Migration:** Once the `jobbright-backend` service has successfully deployed *at least once*, you need to run the database migrations.
    *   Go to the `Shell` tab for the `jobbright-backend` service in Render.
    *   Run the command: `alembic upgrade head`
    *   Check the output for success or errors.
4.  **Configure Migration Job (Optional but Recommended):**
    *   Go to `New` -> `Job`.
    *   Configure it to use the same repository and environment variables as `jobbright-backend`.
    *   Set the command to `alembic upgrade head`.
    *   You can trigger this job manually after deployments or potentially automate it using deploy hooks if Render supports that for your service type. *Alternatively*, add the migration command to a deploy hook script for the backend service itself.*

## Phase 5: DNS Configuration

1.  **Find Frontend IP/Hostname:** Go to the Render dashboard for your `jobbright-frontend` Web Service. Find its public URL or IP address provided by Render.
2.  **Update DNS Records:** Go to your domain registrar (where you bought `jobbright.ai`).
    *   Update the `A` record for `jobbright.ai` to point to the IP address provided by Render.
    *   Or, update the `CNAME` record for `www.jobbright.ai` to point to the hostname provided by Render (e.g., `jobbright-frontend.onrender.com`). Check Render's documentation for custom domain setup.
    *   Allow time for DNS propagation (can take minutes to hours).

## Phase 6: Post-Deployment Checks

1.  **Access Frontend:** Open `https://jobbright.ai` in your browser.
2.  **Test Auth:** Try signing up and logging in.
3.  **Test Core Features:** Navigate the site, try interacting with features that communicate with the backend (e.g., dashboard).
4.  **Check Logs:** Monitor the runtime logs for all services (Frontend, Backend API, Worker) in the Render dashboard for any errors.
5.  **Stripe Webhook:** Ensure your Stripe webhook endpoint is configured correctly in Stripe and pointing to your live backend URL.

---

This guide provides a comprehensive overview. Specific commands or UI elements in Render/Auth0/Stripe might change over time. Always refer to the official documentation of each service for the most up-to-date instructions.
