# JustDial Data Scraper - Web Frontend Setup

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python app.py
```

### 3. Open in Browser

Navigate to: **http://localhost:5000**

---

## Features

✅ **Web-based Interface** - No more terminal commands  
✅ **URL Input Form** - Easily paste JustDial URLs  
✅ **Real-time Data Display** - View scraped results instantly  
✅ **File Management** - List and view all scraped CSV files  
✅ **Statistics Dashboard** - Track total files and records  
✅ **Data Preview** - See first 20 records with pagination  

---

## How to Use

1. **Enter URL**: Paste a JustDial search URL in the input field
   - Example: `https://www.justdial.com/Bangalore/search?q=Pizza&stype=company_list`

2. **Click "Start Scraping"**: The frontend will send the URL to the backend

3. **View Results**: 
   - See preview of scraped data immediately
   - Check the "Files" tab to view all previous scrapes
   - Statistics update automatically

4. **Download Data**: All data is saved as CSV in the `Scrapped/` folder

---

## File Structure

```
JustDial-Data-Scrapper/
├── app.py                 # Flask backend API
├── main.py                # Selenium scraper
├── utils.py               # Helper functions
├── requirements.txt       # Python dependencies
├── frontend/
│   └── index.html         # Web interface (embedded CSS & JS)
├── Scrapped/              # Output CSV files
└── README.md
```

---

## API Endpoints

- `POST /api/scrape` - Start scraping with URL
- `GET /api/files` - List all CSV files
- `GET /api/file/<filename>` - Get specific file data
- `GET /api/stats` - Get statistics

---

## Troubleshooting

**Port 5000 already in use?**
```bash
python app.py -p 5001
```

**Frontend not loading?**
- Check browser console for errors (F12)
- Ensure Flask is running (`python app.py`)
- Clear browser cache (Ctrl+Shift+Del)

**Scraping fails?**
- Verify URL is correct and accessible
- Check Chrome/ChromeDriver is installed
- Review the terminal output for error details

---

## Performance Tips

- One scrape typically takes 30-60 seconds
- Disable browser extensions that might block JustDial
- Don't close the terminal while scraping is running

---

Enjoy your data scraping! 🕷️
