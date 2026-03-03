import os
import subprocess
import threading
from flask import Flask, jsonify, request, Response
from flask_cors import CORS

app = Flask(__name__, static_folder="../frontend", static_url_path="/")
CORS(app)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Keep track of running processes to prevent overlaps and allow streaming
active_processes = {}

COMMAND_MAP = {
    "sync_submissions": ["python", "scripts/sync_submissions.py"],
    "prepare_batch": ["python", "scripts/prepare_whydonate_batch.py"],
    "run_automater": ["python", "scripts/whydonate_batch_automater.py"],
    "reconcile_ledger": ["python", "scripts/whydonate_reconcile_all.py"],
    "generate_messages": ["python", "scripts/generate_onboarding_messages.py"],
    "monday_audit": ["python", "scripts/generate_monday_report.py"],
    "generate_seo_nodes": ["python", "scripts/generate_seo_nodes.py"],
    "generate_contextualizer": ["python", "scripts/run_contextualizer.py"],
    "generate_pulse_video": ["python", "scripts/generate_vortex_video.py"],
    "publish_nostr": ["python", "scripts/publish_to_nostr.py"],
    "publish_upscrolled": ["python", "scripts/publish_to_socials.py"],
    "generate_longform": ["python", "scripts/generate_longform_essay.py"],
    "publish_medium": ["python", "scripts/publish_to_medium.py"]
}

@app.route("/")
def index():
    return app.send_static_file("command_center.html")

@app.route("/api/run", methods=["POST"])
def run_command():
    data = request.json
    cmd_id = data.get("command_id")
    
    if cmd_id not in COMMAND_MAP:
        return jsonify({"error": "Unknown command"}), 400
        
    if cmd_id in active_processes and active_processes[cmd_id].poll() is None:
        return jsonify({"error": "Command already running"}), 409

    try:
        # Use shell=True for 'cmd' commands like start
        is_shell = COMMAND_MAP[cmd_id][0] == "cmd"
        
        process = subprocess.Popen(
            COMMAND_MAP[cmd_id], 
            cwd=BASE_DIR,
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            shell=is_shell
        )
        active_processes[cmd_id] = process
        
        return jsonify({"status": "started", "cmd_id": cmd_id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/stream/<cmd_id>")
def stream_output(cmd_id):
    def generate():
        process = active_processes.get(cmd_id)
        if not process:
            yield "data: Error: Process not found or not started.\n\n"
            return
            
        for line in iter(process.stdout.readline, ""):
            if line:
                # Yield SSE formatted data
                yield f"data: {line}\n\n"
        
        process.stdout.close()
        process.wait()
        yield f"data: [PROCESS_COMPLETE] Exit Code: {process.returncode}\n\n"
        
    return Response(generate(), mimetype="text/event-stream")

if __name__ == "__main__":
    print("==================================================")
    print("🚀 SOVEREIGN COMMAND CENTER STARTING 🚀")
    print("Serving on http://127.0.0.1:4040")
    print("==================================================")
    app.run(host="127.0.0.1", port=4040, threaded=True)
