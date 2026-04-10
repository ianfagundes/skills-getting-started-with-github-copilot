"""
Tests for POST /activities/{activity_name}/signup endpoint.

Tests the endpoint that signs up a student for an activity.
"""

import pytest


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint using AAA pattern."""
    
    # ========================================================================
    # HAPPY PATH TESTS
    # ========================================================================
    
    def test_signup_happy_path_success(self, client, valid_email):
        """
        Arrange: Client and new email fixture
        Act: POST /activities/Chess Club/signup?email={valid_email}
        Assert: Response status 200, message indicates success
        """
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": valid_email}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert valid_email in data["message"]
    
    def test_signup_adds_participant_to_list(self, client, valid_email):
        """
        Arrange: Client and new email fixture
        Act: POST signup for Chess Club, then GET /activities
        Assert: Email appears in participants list for Chess Club
        """
        # Act: Sign up
        client.post(
            "/activities/Chess Club/signup",
            params={"email": valid_email}
        )
        
        # Assert: Verify participant added
        response = client.get("/activities")
        activities = response.json()
        assert valid_email in activities["Chess Club"]["participants"]
    
    def test_signup_increments_participant_count(self, client, valid_email):
        """
        Arrange: Client and new email fixture
        Act: GET initial count, signup, GET new count
        Assert: Participant count incremented by 1
        """
        # Arrange: Get initial count
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()["Chess Club"]["participants"])
        
        # Act: Sign up
        client.post(
            "/activities/Chess Club/signup",
            params={"email": valid_email}
        )
        
        # Assert: Verify count increased
        final_response = client.get("/activities")
        final_count = len(final_response.json()["Chess Club"]["participants"])
        assert final_count == initial_count + 1
    
    def test_signup_multiple_activities(self, client, valid_email, alt_email):
        """
        Arrange: Client and two different email fixtures
        Act: Sign up same email for two different activities
        Assert: Email appears in both activities
        """
        # Act: Sign up for two activities
        client.post("/activities/Chess Club/signup", params={"email": valid_email})
        client.post("/activities/Programming Class/signup", params={"email": valid_email})
        
        # Assert: Email in both
        response = client.get("/activities")
        activities = response.json()
        assert valid_email in activities["Chess Club"]["participants"]
        assert valid_email in activities["Programming Class"]["participants"]
    
    # ========================================================================
    # ERROR CASE TESTS
    # ========================================================================
    
    def test_signup_activity_not_found_returns_404(self, client, valid_email):
        """
        Arrange: Client and new email fixture
        Act: POST /activities/NonExistent/signup?email={valid_email}
        Assert: Response status is 404 Not Found
        """
        response = client.post(
            "/activities/NonExistent/signup",
            params={"email": valid_email}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_signup_duplicate_student_returns_400(self, client):
        """
        Arrange: Client with existing participant email
        Act: POST /activities/Chess Club/signup?email=michael@mergington.edu (already signed up)
        Assert: Response status is 400 Bad Request
        """
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"}  # Already in Chess Club
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"].lower()
    
    def test_signup_missing_email_query_parameter(self, client):
        """
        Arrange: Client
        Act: POST /activities/Chess Club/signup (no email parameter)
        Assert: Response status is 422 (missing required parameter)
        """
        response = client.post("/activities/Chess Club/signup")
        
        assert response.status_code == 422  # Unprocessable Entity (missing param)
    
    # ========================================================================
    # EDGE CASE TESTS
    # ========================================================================
    
    def test_signup_email_case_sensitivity(self, client):
        """
        Arrange: Client
        Act: Try to sign up with different case variation of existing email
        Assert: Treated as different email (strings are case-sensitive)
        
        Note: This tests current behavior; email validation could be added later.
        """
        # Arrange: Michael is in Chess Club
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "MICHAEL@mergington.edu"}  # Different case
        )
        
        # Should succeed since it's treated as different email
        assert response.status_code == 200
    
    def test_signup_special_characters_in_email(self, client):
        """
        Arrange: Client
        Act: POST with email containing special characters
        Assert: Accepts the email (no validation in app)
        """
        special_email = "student+test@mergington.edu"
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": special_email}
        )
        
        assert response.status_code == 200
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert special_email in activities["Chess Club"]["participants"]
    
    def test_signup_capacity_boundary_single_slot(self, client):
        """
        Arrange: Client with activity having 1 participant (initial state)
        Act: Get activity with few participants (Art Studio has 1), sign up new student
        Assert: Successfully adds participant when space available
        """
        # Art Studio has 1 participant, max 18, so plenty of space
        new_email = "new_art_student@mergington.edu"
        response = client.post(
            "/activities/Art Studio/signup",
            params={"email": new_email}
        )
        
        assert response.status_code == 200
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert len(activities["Art Studio"]["participants"]) == 2
    
    def test_signup_returns_success_message_format(self, client, valid_email):
        """
        Arrange: Client and new email fixture
        Act: POST signup
        Assert: Response message includes email and activity name
        """
        response = client.post(
            "/activities/Programming Class/signup",
            params={"email": valid_email}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert valid_email in data["message"]
        assert "Programming Class" in data["message"]
        assert "Signed up" in data["message"]
    
    def test_signup_different_activities_independently(self, client, valid_email):
        """
        Arrange: Client and new email fixture
        Act: Sign up for Chess Club, verify, then sign up for Tennis, verify
        Assert: Each activity's participant list updated independently
        """
        # Sign up for Chess Club
        client.post("/activities/Chess Club/signup", params={"email": valid_email})
        response1 = client.get("/activities")
        assert valid_email in response1.json()["Chess Club"]["participants"]
        assert valid_email not in response1.json()["Tennis"]["participants"]
        
        # Sign up for Tennis
        client.post("/activities/Tennis/signup", params={"email": valid_email})
        response2 = client.get("/activities")
        assert valid_email in response2.json()["Chess Club"]["participants"]
        assert valid_email in response2.json()["Tennis"]["participants"]
