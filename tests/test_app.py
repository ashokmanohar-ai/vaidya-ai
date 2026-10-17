"""Smoke tests for the synthetic-only Flask starter."""
from app import app


def test_home():
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert b"Development only" in response.data


def test_health():
    client = app.test_client()
    assert client.get("/health/live").json["status"] == "ok"
    ready = client.get("/health/ready").json
    assert ready["clinical_ready"] is False


def test_no_patient_processing_endpoint():
    client = app.test_client()
    assert client.post("/api/v1/report-jobs").status_code == 404


def test_security_headers():
    response = app.test_client().get("/")
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
