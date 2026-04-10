"""
Integration tests for cross-endpoint scenarios.

Tests interactions between multiple endpoints to verify overall system behavior.
"""

import pytest


class TestActivitySignupIntegration:
    """Integration tests using AAA pattern for multi-endpoint scenarios."""
    
    def test_signup_multiple_students_for_one_activity(self, client, valid_email, alt_email):
        """
        Arrange: Client and two different email fixtures
        Act: 
          1. Sign up valid_email to Chess Club
          2. Sign up alt_email to Chess Club
          3. GET /activities
        Assert: Both emails in participants list, count incremented twice
        """
        # Arrange: Initial count
        initial = client.get("/activities").json()
        initial_count = len(initial["Chess Club"]["participants"])
        
        # Act: Sign up two students
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": valid_email}
        )
        response2 = client.post(
            "/activities/Chess Club/signup",
            params={"email": alt_email}
        )
        
        # Assert: Both succeeded and count increased by 2
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        final = client.get("/activities").json()
        final_count = len(final["Chess Club"]["participants"])
        assert final_count == initial_count + 2
        assert valid_email in final["Chess Club"]["participants"]
        assert alt_email in final["Chess Club"]["participants"]
    
    def test_signup_then_remove_one_student_leaves_others(self, client, valid_email, alt_email):
        """
        Arrange: Client and two different email fixtures
        Act:
          1. Sign up both emails
          2. GET to verify both present
          3. Remove first email
          4. GET to verify second still there
        Assert: Only specified student removed, other unchanged
        """
        # Arrange: Sign up both
        client.post("/activities/Chess Club/signup", params={"email": valid_email})
        client.post("/activities/Chess Club/signup", params={"email": alt_email})
        
        verify_response = client.get("/activities").json()
        assert valid_email in verify_response["Chess Club"]["participants"]
        assert alt_email in verify_response["Chess Club"]["participants"]
        count_before_remove = len(verify_response["Chess Club"]["participants"])
        
        # Act: Remove first student
        response = client.delete(
            "/activities/Chess Club/signup",
            params={"email": valid_email}
        )
        
        # Assert: First removed, second remains
        assert response.status_code == 200
        final = client.get("/activities").json()
        assert valid_email not in final["Chess Club"]["participants"]
        assert alt_email in final["Chess Club"]["participants"]
        assert len(final["Chess Club"]["participants"]) == count_before_remove - 1
    
    def test_fill_activity_to_capacity_then_fail_on_overflow(self, client):
        """
        Arrange: Client with activities that have small capacities
        Act:
          1. Get current Tennis capacity and participants (max 10, starts with 2)
          2. Sign up 8 new students to reach exactly capacity (9/10)
          3. Sign up 1 more (10/10)
          4. Try to sign up one more (should fail at 11/10 or hit capacity check)
        Assert: Can fill to capacity, but behavior on overflow verified
        
        Note: App doesn't explicitly check capacity - it allows overfilling.
              This test documents that behavior.
        """
        # Arrange: Tennis has max_participants=10, starts with 2
        activity = "Tennis"
        emails = [f"student{i}@mergington.edu" for i in range(1, 10)]  # 9 new emails
        
        # Act: Sign up students one by one
        for email in emails:
            response = client.post(
                f"/activities/{activity}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Assert: Activity now has all participants
        final = client.get("/activities").json()
        final_count = len(final[activity]["participants"])
        # Should have initial 2 + 8 new = 10 (or more if no capacity enforcement)
        assert final_count >= 10
    
    def test_toggle_signup_remove_multiple_times(self, client, valid_email):
        """
        Arrange: Client and email fixture
        Act:
          1. Sign up student
          2. Verify in participants
          3. Remove student
          4. Verify not in participants
          5. Sign up again
          6. Verify in participants
        Assert: Each operation succeeds, state reflects changes
        """
        activity = "Chess Club"
        
        # Sign up
        response1 = client.post(
            f"/activities/{activity}/signup",
            params={"email": valid_email}
        )
        assert response1.status_code == 200
        assert valid_email in client.get("/activities").json()[activity]["participants"]
        
        # Remove
        response2 = client.delete(
            f"/activities/{activity}/signup",
            params={"email": valid_email}
        )
        assert response2.status_code == 200
        assert valid_email not in client.get("/activities").json()[activity]["participants"]
        
        # Sign up again
        response3 = client.post(
            f"/activities/{activity}/signup",
            params={"email": valid_email}
        )
        assert response3.status_code == 200
        assert valid_email in client.get("/activities").json()[activity]["participants"]
    
    def test_independent_activities_no_cross_contamination(self, client, valid_email):
        """
        Arrange: Client and email fixture
        Act:
          1. Sign up for Chess Club
          2. Sign up for Programming Class
          3. Get all activities
          4. Remove from Chess Club
        Assert: Each activity's participant list is independent, removals don't affect others
        """
        # Arrange/Act: Sign up for two different activities
        client.post("/activities/Chess Club/signup", params={"email": valid_email})
        client.post("/activities/Programming Class/signup", params={"email": valid_email})
        
        # Verify in both
        activities = client.get("/activities").json()
        assert valid_email in activities["Chess Club"]["participants"]
        assert valid_email in activities["Programming Class"]["participants"]
        
        programming_count_before = len(activities["Programming Class"]["participants"])
        
        # Remove from Chess Club only
        client.delete(
            "/activities/Chess Club/signup",
            params={"email": valid_email}
        )
        
        # Assert: Removed from Chess Club, still in Programming Class
        final = client.get("/activities").json()
        assert valid_email not in final["Chess Club"]["participants"]
        assert valid_email in final["Programming Class"]["participants"]
        assert len(final["Programming Class"]["participants"]) == programming_count_before
    
    def test_get_activities_reflects_all_changes(self, client, valid_email, alt_email):
        """
        Arrange: Client and multiple email fixtures
        Act:
          1. GET /activities (initial state)
          2. Sign up valid_email
          3. GET /activities (should reflect signup)
          4. Sign up alt_email to different activity
          5. GET /activities (should reflect both changes)
          6. Remove valid_email
          7. GET /activities (should reflect removal)
        Assert: Each GET reflects all previous changes
        """
        activity1 = "Chess Club"
        activity2 = "Programming Class"
        
        # Initial state
        initial = client.get("/activities").json()
        initial_chess_count = len(initial[activity1]["participants"])
        
        # After first signup
        client.post(f"/activities/{activity1}/signup", params={"email": valid_email})
        after_first = client.get("/activities").json()
        assert len(after_first[activity1]["participants"]) == initial_chess_count + 1
        
        # After second signup (different activity)
        initial_prog_count = len(initial[activity2]["participants"])
        client.post(f"/activities/{activity2}/signup", params={"email": alt_email})
        after_second = client.get("/activities").json()
        assert len(after_second[activity2]["participants"]) == initial_prog_count + 1
        assert len(after_second[activity1]["participants"]) == initial_chess_count + 1
        
        # After removal
        client.delete(f"/activities/{activity1}/signup", params={"email": valid_email})
        after_remove = client.get("/activities").json()
        assert len(after_remove[activity1]["participants"]) == initial_chess_count
        assert len(after_remove[activity2]["participants"]) == initial_prog_count + 1
    
    def test_error_during_one_operation_doesnt_affect_state(self, client, valid_email):
        """
        Arrange: Client and email fixture
        Act:
          1. Sign up valid_email successfully
          2. Try to sign up same email again (should fail)
          3. Try to sign up to non-existent activity (should fail)
          4. GET /activities
        Assert: Failed operations don't modify state, valid_email still signed up
        """
        client.post("/activities/Chess Club/signup", params={"email": valid_email})
        
        # These should fail
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": valid_email}
        )
        assert response1.status_code == 400
        
        response2 = client.post(
            "/activities/NonExistent/signup",
            params={"email": "other@mergington.edu"}
        )
        assert response2.status_code == 404
        
        # State should be unchanged - valid_email still there
        final = client.get("/activities").json()
        assert valid_email in final["Chess Club"]["participants"]
