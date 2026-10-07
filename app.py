from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# This ensures the database and HTML files are read from the exact folder this script lives in
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, 'nexus_data.db')

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL,
            role TEXT NOT NULL,
            rating INTEGER NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# --- ROUTES TO SERVE YOUR WEBSITE ---
@app.route('/')
def home():
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/index.html')
def index():
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/news.html')
def news():
    return send_from_directory(BASE_DIR, 'news.html')

# --- DATA API ROUTES ---
@app.route('/api/collect', methods=['POST'])
def collect_data():
    try:
        data = request.get_json()
        required_fields = ['fullName', 'email', 'role', 'rating']
        if not all(field in data for field in required_fields):
            return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        timestamp = data.get('timestamp', datetime.now().isoformat())
        
        cursor.execute('''
            INSERT INTO user_data (full_name, email, role, rating, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (data['fullName'], data['email'], data['role'], int(data['rating']), timestamp))
        
        conn.commit()
        conn.close()
        return jsonify({'status': 'success', 'message': 'Data successfully recorded'}), 201

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/data', methods=['GET'])
def get_data():
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row 
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user_data ORDER BY id DESC')
        rows = cursor.fetchall()
        conn.close()
        
        result = [dict(row) for row in rows]
        return jsonify({'status': 'success', 'count': len(result), 'data': result}), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Initialize database on startup
init_db()

if __name__ == '__main__':
    app.run(debug=True, port=5000)