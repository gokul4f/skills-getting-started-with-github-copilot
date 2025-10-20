from fastapi.testclient import TestClient
import pytest

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    # Make a shallow copy of participants so tests can modify and be isolated
    backup = {k: v.copy() for k, v in activities.items()}
    # Ensure participants lists are copied as well
    for k in backup:
        backup[k]["participants"] = list(activities[k]["participants"])
    yield
    activities.clear()
    activities.update(backup)


def test_get_activities():
    client = TestClient(app)
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # At least one known activity exists
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    client = TestClient(app)
    email = "teststudent@example.com"
    activity_name = "Chess Club"

    # Ensure not present initially
    assert email not in activities[activity_name]["participants"]

    # Sign up
    signup_resp = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert signup_resp.status_code == 200
    assert "Signed up" in signup_resp.json().get("message", "")
    assert email in activities[activity_name]["participants"]

    # Signing up again should return 400
    resp_again = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert resp_again.status_code == 400

    # Unregister
    delete_resp = client.delete(f"/activities/{activity_name}/participants?email={email}")
    assert delete_resp.status_code == 200
    assert email not in activities[activity_name]["participants"]

    # Unregistering again should return 404
    del_again = client.delete(f"/activities/{activity_name}/participants?email={email}")
    assert del_again.status_code == 404
