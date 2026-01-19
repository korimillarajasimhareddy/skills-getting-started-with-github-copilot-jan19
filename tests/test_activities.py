"""Tests for activities endpoints."""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_list(self, client):
        """Test that get activities returns all activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0

    def test_get_activities_includes_required_fields(self, client):
        """Test that each activity has required fields."""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_get_activities_has_basketball(self, client):
        """Test that Basketball activity exists."""
        response = client.get("/activities")
        data = response.json()
        assert "Basketball" in data


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_success(self, client, reset_activities):
        """Test successful signup for an activity."""
        response = client.post(
            "/activities/Basketball/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]

    def test_signup_adds_participant(self, client, reset_activities):
        """Test that signup actually adds participant to activity."""
        email = "newstudent@mergington.edu"
        client.post(f"/activities/Basketball/signup?email={email}")
        
        # Check that participant was added
        response = client.get("/activities")
        activities = response.json()
        assert email in activities["Basketball"]["participants"]

    def test_signup_nonexistent_activity_returns_404(self, client, reset_activities):
        """Test signup for non-existent activity returns 404."""
        response = client.post(
            "/activities/NonexistentClub/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_duplicate_participant_returns_400(self, client, reset_activities):
        """Test signup for duplicate participant returns 400."""
        email = "alex@mergington.edu"  # Already signed up for Basketball
        response = client.post(
            f"/activities/Basketball/signup?email={email}"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]


class TestUnregister:
    """Tests for POST /activities/{activity_name}/unregister endpoint."""

    def test_unregister_success(self, client, reset_activities):
        """Test successful unregister from an activity."""
        email = "alex@mergington.edu"
        response = client.post(
            f"/activities/Basketball/unregister?email={email}"
        )
        assert response.status_code == 200
        data = response.json()
        assert email in data["message"]

    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister actually removes participant from activity."""
        email = "alex@mergington.edu"
        client.post(f"/activities/Basketball/unregister?email={email}")
        
        # Check that participant was removed
        response = client.get("/activities")
        activities = response.json()
        assert email not in activities["Basketball"]["participants"]

    def test_unregister_nonexistent_activity_returns_404(self, client, reset_activities):
        """Test unregister from non-existent activity returns 404."""
        response = client.post(
            "/activities/NonexistentClub/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404

    def test_unregister_not_signed_up_returns_400(self, client, reset_activities):
        """Test unregister for participant not signed up returns 400."""
        email = "notstudent@mergington.edu"
        response = client.post(
            f"/activities/Basketball/unregister?email={email}"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]

    def test_unregister_then_can_signup_again(self, client, reset_activities):
        """Test that participant can signup again after unregistering."""
        email = "alex@mergington.edu"
        
        # Unregister
        client.post(f"/activities/Basketball/unregister?email={email}")
        
        # Signup again
        response = client.post(
            f"/activities/Basketball/signup?email={email}"
        )
        assert response.status_code == 200
