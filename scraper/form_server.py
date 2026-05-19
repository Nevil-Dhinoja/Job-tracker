from flask import Flask, send_from_directory
import os

app = Flask(__name__)
FORM_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route("/")
@app.route("/form")
def serve_form():
    return send_from_directory(FORM_DIR, "form.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=False)