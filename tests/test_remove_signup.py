"""
Tests for DELETE /activities/{activity_name}/signup endpoint.

Tests the endpoint that removes a student from an activity.
"""

import pytest


class TestRemoveFromActivity:
    """Tests for DELETE /activities/{activity_name}/signup endpoint using AAA pattern."""
    
    # ========================================================================
    # HAPPY PATH TESTS
    # ========================================================================
    
    def test_remove_happy_path_success(self, client):
        """
        Arrange: Client with existing participant
        Act: DELETE /activities/Chess Club/signup?email=michael@mergington.edu
        Assert: Response status 200, message indicates success
        """
        response = client.delete(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "michael@mergington.edu" in data["message"]
    
    def test_remove_deletes_participant_from_list(self, client):
        """
        Arrange: Client with existing participant
        Act: DELETE signup, then GET /activities
        Assert: Email no longer in participants list
        """
        email = "michael@mergington.edu"
        
        # Act: Remove
        client.delete(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        
        # Assert: Verify participant removed
        response = client.get("/activities")
        activities = response.json()
        assert email not in activities["Chess Club"]["participants"]
    
    def test_remove_decrements_participant_count(self, client):
        """
        Arrange: Client with existing participant
        Act: GET initial count, remove, GET new count
        Assert: Participant count decremented by 1
        """
        email = "michael@mergington.edu"
        
        # Arrange: Get initial count (Chess Club starts with 2)
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()["Chess Club"]["participants"])
        
        # Act: Remove
        client.delete(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        
        # Assert: Verify count decreased
        final_response = client.get("/activities")
        final_count = len(final_response.json()["Chess Club"]["participants"])
        assert final_count == initial_count - 1
    
    def test_remove_leaves_other_participants(self, client):
        """
        Arrange: Client with activity having multiple participants
        Act: Remove one participant, verify others remain
        Assert: Only specified participant removed, others unchanged
        """
        # Arrange: Chess Club has michael and daniel
        remove_email = "michael@mergington.edu"
        keep_email = "daniel@mergington.edu"
        
        # Act: Remove michael
        client.delete(
            "/activities/Chess Club/signup",
            params={"email": remove_email}
        )
        
        # Assert: Daniel still there, michael gone
        response = client.get("/activities")
        activities = response.json()
        assert remove_email not in activities["Chess Club"]["participants"]
        assert keep_email in activities["Chess Club"]["participants"]
    
    def test_remove_multiple_participants_sequentially(self, client):
        """
        Arrange: Client with activity having multiple participants
        Act: Remove first participant, then second
        Assert: Both removals succeed, activity ends empty
        """
        first_email = "michael@mergington.edu"
        second_email = "daniel@mergington.edu"
        
        # Remove first
        response1 = client.delete(
            "/activities/Chess Club/signup",
            params={"email": first_email}
        )
        assert response1.status_code == 200
        
        # Remove second
        response2 = client.delete(
            "/activities/Chess Club/signup",
            params={"email": second_email}
        )
        assert response2.status_code == 200
        
        # Verify both gone
        response = client.get("/activities")
        activities = response.json()
        assert len(activities["Chess Club"]["participants"]) == 0
    
    # ========================================================================
    # ERROR CASE TESTS
    # ========================================================================
    
    def test_remove_activity_not_found_returns_404(self, client):
        """
        Arrange: Client
        Act: DELETE /activities/NonExistent/signup?email={valid_email}
        Assert: Response status is 404 Not Found
        """
        response = client.delete(
            "/activities/NonExistent/signup",
            params={"email": "test@mergington.edu"}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_remove_student_not_signed_up_returns_400(self, client):
        """
        Arrange: Client with email not in activity
        Act: DELETE /activities/Chess Club/signup?email={not_signed_up_email}
        Assert: Response status is 400 Bad Request
        """
        response = client.delete(
            "/activities/Chess Club/signup",
            params={"email": "not_signed_up@mergington.edu"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "not signed up" in data["detail"].lower()
    
    def test_remove_missing_email_query_parameter(self, client):
        """
        Arrange: Client
        Act: DELETE /activities/Chess Club/signup (no email parameter)
        Assert: Response status is 422 (missing required parameter)
        """
        response = client.delete("/activities/Chess Club/signup")
        
        assert response.status_code == 422  # Unprocessable Entity
    
    def test_remove_already_removed_fails(self, client):
        """
        Arrange: Client, pre-remove a participant
        Act: Try to remove same participant twice
        Assert: First succeeds (200), second fails (400)
        """
        email = "michael@mergington.edu"
        
        # First removal should succeed
        response1 = client.delete(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Second removal should fail
        response2 = client.delete(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response2.status_code == 400
    
    # ========================================================================
    # EDGE CASE TESTS
    # ========================================================================
    
    def test_remove_email_case_sensitivity(self, client):
        """
        Arrange: Client with michael@mergington.edu in Chess Club
        Act: Try to remove MICHAEL@mergington.edu (different case)
        Assert: Fails because strings are case-sensitive
        """
        response = client.delete(
            "/activities/Chess Club/signup",
            params={"email": "MICHAEL@mergington.edu"}  # Different case
        )
        
        assert response.status_code == 400  # Should fail - not found as written
    
    def test_remove_special_characters_in_email(self, client, valid_email):
        """
        Arrange: First add student with special char email, then remove
        Act: Add special email, then remove it
        Assert: Successfully removes the special char email
        """
        special_email = "student+test@mergington.edu"
        
        # First add
        client.post(
            "/activities/Chess Club/signup",
            params={"email": special_email}
        )
        
        # Then remove
        response = client.delete(
            "/activities/Chess Club/signup",
            params={"email": special_email}
        )
        
        assert response.status_code == 200
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert special_email not in activities["Chess Club"]["participants"]
    
    def test_remove_returns_success_message_format(self, client):
        """
        Arrange: Client with existing participant
        Act: DELETE signup
        Assert: Response message includes email and activity name
        """
        email = "michael@mergington.edu"
        response = client.delete(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert email in data["message"]
        assert "Chess Club" in data["message"]
        assert "Removed" in data["message"]
    
    def test_remove_activity_in_isolation(self, client):
        """
        Arrange: Client with activities having participants
        Act: Remove from one activity
        Assert: Other activities unaffected
        """
        # Remove from Chess Club
        client.delete(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        
        # Check Programming Class unchanged
        response = client.get("/activities")
        activities = response.json()
        assert len(activities["Programming Class"]["participants"]) == 2
        assert "emma@mergington.edu" in activities["Programming Class"]["participants"]
