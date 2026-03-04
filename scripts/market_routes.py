from flask import Blueprint, send_from_directory, current_app
import os

market_bp = Blueprint('market', __name__)

@market_bp.route('/data/<path:filename>')
def serve_data(filename):
    # Serve static files from the frontend/data directory
    data_dir = os.path.join(current_app.root_path, '..', 'frontend', 'data')
    return send_from_directory(data_dir, filename)
