# 🚀 NASA Space Data Explorer

A modern, interactive web dashboard for exploring live NASA space data — including the Astronomy Picture of the Day (APOD) and Near-Earth Asteroid tracking.

![Dashboard Preview](https://img.shields.io/badge/NASA-API-blue?style=flat&logo=nasa)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python)
![Flask](https://img.shields.io/badge/Flask-2.0+-000000?style=flat&logo=flask)

---

## ✨ Features

- **🌌 Astronomy Picture of the Day (APOD)** — Browse daily space imagery with full explanations, date picker, and video support
- **☄️ Near-Earth Asteroid Tracker** — Live asteroid data with sorting, filtering, and search
- **📊 Real-time Dashboard** — Stat cards, hazard distribution chart, and highlight rankings
- **🎨 Dark Space Theme** — Modern, responsive UI optimized for all screen sizes
- **⚡ REST API Backend** — Clean Flask API with structured JSON responses and error handling

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python, Flask, Pandas |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Data Source | [NASA Open APIs](https://api.nasa.gov) |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- A NASA API key (optional — `DEMO_KEY` works for testing)

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/nasa-space-data-explorer.git
cd nasa-space-data-explorer
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. (Optional) Set your NASA API key

```bash
# Linux/macOS
export NASA_API_KEY="your_api_key_here"

# Windows (PowerShell)
$env:NASA_API_KEY="your_api_key_here"
```

Get your free API key at [api.nasa.gov](https://api.nasa.gov).

### 4. Run the backend

```bash
python app.py
```

The API will start at `http://localhost:5000`.

### 5. Open the frontend

Simply open `index.html` in your browser, or serve it via any static file server.

---

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/apod` | GET | Astronomy Picture of the Day |
| `/api/apod?date=YYYY-MM-DD` | GET | APOD for a specific date |
| `/api/asteroids` | GET | Near-Earth Asteroids (default: today + 2 days) |
| `/api/asteroids?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD` | GET | Asteroids for a date range |
| `/api/asteroids/stats` | GET | Computed statistics for asteroids |

---

## 📁 Project Structure

```
nasa-space-data-explorer/
├── app.py              # Flask REST API backend
├── index.html          # Single-page frontend
├── style.css           # Dark space theme styling
├── app.js              # Frontend logic & interactivity
├── requirements.txt    # Python dependencies
├── .gitignore          # Git ignore rules
└── README.md           # Project documentation
```

---

## 🖼️ Screenshots

### Dashboard
Live stat cards, hazard distribution donut chart, and recent asteroid table.

### APOD Viewer
Browse any date's Astronomy Picture with full media support (images & videos).

### Asteroid Table
Sortable, filterable, and searchable near-Earth object data.

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

---

## 📜 License

This project is open source and available under the [MIT License](LICENSE).

---

> **Disclaimer:** This project uses NASA's public APIs. Data is provided by NASA and is subject to their terms of use.
