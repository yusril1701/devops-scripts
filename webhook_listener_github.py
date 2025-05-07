from flask import Flask, request
import subprocess
import hmac
import hashlib

app = Flask(__name__)

SECRET = b'2f43de3f51e76b93f88a5ab7c37b7b84d1e726bcbbf934f1ae64a9b412874b02'

APP_REPOS = {
    "app1": "/app/sindimawa"
}

@app.route("/<app_name>", methods=["POST"])
def webhook(app_name):
    # Validasi apakah app_name dikenal
    if app_name not in APP_REPOS:
        return f"Unknown app: {app_name}", 404

    # Ambil signature dari header
    signature = request.headers.get('X-Hub-Signature-256')
    if not signature:
        return "Missing signature", 403

    # Validasi format signature
    try:
        sha_name, signature = signature.split('=')
        if sha_name != 'sha256':
            return "Unsupported signature method", 400
    except ValueError:
        return "Invalid signature format", 400

    # Validasi signature menggunakan HMAC
    mac = hmac.new(SECRET, msg=request.data, digestmod=hashlib.sha256)
    if not hmac.compare_digest(mac.hexdigest(), signature):
        return "Invalid signature", 403

    # Jalankan git pull untuk direktori aplikasi yang sesuai
    repo_path = APP_REPOS[app_name]
    try:
        subprocess.run(["git", "-C", repo_path, "pull", "origin", "main"], check=True)
        return f"Pulled latest code for {app_name}", 200
    except subprocess.CalledProcessError as e:
        return f"Failed to pull for {app_name}: {str(e)}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001)
