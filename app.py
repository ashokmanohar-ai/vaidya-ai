"""Synthetic-only VAIDYA AI Flask starter; no clinical processing or model calls."""
from __future__ import annotations

import os
from flask import Flask, jsonify, render_template

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 4 * 1024 * 1024


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/health/live")
def live():
    return jsonify(service="vaidya-ai", status="ok")


@app.get("/health/ready")
def ready():
    # Only the starter's web process is ready. No database, AI, or worker checks yet.
    return jsonify(service="vaidya-ai", status="foundation_only", clinical_ready=False)


@app.get("/api/v1/status")
def status():
    return jsonify(
        name="Vaidya AI",
        environment="synthetic_demo",
        clinical_ready=False,
        features={
            "flask_web": True,
            "langgraph": False,
            "bedrock": False,
            "authentication": False,
            "patient_processing": False,
            "report_generation": False,
            "learning": False,
        },
    )


@app.after_request
def secure_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; script-src 'self'; frame-ancestors 'none'"
    )
    return response


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "8080")), debug=False)
