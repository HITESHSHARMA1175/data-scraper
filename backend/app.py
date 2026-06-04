import os
import sys
import subprocess
import csv
import threading
import webbrowser
from flask import Flask, request, jsonify
from flask_cors import CORS
from pathlib import Path

app = Flask(__name__)
CORS(app)

BACKEND_DIR = Path(__file__).parent
# Prefer a `data` folder for outputs; fall back to legacy `Scrapped` for compatibility.
SCRAPPED_DIR = BACKEND_DIR / 'data'
LEGACY_SCRAPPED = BACKEND_DIR / 'Scrapped'
if not SCRAPPED_DIR.exists():
    if LEGACY_SCRAPPED.exists():
        # keep legacy files accessible; use legacy folder if data/ doesn't exist
        SCRAPPED_DIR = LEGACY_SCRAPPED
    else:
        SCRAPPED_DIR.mkdir(exist_ok=True)

@app.route('/api/scrape', methods=['POST'])
def scrape():
    data = request.json
    
    url = None
    if 'url' in data and data['url'].strip():
        url = data['url'].strip()
    elif 'city' in data and 'keyword' in data:
        city = data['city'].replace(' ', '-').strip()
        keyword = data['keyword'].replace(' ', '-').strip()
        url = f"https://www.justdial.com/{city}/{keyword}/"
    
    if not url:
        return jsonify({"success": False, "error": "URL or City/Keyword is required"}), 400

    # Support temp URL in a `tmp/` folder for clearer separation
    tmp_dir = BACKEND_DIR / 'tmp'
    tmp_dir.mkdir(exist_ok=True)
    temp_url_path = tmp_dir / 'temp_url.txt'
    # Backwards compatibility: if legacy temp_url.txt exists at backend root, prefer it
    legacy_temp = BACKEND_DIR / 'temp_url.txt'
    if legacy_temp.exists() and not temp_url_path.exists():
        temp_url_path = legacy_temp
    try:
        # Write the URL to temp_url.txt so main.py can read it
        with open(temp_url_path, 'w') as f:
            f.write(url)
            
        # Run the scraper
        print(f"Starting scraper for URL: {url}")
        # Capture stdout/stderr to return clearer error messages to the frontend
        result = subprocess.run(
            [sys.executable, 'scraper/main.py'],
            check=True,
            cwd=str(BACKEND_DIR),
            capture_output=True,
            text=True,
        )
        print(result.stdout)
        
        # Clean up temp_url.txt
        if temp_url_path.exists():
            temp_url_path.unlink()
            
        # Determine the expected filename
        filename = f"{url.split('/')[-2]}.csv"
        file_path = SCRAPPED_DIR / filename
        
        if file_path.exists():
            # Read the generated file to return a preview
            records = []
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    records.append(row)
            
            return jsonify({
                "success": True, 
                "message": "Scraping completed",
                "filename": filename,
                "data": records
            })
        else:
            return jsonify({
                "success": False,
                "error": "Scraping completed, but output file was not found."
            })
            
    except subprocess.CalledProcessError as e:
        # Include stdout/stderr from the failed process to aid debugging
        error_msg = f"Scraper process failed with return code {e.returncode}."
        if hasattr(e, 'stdout') and e.stdout:
            error_msg += f"\nStdout:\n{e.stdout}"
        if hasattr(e, 'stderr') and e.stderr:
            error_msg += f"\nStderr:\n{e.stderr}"
        return jsonify({"success": False, "error": error_msg}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/files', methods=['GET'])
def get_files():
    files = []
    for file_path in SCRAPPED_DIR.glob('*.csv'):
        stat = file_path.stat()
        files.append({
            "name": file_path.name,
            "size": stat.st_size,
            "modified": stat.st_mtime * 1000 # Convert to milliseconds for JS
        })
    # Sort by modified time descending
    files.sort(key=lambda x: x['modified'], reverse=True)
    return jsonify({"success": True, "files": files})

@app.route('/api/file/<filename>', methods=['GET'])
def get_file(filename):
    file_path = SCRAPPED_DIR / filename
    if not file_path.exists():
        return jsonify({"success": False, "error": "File not found"}), 404
        
    try:
        records = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append(row)
        return jsonify({
            "success": True,
            "filename": filename,
            "data": records
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    total_files = 0
    total_records = 0
    
    for file_path in SCRAPPED_DIR.glob('*.csv'):
        total_files += 1
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                total_records += sum(1 for line in f) - 1 # Subtract header row
        except Exception:
            pass
            
    return jsonify({
        "success": True,
        "total_files": total_files,
        "total_records": max(0, total_records)
    })

if __name__ == '__main__':
    print("Backend API running on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
