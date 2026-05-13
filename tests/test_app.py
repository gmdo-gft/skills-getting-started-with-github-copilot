"""Backend FastAPI tests using the AAA (Arrange-Act-Assert) pattern."""

import pytest
from src.app import activities


class TestRootRedirect:
    """Tests for the root endpoint."""
    
    def test_root_redirects_to_static_index(self, client):
        # Arrange
        expected_redirect_url = "/static/index.html"
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == expected_redirect_url


class TestGetActivities:
    """Tests for fetching all activities."""
    
    def test_get_activities_returns_all_activities(self, client, fresh_activities):
        # Arrange
        expected_activity_names = {"Chess Club", "Programming Class", "Gym Class"}
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert isinstance(data, dict)
        assert expected_activity_names.issubset(data.keys())
    
    def test_get_activities_includes_required_fields(self, client, fresh_activities):
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = client.get("/activities")
        data = response.json()
        first_activity = next(iter(data.values()))
        
        # Assert
        assert response.status_code == 200
        assert required_fields.issubset(first_activity.keys())


class TestSignupForActivity:
    """Tests for signing up for an activity."""
    
    def test_signup_successfully_adds_participant(self, client, fresh_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert email in activities[activity_name]["participants"]
    
    def test_signup_returns_error_for_nonexistent_activity(self, client):
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_signup_rejects_duplicate_registration(self, client, fresh_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]


class TestRemoveParticipant:
    """Tests for removing a participant from an activity."""
    
    def test_remove_participant_successfully(self, client, fresh_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]
        assert email not in activities[activity_name]["participants"]
    
    def test_remove_participant_returns_error_for_nonexistent_activity(self, client):
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_remove_participant_returns_error_for_nonexistent_participant(self, client, fresh_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "notparticipating@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Participant not found" in response.json()["detail"]
