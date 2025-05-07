from flask import Flask, request
import subprocess
import hmac
import hashlib

app = Flask(__name__)

# Secret token dari GitHub
SECRET = b'your-secret-token'

# Mapping nama app ke direktori lokal
APP_REPOS = {
    "app1": "/app/repos/app1",
    "app2": "/app/repos/app2",
    # Tambahkan lebih banyak aplikasi di sini
}

@app.route("/webhook/<app_name>", methods=["POST"])
def webhook(app_name):
    if app_name not in APP_REPOS:
        return f"Unknown app: {app_name}", 404

    signature = request.headers.get('X-Hub-Signature-256')
    if signature is None:
        return "No signature", 403

    try:
        sha_name, signature = signature.split('=')
    except ValueError:
        return "Invalid signature format", 400

    mac = hmac.new(SECRET, msg=request.data, digestmod=hashlib.sha256)
    if not hmac.compare_digest(mac.hexdigest(), signature):
        return "Invalid signature", 403

    repo_path = APP_REPOS[app_name]
    subprocess.Popen(["git", "-C", repo_path, "pull", "origin", "main"])
    return f"Triggered git pull for {app_name}", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001)
