# 🚀 NASA Space Data Explorer

A full-stack Flask web dashboard for exploring live NASA data, including **Astronomy Picture of the Day (APOD)** and **Near-Earth Objects (NEOs)**.

## Features

- 🌌 APOD viewer with date selection and image/video support
- ☄️ Near-Earth asteroid tracker using NASA's NEO Feed API
- 📊 Dashboard statistics: total, hazardous, safe, average velocity
- 🔎 Search, hazard filtering, date filtering and sortable asteroid table
- 🟢 API health indicator
- 📱 Responsive dark-space UI
- 🔐 NASA API key configured through environment variables
- 🚀 Ready for GitHub + Render deployment

## Tech Stack

- Python 3
- Flask
- Flask-CORS
- Pandas
- Requests
- Gunicorn
- HTML/CSS/Vanilla JavaScript
- NASA Open APIs

## Project Structure

```text
nasa-space-data-explorer/
├── app.py
├── requirements.txt
├── Procfile
├── render.yaml
├── .env.example
├── .gitignore
├── LICENSE
├── README.md
└── static/
    ├── index.html
    ├── style.css
    └── app.js
```

## Run Locally

### 1. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv venv
.env\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure NASA API key

Copy `.env.example` to `.env` if you want to keep local configuration separately.

For PowerShell:

```powershell
$env:NASA_API_KEY="YOUR_NASA_API_KEY"
```

For macOS/Linux:

```bash
export NASA_API_KEY="YOUR_NASA_API_KEY"
```

`DEMO_KEY` is used automatically if `NASA_API_KEY` is not set, but NASA's demo key has stricter rate limits.

### 4. Start the server

```bash
python app.py
```

Open:

```text
http://localhost:5000
```

## Render Deployment

### Option A — Blueprint

1. Push this project to GitHub.
2. In Render, choose **New → Blueprint**.
3. Connect your GitHub repository.
4. Render will read `render.yaml`.
5. Add your `NASA_API_KEY` as a secret/environment variable if you have a personal NASA key.
6. Deploy.

### Option B — Web Service

Use:

- **Runtime:** Python
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn app:app`

Add environment variable:

```text
NASA_API_KEY=YOUR_NASA_API_KEY
```

## API Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/health` | GET | API health |
| `/api/apod` | GET | Today's APOD |
| `/api/apod?date=YYYY-MM-DD` | GET | APOD for a selected date |
| `/api/asteroids` | GET | NEOs for the default date range |
| `/api/asteroids?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD` | GET | NEOs for a selected range |
| `/api/asteroids/stats` | GET | Calculated asteroid statistics |

## Notes

- The backend proxies NASA API requests so the browser does not need the NASA API key.
- Never commit a real API key to GitHub.
- The included `.gitignore` excludes `.env` and Python build/cache files.
- NASA API availability and rate limits can affect live data.

## License

MIT License. See `LICENSE`.

## Data Source

NASA Open APIs: https://api.nasa.gov/
