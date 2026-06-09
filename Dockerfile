FROM python:3.10-slim

# Install system dependencies and Google Chrome
RUN apt-get update && apt-get install -y \
    chromium \
    wget \
    gnupg \
    unzip \
    xvfb \
    libgconf-2-4 \
    libnss3 \
    libxss1 \
    libasound2 \
    fonts-liberation \
    libappindicator3-1 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install them
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy the rest of the application
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# Set working directory to backend where app.py lives
WORKDIR /app/backend

# Render uses the PORT environment variable; fallback to 10000
ENV PORT=10000
EXPOSE $PORT

# Use increased timeout for long scraping processes
CMD gunicorn --bind 0.0.0.0:$PORT --timeout 120 app:app
