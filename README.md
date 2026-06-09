# JustDial Data Scraper

A web application that scrapes business listings from JustDial based on city and keywords. Built with a Flask backend, a vanilla HTML/JS frontend, and an automated scraper using `undetected-chromedriver`.

## Features
- Scrape JustDial listings automatically.
- Save scraped data into CSV files.
- Modern frontend for inputting target URLs or city/keywords.
- Unified web service: backend serves the frontend statically.
- Configured for Docker and Render deployment.

## Tech Stack
- **Frontend**: HTML, Vanilla JS, CSS
- **Backend**: Python, Flask, Gunicorn
- **Scraper**: Selenium, undetected-chromedriver
- **Deployment**: Docker, Render

## Running Locally

1. Create a Python virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```
2. Install the required dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
3. Run the application (this will start the Flask server which also serves the frontend):
   ```bash
   cd backend
   python app.py
   ```
4. Open http://localhost:5000 in your browser.

## Deployment on Render

This project is configured to be deployed on Render using a Docker container, which guarantees that Google Chrome is installed for the `undetected-chromedriver` to work properly.

1. Push all your code to a GitHub repository.
2. Go to the [Render Dashboard](https://dashboard.render.com).
3. Click on **New** -> **Blueprint**.
4. Connect the repository. Render will detect the `render.yaml` file.
5. Deploy the Web Service.

**Note on Scraping Limits**: Web scraping JustDial is intensive and may hit Render's free tier memory limits. Keep an eye on the logs during execution.
