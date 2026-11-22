import pytest
from fastapi.testclient import TestClient

from app import main

client = TestClient(main.app)


@pytest.fixture(autouse=True)
def reset_state():
    """Remet la liste de tâches à zéro avant chaque test."""
    main.tasks.clear()
    main.next_id = 1


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_tasks_empty():
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_create_task():
    response = client.post("/tasks", json={"title": "Apprendre Docker"})
    assert response.status_code == 201
    assert response.json() == {"id": 1, "title": "Apprendre Docker"}
    assert len(client.get("/tasks").json()) == 1


def test_delete_task():
    client.post("/tasks", json={"title": "A supprimer"})
    response = client.delete("/tasks/1")
    assert response.status_code == 204
    assert client.get("/tasks").json() == []


def test_delete_unknown_task():
    response = client.delete("/tasks/999")
    assert response.status_code == 404
