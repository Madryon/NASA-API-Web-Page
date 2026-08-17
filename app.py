"""
NASA Space Data Explorer - Flask Backend API
"""

import os
import mimetypes
import requests
import pandas as pd
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, Response

app = Flask(__name__)
from flask_cors import CORS
CORS(app)

# Configuration
API_KEY = os.environ.get("NASA_API_KEY", "DEMO_KEY")
BASE_URL = "https://api.nasa.gov"

# Absolute path to project folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ================================================================
# DEBUG: List files on startup
# ================================================================
print("=" * 50)
print(f"BASE_DIR: {BASE_DIR}")
print(f"Files in directory: {os.listdir(BASE_DIR)}")
print("=" * 50)


# ================================================================
# STATIC FILES (Explicit - no catch-all conflicts)
# ================================================================

def serve_file(filename, mime_type):
    """Read and serve a file with correct MIME type."""
    file_path = os.path.join(BASE_DIR, filename)
    print(f"Serving: {file_path} (exists: {os.path.exists(file_path)})")
    
    if not os.path.exists(file_path):
        return f"File not found: {filename}. Available: {os.listdir(BASE_DIR)}", 404
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return Response(content, mimetype=mime_type)


@app.route('/')
def index():
    return serve_file('index.html', 'text/html')

@app.route('/style.css')
def serve_css():
    return serve_file('style.css', 'text/css')

@app.route('/app.js')
def serve_js():
    return serve_file('app.js', 'application/javascript')

@app.route('/favicon.ico')
def favicon():
    return '', 204


# ================================================================
# API ROUTES
# ================================================================

@app.route("/api/health", methods=["GET"])
def health_check():
    files = os.listdir(BASE_DIR)
    return jsonify({
        "status": "healthy",
        "files_in_directory": files,
        "base_dir": BASE_DIR,
        "timestamp": datetime.utcnow().isoformat()
    })


@app.route("/api/apod", methods=["GET"])
def get_apod():
    date = request.args.get("date", None)
    url = f"{BASE_URL}/planetary/apod"
    params = {"api_key": API_KEY}
    if date:
        params["date"] = date
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        return jsonify({
            "success": True,
            "data": {
                "date": data.get("date"),
                "title": data.get("title"),
                "explanation": data.get("explanation"),
                "media_type": data.get("media_type"),
                "url": data.get("url"),
                "hdurl": data.get("hdurl"),
                "copyright": data.get("copyright", "NASA")
            }
        })
    except requests.exceptions.Timeout:
        return jsonify({"success": False, "error": "NASA server timeout"}), 504
    except requests.exceptions.ConnectionError:
        return jsonify({"success": False, "error": "Could not connect to NASA"}), 503
    except requests.exceptions.HTTPError as e:
        return jsonify({"success": False, "error": str(e)}), 502
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/asteroids", methods=["GET"])
def get_asteroids():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    
    if not start_date:
        today = datetime.utcnow().date()
        start_date = str(today)
        end_date = str(today + timedelta(days=2))
    
    url = f"{BASE_URL}/neo/rest/v1/feed"
    params = {
        "start_date": start_date,
        "end_date": end_date,
        "api_key": API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        asteroid_list = []
        neo_data = data.get("near_earth_objects", {})
        
        for date_str, asteroids in neo_data.items():
            for asteroid in asteroids:
                approach_data = asteroid.get("close_approach_data", [])
                if not approach_data:
                    continue
                
                approach = approach_data[0]
                
                diameter_km = asteroid.get("estimated_diameter", {}).get("kilometers", {})
                min_dia = diameter_km.get("estimated_diameter_min", 0)
                max_dia = diameter_km.get("estimated_diameter_max", 0)
                
                velocity = float(approach.get("relative_velocity", {}).get("kilometers_per_second", 0))
                distance = float(approach.get("miss_distance", {}).get("kilometers", 0))
                
                asteroid_list.append({
                    "id": asteroid.get("id"),
                    "name": asteroid.get("name", "Unknown"),
                    "date": date_str,
                    "hazardous": asteroid.get("is_potentially_hazardous_asteroid", False),
                    "min_diameter_km": round(min_dia, 4),
                    "max_diameter_km": round(max_dia, 4),
                    "velocity_km_s": round(velocity, 2),
                    "distance_km": round(distance, 0),
                    "orbiting_body": approach.get("orbiting_body", "Earth"),
                    "approach_time": approach.get("close_approach_date_full", "")
                })
        
        return jsonify({
            "success": True,
            "count": len(asteroid_list),
            "date_range": {"start": start_date, "end": end_date},
            "data": asteroid_list
        })
    except requests.exceptions.Timeout:
        return jsonify({"success": False, "error": "NASA server timeout"}), 504
    except requests.exceptions.ConnectionError:
        return jsonify({"success": False, "error": "Could not connect to NASA"}), 503
    except requests.exceptions.HTTPError as e:
        return jsonify({"success": False, "error": str(e)}), 502
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/asteroids/stats", methods=["GET"])
def get_asteroid_stats():
    result = get_asteroids()
    data = result.get_json()
    
    if not data.get("success"):
        return jsonify(data), result.status_code
    
    asteroids = data["data"]
    df = pd.DataFrame(asteroids)
    
    if df.empty:
        return jsonify({"success": True, "stats": None})
    
    total = len(df)
    hazardous_count = int(df["hazardous"].sum())
    safe_count = total - hazardous_count
    
    fastest = df.loc[df["velocity_km_s"].idxmax()]
    closest = df.loc[df["distance_km"].idxmin()]
    largest = df.loc[df["max_diameter_km"].idxmax()]
    
    stats = {
        "total": total,
        "hazardous_count": hazardous_count,
        "safe_count": safe_count,
        "hazardous_percentage": round((hazardous_count / total) * 100, 1),
        "fastest": {
            "name": fastest["name"],
            "speed_km_s": fastest["velocity_km_s"]
        },
        "closest": {
            "name": closest["name"],
            "distance_km": closest["distance_km"]
        },
        "largest": {
            "name": largest["name"],
            "diameter_km": largest["max_diameter_km"]
        },
        "avg_velocity": round(df["velocity_km_s"].mean(), 2),
        "avg_distance": round(df["distance_km"].mean(), 0)
    }
    
    return jsonify({"success": True, "stats": stats})


# ================================================================
# RUN SERVER
# ================================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("🚀 NASA Space Data Explorer API starting...")
    app.run(host="0.0.0.0", port=port, debug=False)
