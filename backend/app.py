import os
import threading
from flask import Flask, jsonify, request
from flask_cors import CORS
from deployer import run_deployment_thread
app = Flask(__name__)
CORS(app)
LOG_FILE = "/workspace/deployment.log"
STATUS_FILE = "/workspace/deployment.status"
@app.route('/api/deploy', methods=['POST'])
def deploy_app():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, 'r') as f:
            if f.read().strip() == 'running':
                return jsonify({"error": "A deployment is already in progress."}), 409
    data = request.json
    with open(LOG_FILE, 'w') as f: f.write("Deployment job received.\n")
    with open(STATUS_FILE, 'w') as f: f.write("running")
    deployment_thread = threading.Thread(target=run_deployment_thread, args=(data, LOG_FILE, STATUS_FILE))
    deployment_thread.start()
    return jsonify({"message": "Deployment job started!", "status": "running"}), 202
@app.route('/api/deploy/status', methods=['GET'])
def get_deployment_status():
    status = 'pending'
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, 'r') as f: status = f.read().strip()
    log_content = "Waiting for logs..."
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f: log_content = f.read()
    return jsonify({"status": status, "log": log_content})
if __name__ == '__main__':
    if not os.path.exists('/workspace'): os.makedirs('/workspace')
    with open(STATUS_FILE, 'w') as f: f.write("idle")
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)