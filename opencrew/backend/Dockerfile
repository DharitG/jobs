# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required by Playwright
# Check Playwright docs for potentially needed dependencies on Debian (slim)
# Example: RUN apt-get update && apt-get install -y --no-install-recommends libnss3 libatk1.0-0 libatk-bridge2.0-0 libx11-xcb1 libxcb-dri3-0 libdrm2 libgbm1 libxkbcommon0 libcups2 libxrandr2 libxcomposite1 libxcursor1 libxdamage1 libxi6 libxtst6 libpango-1.0-0 libcairo2 libasound2 libatspi2.0-0 && rm -rf /var/lib/apt/lists/*
# RUN apt-get update && apt-get install -y --no-install-recommends wget gnupg ca-certificates && \
#     wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
#     sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list' && \
#     apt-get update && \
#     apt-get install -y google-chrome-stable fonts-ipafont-gothic fonts-wqy-zenhei fonts-thai-tlwg fonts-kacst fonts-freefont-ttf libxss1 --no-install-recommends && \
#     rm -rf /var/lib/apt/lists/*
# Note: Installing full Chrome is large. Check if Playwright's built-in browser download works first.

# Install Playwright browsers
# RUN playwright install --with-deps chromium # Install only chromium with dependencies
# This is often better done after installing python dependencies

# Copy the requirements file into the container at /app
COPY ./requirements.txt /app/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install playwright browsers after python deps
RUN playwright install chromium # Install only chromium

# Copy the rest of the application code into the container at /app
COPY . /app/

# Expose port 8000 to the outside world
EXPOSE 8000

# Define the command to run your app using uvicorn
# Use 0.0.0.0 to allow connections from outside the container
# Ensure your main FastAPI app instance is named "app" in "app.main"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"] 