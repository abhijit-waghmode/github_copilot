"""Tests for the FastAPI activities application."""

import pytest


class TestGetActivities:
    """Test suite for the GET /activities endpoint."""

    def test_get_activities_returns_200(self, client):
        """Test that getting activities returns a 200 status code."""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self, client):
        """Test that getting activities returns a dictionary."""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)

    def test_get_activities_has_expected_activities(self, client):
        """Test that all expected activities are present."""
        response = client.get("/activities")
        activities = response.json()
        
        expected_activities = [
            "Basketball", "Tennis Club", "Drama Club", "Visual Arts",
            "Debate Team", "Science Club", "Chess Club", "Programming Class",
            "Gym Class"
        ]
        
        for activity in expected_activities:
            assert activity in activities

    def test_activity_has_required_fields(self, client):
        """Test that each activity has required fields."""
        response = client.get("/activities")
        activities = response.json()
        
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        for activity_name, activity_data in activities.items():
            for field in required_fields:
                assert field in activity_data, f"Activity {activity_name} missing field {field}"

    def test_participants_is_list(self, client):
        """Test that participants field is a list."""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["participants"], list)


class TestSignupForActivity:
    """Test suite for the POST /activities/{activity_name}/signup endpoint."""

    def test_signup_for_activity_success(self, client, reset_activities):
        """Test successful signup for an activity."""
        response = client.post(
            "/activities/Basketball/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]

    def test_signup_adds_participant(self, client, reset_activities):
        """Test that signup adds the participant to the activity."""
        email = "newstudent@mergington.edu"
        client.post(
            "/activities/Basketball/signup",
            params={"email": email}
        )
        
        response = client.get("/activities")
        activities = response.json()
        
        assert email in activities["Basketball"]["participants"]

    def test_signup_for_nonexistent_activity(self, client, reset_activities):
        """Test signup for an activity that doesn't exist."""
        response = client.post(
            "/activities/NonExistent/signup",
            params={"email": "student@mergington.edu"}
        )
        
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_duplicate_email(self, client, reset_activities):
        """Test that duplicate signup is rejected."""
        email = "alex@mergington.edu"  # Already signed up for Basketball
        response = client.post(
            "/activities/Basketball/signup",
            params={"email": email}
        )
        
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_different_activity(self, client, reset_activities):
        """Test that same student can sign up for different activities."""
        email = "alex@mergington.edu"
        response = client.post(
            "/activities/Tennis Club/signup",
            params={"email": email}
        )
        
        assert response.status_code == 200

    def test_signup_multiple_students(self, client, reset_activities):
        """Test that multiple students can sign up for the same activity."""
        response1 = client.post(
            "/activities/Basketball/signup",
            params={"email": "student1@mergington.edu"}
        )
        response2 = client.post(
            "/activities/Basketball/signup",
            params={"email": "student2@mergington.edu"}
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Verify both are added
        response = client.get("/activities")
        activities = response.json()
        assert "student1@mergington.edu" in activities["Basketball"]["participants"]
        assert "student2@mergington.edu" in activities["Basketball"]["participants"]


class TestUnregisterFromActivity:
    """Test suite for the POST /activities/{activity_name}/unregister endpoint."""

    def test_unregister_success(self, client, reset_activities):
        """Test successful unregistration from an activity."""
        email = "alex@mergington.edu"
        response = client.post(
            "/activities/Basketball/unregister",
            params={"email": email}
        )
        
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]

    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister removes the participant."""
        email = "alex@mergington.edu"
        client.post(
            "/activities/Basketball/unregister",
            params={"email": email}
        )
        
        response = client.get("/activities")
        activities = response.json()
        
        assert email not in activities["Basketball"]["participants"]

    def test_unregister_nonexistent_activity(self, client, reset_activities):
        """Test unregister from an activity that doesn't exist."""
        response = client.post(
            "/activities/NonExistent/unregister",
            params={"email": "student@mergington.edu"}
        )
        
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_not_signed_up(self, client, reset_activities):
        """Test unregister for a student not signed up for the activity."""
        response = client.post(
            "/activities/Basketball/unregister",
            params={"email": "notstudent@mergington.edu"}
        )
        
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_unregister_then_signup_again(self, client, reset_activities):
        """Test that a student can sign up after unregistering."""
        email = "alex@mergington.edu"
        
        # Unregister
        response1 = client.post(
            "/activities/Basketball/unregister",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Sign up again
        response2 = client.post(
            "/activities/Basketball/signup",
            params={"email": email}
        )
        assert response2.status_code == 200
        
        # Verify participant is back
        response = client.get("/activities")
        activities = response.json()
        assert email in activities["Basketball"]["participants"]


class TestRootEndpoint:
    """Test suite for the root endpoint."""

    def test_root_redirects(self, client):
        """Test that root endpoint redirects to static HTML."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307  # Temporary redirect
        assert response.headers["location"] == "/static/index.html"
