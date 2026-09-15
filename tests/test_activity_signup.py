from abc import ABC, abstractmethod

from fastapi.testclient import TestClient

from src.app import app


class client(ABC):
    """A lightweight client with concrete helper methods for the abstract API."""

    @abstractmethod
    def fetch(self, method, path, params=None, json_body=None):
        """Send an HTTP request to the underlying service."""

    @abstractmethod
    def send(self, method, path, params=None, json_body=None):
        """Dispatch a request using the specific transport."""

    def get(self, path, params=None):
        return self.send("GET", path, params=params)

    def post(self, path, params=None, json_body=None):
        return self.send("POST", path, params=params, json_body=json_body)

    def delete(self, path, params=None):
        return self.send("DELETE", path, params=params)


class HttpClient(client):
    def __init__(self, base_url=""):
        self.base_url = base_url.rstrip("/")

    def fetch(self, method, path, params=None, json_body=None):
        if not path.startswith("/"):
            path = "/" + path
        url = f"{self.base_url}{path}"
        response = TestClient(app).request(method, url, params=params, json=json_body)
        return response

    def send(self, method, path, params=None, json_body=None):
        return self.fetch(method, path, params=params, json_body=json_body)


client = TestClient(app)


def test_unregister_participant_removes_email_from_activity():
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert
    assert response.status_code == 200

    payload = response.json()
    assert payload["message"] == f"Removed {email} from {activity_name}"

    activity = client.get("/activities").json()[activity_name]
    assert email not in activity["participants"]


def test_unregister_missing_participant_returns_404_or_400():
    # Arrange
    activity_name = "Chess Club"
    email = "not-signed-up@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert
    assert response.status_code in (404, 400)
