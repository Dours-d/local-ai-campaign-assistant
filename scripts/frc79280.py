import os
import json
import requests
import secure_filename
from flask import Flask, request, jsonify, render_template
from functools import wraps
from datetime import datetime
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

UPLOAD_FOLDER = app.config['UPLOAD_FOLDER']
DATA_DIR = app.config['DATA_DIR']
DATA_DIR = os.path.join(app.root_path, DATA_DIR)
DATA_DIR = os.path.abspath(DATA_DIR)
os.makedirs(DATA_DIR, exist_ok=True)

# Database (in-memory for simplicity - replace with a real database in production)
# In real production, this would be a database like PostgreSQL, MySQL, or MongoDB.
# For this example, we'll store data in JSON files.
# Each beneficiary_id will have a corresponding JSON file.
# Example file structure:  /data/{beneficiary_id}_submission.json

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_admin():
            return jsonify({'error': 'Unauthorized'}), 403
        return f(*args, **kwargs)
    return decorated_function

def is_admin():
    # Replace this with your actual admin authentication logic
    # e.g., check for a specific role or user in a database
    return True  # For demonstration purposes, always return True

def secure_filename(filename):
    # Sanitize filename to prevent directory traversal attacks
    return os.path.basename(filename)

def check_for_blood(filepath):
    # Placeholder function - replace with your actual blood density detection logic
    # This is a dummy function to demonstrate file handling
    # in a real application, you would use a medical image processing library
    # to analyze the image and determine the blood density.

    # Simulate blood density
    blood_density = "2.5"

    # Simulate blood detection flag
    is_flagged = False
    return is_flagged, blood_density

# Helper function to determine if a beneficiary ID is in scope
def is_in_scope(id):
    # Replace this with your actual scope checking logic
    # For demonstration purposes, we'll check if the ID starts with "viral_"
    return id.startswith('viral_')


# Utility functions (can be moved to a separate module)
def load_submission_data(beneficiary_id):
    json_path = os.path.join(DATA_DIR, f"{beneficiary_id}_submission.json")
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def save_submission_data(beneficiary_id, data):
    json_path = os.path.join(DATA_DIR, f"{beneficiary_id}_submission.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


# Sample routes (implement your actual API endpoints here)
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/submission', methods=['POST'])
def api_submission():
    beneficiary_id = request.form.get('beneficiary_id', 'unknown')
    whatsapp_number = request.form.get('whatsapp_number', '')
    title = request.form.get('title', '')
    story = request.form.get('story', '')
    display_name = request.form.get('display_name', '')
    personal_wallet = request.form.get('personal_wallet', '')
    files = request.files.getlist('files')

    submission_data = {
        'beneficiary_id': beneficiary_id,
        'whatsapp_number': whatsapp_number,
        'title': title,
        'story': story,
        'display_name': display_name,
        'personal_wallet': personal_wallet,
        'files': [],
        'timestamp': datetime.now().isoformat()
    }

    for file in files:
        if file.filename:
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            submission_data['files'].append({
                'path': file_path,
                'is_flagged': False,
                'blood_density': '0.0'
            })

    save_submission_data(beneficiary_id, submission_data)
    return jsonify({'status': 'success'}), 201  # Return 201 Created

@app.route('/api/translate', methods=['POST'])
def api_translate():
    data = request.get_json() or {}
    text = data.get('text', '').strip()
    mode = data.get('mode', 'title')

    if not text:
        return jsonify({'error': 'No text provided'}), 400

    translation = translate_arabic(text, mode)
    return jsonify({'translation': translation, 'detected': 'ar' if any('\u0600' <= char <= '\u06FF' for char in text) else 'en'})

def translate_arabic(text, mode):
    # This is a placeholder function - replace with your actual translation logic
    if mode == 'title':
        return "Arabic Title"
    else:
        return "Arabic Text"


# Example route for uploading files
@app.route('/upload', methods=['POST'])
def upload_route():
    beneficiary_id = request.form.get('beneficiary_id', 'unknown')
    whatsapp_number = request.form.get('whatsapp_number', '')
    
    is_id_known = is_in_scope(beneficiary_id) if beneficiary_id else (not beneficiary_id.isdigit() and beneficiary_id not in ['unknown', 'onboard', 'index.html', ''])
    is_wa_known = is_in_scope(whatsapp_number) if whatsapp_number else False

    if not is_id_known and not is_wa_known:
        return jsonify({"error": "Out of Scope"}), 403
        
    if beneficiary_id in ['unknown', 'onboard', 'index.html', '']:
        if whatsapp_number:
            beneficiary_id = f"viral_{whatsapp_number}"
        else:
            return jsonify({"error": "Missing WhatsApp"}), 400
    
    submission_data = {
        "beneficiary_id": beneficiary_id,
        "whatsapp_number": whatsapp_number,
        "title": request.form.get('title', ''),
        "story": request.form.get('story', ''),
        "display_name": request.form.get('display_name', ''),
        "personal_wallet": request.form.get('personal_wallet', ''),
        "files": [],
        "timestamp": datetime.now().isoformat()
    }
    
    files = request.files.getlist('files')
    beneficiary_folder = os.path.join(app.config['UPLOAD_FOLDER'], beneficiary_id)
    os.makedirs(beneficiary_folder, exist_ok=True)
    
    for file in files:
        if file.filename:
            filename = secure_filename(file.filename)
            file_path = os.path.join(beneficiary_folder, filename)
            file.save(file_path)
            
            is_flagged, blood_density = check_for_blood(file_path)
            submission_data["files"].append({
                "path": file_path,
                "is_flagged": bool(is_flagged),
                "blood_density": float(blood_density)
            })
            
    os.makedirs(DATA_DIR, exist_ok=True)
    json_path = os.path.join(DATA_DIR, f"{beneficiary_id}_submission.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(submission_data, f, indent=2)
        
    return jsonify({"status": "success"}), 200


if __name__ == '__main__':
    app.run(debug=True)
