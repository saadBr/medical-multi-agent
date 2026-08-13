from uuid import UUID

from fastapi.testclient import TestClient

from backend.app.api import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_start_session_returns_valid_uuid():
    response = client.post("/sessions/start")

    assert response.status_code == 200
    UUID(response.json()["thread_id"])


def test_unknown_session_is_rejected():
    response = client.post(
        "/consultation/start",
        json={
            "thread_id": "unknown-session",
            "initial_case": "The patient reports a mild headache.",
        },
    )

    assert response.status_code == 404


def test_consultation_starts_with_first_question():
    session_response = client.post("/sessions/start")
    thread_id = session_response.json()["thread_id"]

    response = client.post(
        "/consultation/start",
        json={
            "thread_id": thread_id,
            "initial_case": (
                "The patient reports cough and fever for two days."
            ),
        },
    )

    data = response.json()

    assert response.status_code == 200
    assert data["status"] == "waiting_for_patient"
    assert data["pending_interrupt"]["type"] == "patient_question"
    assert data["pending_interrupt"]["question"] == (
        "When did your symptoms begin?"
    )