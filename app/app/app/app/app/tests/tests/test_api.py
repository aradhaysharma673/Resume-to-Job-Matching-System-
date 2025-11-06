from fastapi.testclient import TestClient
from app.main import app
import io

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["total_matches_processed"] >= 0

def test_match_text():
    response = client.post(
        "/match-text",
        data={
            "resume_text": "Python developer with 3 years experience in Django, FastAPI, and machine learning. Skilled in Docker and AWS." * 5,
            "job_title": "Python Developer",
            "job_description": "Looking for a Python developer with experience in FastAPI and cloud deployment",
            "required_skills": "Python, FastAPI, Docker, AWS"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "match_score" in data
    assert data["match_score"] >= 0
    assert data["match_score"] <= 100

def test_match_text_too_short():
    response = client.post(
        "/match-text",
        data={
            "resume_text": "Short resume",
            "job_title": "Developer",
            "job_description": "We need a developer",
            "required_skills": "Python"
        }
    )
    assert response.status_code == 422  # Validation error
