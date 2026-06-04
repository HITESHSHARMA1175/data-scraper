Quick run instructions

1) Create and activate a Python virtual environment (Windows PowerShell example):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) Install backend dependencies:

```powershell
cd backend
pip install -r requirements.txt
```

3) Start the Flask backend API:

```powershell
python app.py
```

The backend will run on http://localhost:5000

4) Serve the frontend (recommended to avoid file:// CORS issues):

```powershell
cd ..\frontend
python -m http.server 8000
```

Open the frontend at http://localhost:8000/index.html and start scraping.

Notes:
- The scraper uses `undetected-chromedriver`; ensure Google Chrome is installed and compatible.
- The backend now prefers `backend/data/` for scraped CSV outputs. Legacy `backend/Scrapped/` is still supported.
- The scraper can read a URL from `backend/tmp/temp_url.txt`. For backward compatibility it will also read `backend/temp_url.txt`.
- If you prefer running the scraper directly, run `python backend/scraper/main.py` and provide input or create `backend/tmp/temp_url.txt` with the target URL.
