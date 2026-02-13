"""Tests for the Mergington High School API"""

import pytest


class TestActivities:
    """Tests for the activities endpoints"""

    def test_get_activities(self, client):
        """Test getting all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data

    def test_get_activities_structure(self, client):
        """Test that activities have the correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity in data.items():
            assert "description" in activity
            assert "schedule" in activity
            assert "max_participants" in activity
            assert "participants" in activity
            assert isinstance(activity["participants"], list)

    def test_get_activities_has_participants(self, client):
        """Test that activities have initial participants"""
        response = client.get("/activities")
        data = response.json()
        
        assert len(data["Chess Club"]["participants"]) == 2
        assert len(data["Programming Class"]["participants"]) == 2
        assert len(data["Gym Class"]["participants"]) == 2


class TestSignup:
    """Tests for signup functionality"""

    def test_signup_for_activity(self, client):
        """Test signing up for an activity"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "alice@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "alice@mergington.edu" in data["message"]

    def test_signup_adds_participant(self, client):
        """Test that signup actually adds the participant"""
        client.post(
            "/activities/Chess Club/signup",
            params={"email": "bob@mergington.edu"}
        )
        
        response = client.get("/activities")
        data = response.json()
        assert "bob@mergington.edu" in data["Chess Club"]["participants"]

    def test_signup_nonexistent_activity(self, client):
        """Test signing up for an activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.text

    def test_signup_duplicate_email(self, client):
        """Test signing up with the same email multiple times"""
        email = "charlie@mergington.edu"
        
        # First signup
        response1 = client.post(
            "/activities/Programming Class/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Second signup with same email
        response2 = client.post(
            "/activities/Programming Class/signup",
            params={"email": email}
        )
        assert response2.status_code == 200
        
        # Verify both were added
        response = client.get("/activities")
        data = response.json()
        count = data["Programming Class"]["participants"].count(email)
        assert count == 2


class TestUnregister:
    """Tests for unregister functionality"""

    def test_unregister_from_activity(self, client):
        """Test unregistering from an activity"""
        # First signup
        client.post(
            "/activities/Gym Class/signup",
            params={"email": "diana@mergington.edu"}
        )
        
        # Then unregister
        response = client.post(
            "/activities/Gym Class/unregister",
            params={"email": "diana@mergington.edu"}
        )
        assert response.status_code == 200
        assert "Unregistered" in response.text

    def test_unregister_removes_participant(self, client):
        """Test that unregister actually removes the participant"""
        email = "eve@mergington.edu"
        
        # Signup
        client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        
        # Unregister
        client.post(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        
        # Verify removal
        response = client.get("/activities")
        data = response.json()
        assert email not in data["Chess Club"]["participants"]

    def test_unregister_nonexistent_activity(self, client):
        """Test unregistering from an activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent Activity/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.text

    def test_unregister_nonexistent_student(self, client):
        """Test unregistering a student who isn't registered"""
        response = client.post(
            "/activities/Chess Club/unregister",
            params={"email": "notregistered@mergington.edu"}
        )
        assert response.status_code == 400
        assert "Student not found" in response.text

    def test_unregister_existing_participant(self, client):
        """Test unregistering an existing participant"""
        # Try to unregister someone who was in the initial participants list
        response = client.post(
            "/activities/Chess Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 200
        
        # Verify removal
        response = client.get("/activities")
        data = response.json()
        assert "michael@mergington.edu" not in data["Chess Club"]["participants"]
