from flask import Flask, request, jsonify
from scraper import scrape_job  # pyrefly: ignore[could-not-resolve-import]
from datetime import datetime
import gspread
# pyrefly: ignore [missing-import]
from submit import process_job
from google.oauth2.service_account import Credentials
import os

app = Flask(__name__)

# ── Google Sheets setup ──────────────────────────────────────────────────────
CREDS_PATH = os.path.join(os.path.dirname(__file__), "..", "credentials", "credentials.json")
SHEET_NAME = "Job Tracker"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_sheet():
    creds = Credentials.from_service_account_file(CREDS_PATH, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open(SHEET_NAME).sheet1


# ── Routes ───────────────────────────────────────────────────────────────────

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/scrape", methods=["POST"])
def scrape():
    """
    Called by n8n HTTP Request node.
    Accepts: { "url": "...", "company": "...", "role": "...", ... } (all optional except url)
    Returns scraped + merged data.
    """
    data = request.get_json(force=True)
    url = data.get("url", "").strip()

    if not url:
        return jsonify({"error": "url is required"}), 400

    # If fields are already provided manually, use them; else scrape
    scraped = scrape_job(url)

    result = {
        "company":  data.get("company")  or scraped.get("company")  or "Unknown",
        "role":     data.get("role")     or scraped.get("role")     or "Unknown",
        "salary":   data.get("salary")   or scraped.get("salary")   or "Not mentioned",
        "deadline": data.get("deadline") or scraped.get("deadline") or "Not mentioned",
        "url": url,
        "status": "pending",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "scrape_error": scraped.get("error")
    }

    return jsonify(result)


@app.route("/append", methods=["POST"])
def append_row():
    """
    Backup route — n8n Google Sheets node handles this,
    but this works too if you want pure Python flow.
    """
    data = request.get_json(force=True)
    try:
        sheet = get_sheet()
        row = [
            data.get("company", ""),
            data.get("role", ""),
            data.get("salary", ""),
            data.get("deadline", ""),
            data.get("url", ""),
            data.get("status", "pending"),
            data.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        ]
        sheet.append_row(row)
        return jsonify({"success": True, "row": row})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/trigger", methods=["POST"])
def trigger_selenium():
    """
    Called by n8n after appending to Google Sheets.
    Kicks off Selenium to fill the demo form.
    """
    data = request.get_json(force=True)

    required = ["company", "role", "url"]
    for field in required:
        if not data.get(field):
            return jsonify({"error": f"Missing field: {field}"}), 400

    result = process_job(data)

    if result.get("success"):
        return jsonify({"status": "done", "screenshot": result["screenshot"]})
    else:
        return jsonify({"status": "failed", "error": result.get("error")}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)