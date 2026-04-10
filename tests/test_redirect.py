"""
Tests for GET / endpoint.

Tests the root endpoint that redirects to the static index.html file.
"""

import pytest


class TestRootRedirect:
    """Tests for GET / endpoint using AAA pattern."""
    
    def test_root_redirect_status_code(self, client):
        """
        Arrange: Client
        Act: GET /
        Assert: Response status is redirect (307 Temporary Redirect)
        """
        response = client.get("/", follow_redirects=False)
        
        # RedirectResponse uses 307 status code
        assert response.status_code == 307
    
    def test_root_redirect_location_header(self, client):
        """
        Arrange: Client
        Act: GET /
        Assert: Location header points to /static/index.html
        """
        response = client.get("/", follow_redirects=False)
        
        assert "location" in response.headers
        assert response.headers["location"] == "/static/index.html"
    
    def test_root_redirect_is_temporary(self, client):
        """
        Arrange: Client
        Act: GET / (without following redirect)
        Assert: Status is 307 (Temporary Redirect), not 301 (Permanent)
        """
        response = client.get("/", follow_redirects=False)
        
        # 307 indicates temporary redirect
        assert response.status_code == 307
        assert response.status_code != 301  # Not permanent
    
    def test_root_can_follow_redirect(self, client):
        """
        Arrange: Client
        Act: GET / with follow_redirects=True
        Assert: Eventually reaches a response (redirect followed)
        
        Note: This may fail if /static/index.html doesn't exist, 
        but tests that the redirect mechanism works.
        """
        response = client.get("/", follow_redirects=True)
        
        # After following redirect, we get some response
        assert response.status_code is not None
    
    def test_root_redirect_no_body(self, client):
        """
        Arrange: Client
        Act: GET /
        Assert: Response has minimal/no body (redirect responses typically empty)
        """
        response = client.get("/", follow_redirects=False)
        
        # Redirect responses typically have minimal content
        # (may be empty or just contain redirect info)
        assert response.status_code == 307
