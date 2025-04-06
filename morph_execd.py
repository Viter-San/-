import os
import subprocess
import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

LOG_FILE = "/opt/morph-execd/logs/exec.log"
TMP_SCRIPT = "/tmp/morph_exec.sh"

def log(entry):
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.datetime.now()}] {entry}\n")

@app.route("/exec", methods=["POST"])
def execute():
    data = request.get_json(force=True)
    command = data.get("cmd")
    if not command:
        return jsonify({"error": "Missing 'cmd' in JSON"}), 400

    log(f"CMD: {command}")
    
    try:
        with open(TMP_SCRIPT, "w") as f:
            f.write("#!/bin/bash\n")
            f.write(command + "\n")
        os.chmod(TMP_SCRIPT, 0o700)

        result = subprocess.run(
            ["/bin/bash", TMP_SCRIPT],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=20
        )

        log(f"OUT: {result.stdout}")
        log(f"ERR: {result.stderr}")
        return jsonify({
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode
        })

    except subprocess.TimeoutExpired:
        return jsonify({"error": "Execution timed out"}), 408
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/status", methods=["GET"])
def status():
    return jsonify({"status": "running", "time": str(datetime.datetime.now())})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)
