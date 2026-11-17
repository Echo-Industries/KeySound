"""
BeatPad Keyboard Soundboard - Flask Web Server
Serves the interactive HTML/Tone.js soundboard frontend and provides
optional JSON API endpoints for saving and loading recorded beat loops.
"""

import json
import os
from datetime import datetime
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

# Path to local JSON file for persisting saved loop presets
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOOPS_FILE = os.path.join(BASE_DIR, "loops.json")


def read_saved_loops():
    """Safely reads saved beat loops from disk."""
    if not os.path.exists(LOOPS_FILE):
        return []
    try:
        with open(LOOPS_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError):
        return []


def write_saved_loops(loops):
    """Writes the list of beat loops to disk in formatted JSON."""
    with open(LOOPS_FILE, "w", encoding="utf-8") as file:
        json.dump(loops, file, indent=2)


@app.route("/")
def index():
    """Renders the main BeatPad soundboard interface."""
    return render_template("index.html")


@app.route("/api/loops", methods=["GET"])
def get_loops():
    """Returns all saved loop presets."""
    try:
        loops = read_saved_loops()
        return jsonify({"status": "ok", "loops": loops}), 200
    except Exception as exc:
        return jsonify({"status": "error", "message": str(exc)}), 500


@app.route("/api/loops", methods=["POST"])
def save_loop():
    """Saves a new recorded loop preset to loops.json."""
    try:
        payload = request.get_json(silent=True) or {}
        events = payload.get("events", [])
        duration = payload.get("duration", 0)
        bpm = payload.get("bpm", 110)

        if not events or duration <= 0:
            return jsonify({"status": "error", "message": "No loop events to save."}), 400

        loops = read_saved_loops()
        preset_number = len(loops) + 1
        new_loop = {
            "id": int(datetime.now().timestamp() * 1000),
            "name": payload.get("name") or f"Beat #{preset_number} ({bpm} BPM)",
            "bpm": bpm,
            "duration": duration,
            "events": events,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }

        loops.append(new_loop)
        write_saved_loops(loops)
        return jsonify({"status": "ok", "loop": new_loop}), 201
    except Exception as exc:
        return jsonify({"status": "error", "message": str(exc)}), 500


@app.route("/api/loops/<int:loop_id>", methods=["DELETE"])
def delete_loop(loop_id):
    """Deletes a saved loop preset by ID."""
    try:
        loops = read_saved_loops()
        updated = [item for item in loops if item.get("id") != loop_id]
        write_saved_loops(updated)
        return jsonify({"status": "ok"}), 200
    except Exception as exc:
        return jsonify({"status": "error", "message": str(exc)}), 500


if __name__ == "__main__":
    # Start the local development server on http://127.0.0.1:5000
    app.run(host="127.0.0.1", port=5000, debug=True)