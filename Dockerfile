FROM python:3.10

# Using the full python:3.10 image ensures we have all necessary system libraries.
# We only need to install chromium and xvfb for headless browser support.
RUN apt-get update && apt-get install -y \
    chromium \
    xvfb \
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

CMD gunicorn --bind 0.0.0.0:$PORT --timeout 600 app:app
