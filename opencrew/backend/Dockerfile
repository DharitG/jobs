# ---- Builder Stage ----
FROM python:3.11.9-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# Install build dependencies (if any, e.g., gcc for some packages)
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY ./requirements.txt .
RUN pip install --upgrade pip && \
    pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# Install Playwright and its browser dependencies
# Using --with-deps might be necessary on slim images
# RUN apt-get update && apt-get install -y --no-install-recommends wget gnupg ca-certificates && \
#     apt-get install -y --no-install-recommends libnss3 libatk1.0-0 libatk-bridge2.0-0 libx11-xcb1 libxcb-dri3-0 libdrm2 libgbm1 libxkbcommon0 libcups2 libxrandr2 libxcomposite1 libxcursor1 libxdamage1 libxi6 libxtst6 libpango-1.0-0 libcairo2 libasound2 libatspi2.0-0 && \
#     rm -rf /var/lib/apt/lists/*
# RUN playwright install-deps chromium # Use playwright's command if available and preferred
RUN pip install --no-cache-dir playwright # Ensure playwright itself is installed
RUN playwright install chromium # Install only chromium browser

# ---- Final Stage ----
FROM python:3.11.9-slim AS final

# Create a non-root user
ENV PYTHONUSERBASE=/home/appuser/.local
RUN useradd --create-home --user-group --shell /bin/bash appuser
USER appuser
WORKDIR /home/appuser/app

# Copy installed dependencies from builder stage
COPY --from=builder /wheels /wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --no-index --find-links=/wheels -r requirements.txt

# Copy Playwright browsers from builder stage
# The playwright install command typically puts browsers in a user-specific cache.
# Need to ensure the final user can access them. A common location is ~/.cache/ms-playwright
# Adjust the source path if 'playwright install' in the builder stage saves them elsewhere.
COPY --from=builder /root/.cache/ms-playwright /home/appuser/.cache/ms-playwright
ENV PLAYWRIGHT_BROWSERS_PATH=/home/appuser/.cache/ms-playwright

# Copy application code
COPY --chown=appuser:appuser . .

# Expose the port the app runs on
EXPOSE 8000

# Set the entrypoint command
# Run migrations automatically before starting the server
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1"]
# Add --workers 1 for better compatibility with Uvicorn in containers, adjust if needed