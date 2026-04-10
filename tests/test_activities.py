"""
Tests for GET /activities endpoint.

Tests the endpoint that retrieves all available activities with their details.
"""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint using AAA pattern."""
    
    def test_get_activities_returns_200(self, client):
        """
        Arrange: Client is provided by fixture
        Act: GET /activities
        Assert: Response status is 200 OK
        """
        response = client.get("/activities")
        
        assert response.status_code == 200
    
    def test_get_activities_returns_all_9_activities(self, client):
        """
        Arrange: Client is provided by fixture
        Act: GET /activities
        Assert: Response contains all 9 activities
        """
        response = client.get("/activities")
        activities = response.json()
        
        assert len(activities) == 9
    
    def test_get_activities_response_schema(self, client):
        """
        Arrange: Client is provided by fixture
        Act: GET /activities
        Assert: Each activity has correct schema (name, description, schedule, max_participants, participants)
        """
        response = client.get("/activities")
        activities = response.json()
        
        # Check each activity has required fields
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_name, str)
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)
    
    def test_get_activities_contains_chess_club(self, client):
        """
        Arrange: Client is provided by fixture
        Act: GET /activities
        Assert: Chess Club activity exists with correct properties
        """
        response = client.get("/activities")
        activities = response.json()
        
        assert "Chess Club" in activities
        chess = activities["Chess Club"]
        assert chess["max_participants"] == 12
        assert "michael@mergington.edu" in chess["participants"]
        assert "daniel@mergington.edu" in chess["participants"]
    
    def test_get_activities_contains_programming_class(self, client):
        """
        Arrange: Client is provided by fixture
        Act: GET /activities
        Assert: Programming Class activity exists with correct properties
        """
        response = client.get("/activities")
        activities = response.json()
        
        assert "Programming Class" in activities
        programming = activities["Programming Class"]
        assert programming["max_participants"] == 20
        assert "emma@mergington.edu" in programming["participants"]
        assert "sophia@mergington.edu" in programming["participants"]
    
    def test_get_activities_initial_participant_counts(self, client):
        """
        Arrange: Client is provided by fixture with initial state
        Act: GET /activities
        Assert: All initial participant counts are correct (2, 2, 2, 1, 2, 2, 1, 2, 2)
        """
        response = client.get("/activities")
        activities = response.json()
        
        expected_counts = {
            "Chess Club": 2,
            "Programming Class": 2,
            "Gym Class": 2,
            "Basketball": 1,
            "Tennis": 2,
            "Drama Club": 2,
            "Art Studio": 1,
            "Debate Team": 2,
            "Science Club": 2
        }
        
        for activity_name, expected_count in expected_counts.items():
            actual_count = len(activities[activity_name]["participants"])
            assert actual_count == expected_count, \
                f"{activity_name} has {actual_count} participants, expected {expected_count}"
    
    def test_get_activities_has_all_required_activities(self, client, activity_names):
        """
        Arrange: Client and activity_names fixture provided
        Act: GET /activities
        Assert: Response contains all required activities
        """
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name in activity_names:
            assert activity_name in activities, f"Activity '{activity_name}' not found in response"
