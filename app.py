"""
NASA Space Data Explorer - Flask Backend API
Updated with REST endpoints, CORS, static file serving, and Render support
"""

import os
import mimetypes
import requests
import pandas as pd
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, send_from_directory, Response

app = Flask(__name__)

# CORS
from flask_cors import CORS
CORS(app)

# Configuration
API_KEY = os.environ.get("NASA_API_KEY", "DEMO_KEY")
BASE_URL = "https://api.nasa.gov"

# Get the directory where app.py lives
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# ================================================================
# STATIC FILES (Serve frontend with correct MIME types)
# ================================================================

@app.route('/')
def index():
    return send_from_directory(BASE_DIR, 'index.html', mimetype='text/html')

@app.route('/style.css')
def serve_css():
    return send_from_directory(BASE_DIR, 'style.css', mimetype='text/css')

@app.route('/app.js')
def serve_js():
    return send_from_directory(BASE_DIR, 'app.js', mimetype='application/javascript')

@app.route('/<path:filename>')
def static_files(filename):
    # Guess the correct MIME type
    mime_type, _ = mimetypes.guess_type(filename)
    if mime_type is None:
        mime_type = 'application/octet-stream'
    return send_from_directory(BASE_DIR, filename, mimetype=mime_type)


# ================================================================
# API ROUTES
# ================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "NASA Space Data Explorer API"
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
    print("📡 Endpoints:")
    print("   GET /")
    print("   GET /style.css")
    print("   GET /app.js")
    print("   GET /api/health")
    print("   GET /api/apod")
    print("   GET /api/asteroids")
    print("   GET /api/asteroids/stats")
    app.run(host="0.0.0.0", port=port, debug=False)
