"""
2026 Summer Study Plan — Sync Server
Flask app serving HTML + /api/summer2026 JSON persistence.
Deploy anywhere: Render, PythonAnywhere, Fly.io, etc.
"""
import os
import json
import time
import threading
from flask import Flask, request, jsonify, send_from_directory

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data.json')
STATIC_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path='')

# ── Thread-safe data access ──────────────────────────────────
_data_lock = threading.Lock()

def load_data():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {'tasks': [], 'version': 0, 'updated': 0}

def save_data(data):
    with _data_lock:
        data['updated'] = int(time.time() * 1000)
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)

# ── Routes ───────────────────────────────────────────────────

@app.route('/')
def index():
    """Serve the study plan HTML."""
    return send_from_directory(STATIC_DIR, 'index.html')

@app.route('/api/summer2026', methods=['GET', 'POST'])
def api_summer():
    if request.method == 'GET':
        return jsonify(load_data())
    elif request.method == 'POST':
        body = request.get_json(force=True)
        if not body or 'tasks' not in body:
            return jsonify({'error': 'Missing "tasks" field'}), 400
        tasks = body.get('tasks', [])
        if not isinstance(tasks, list):
            return jsonify({'error': '"tasks" must be an array'}), 400
        version = body.get('version', int(time.time() * 1000))
        data = {'tasks': tasks, 'version': version}
        save_data(data)
        return jsonify(data)

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'ts': int(time.time())})

# ── Main ─────────────────────────────────────────────────────

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 9998))
    app.run(host='0.0.0.0', port=port, debug=False)
