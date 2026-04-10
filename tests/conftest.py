"""
Shared fixtures and configuration for FastAPI backend tests.

Uses the AAA (Arrange-Act-Assert) pattern:
- Arrange: Fixtures set up test data and client
- Act: Test function executes endpoint calls
- Assert: Test function verifies results
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture(autouse=True)
def reset_activities():
    """
    Fixture to reset activities to their initial state before each test.
    
    This ensures test isolation by providing a fresh copy of activities
    for each test, preventing state leakage between tests.
    
    Runs automatically for every test (autouse=True).
    """
    # Initial state of activities
    initial_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball": {
            "description": "Team sport and athletic training",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu"]
        },
        "Tennis": {
            "description": "Racquet sport and fitness conditioning",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 10,
            "participants": ["alex@mergington.edu", "rachel@mergington.edu"]
        },
        "Drama Club": {
            "description": "Acting, theater productions, and performance arts",
            "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["sarah@mergington.edu", "lucas@mergington.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, and visual arts creation",
            "schedule": "Mondays and Thursdays, 3:30 PM - 4:45 PM",
            "max_participants": 18,
            "participants": ["maya@mergington.edu"]
        },
        "Debate Team": {
            "description": "Public speaking and competitive debate",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["andrew@mergington.edu", "jessica@mergington.edu"]
        },
        "Science Club": {
            "description": "Hands-on experiments and scientific exploration",
            "schedule": "Fridays, 3:30 PM - 4:45 PM",
            "max_participants": 22,
            "participants": ["david@mergington.edu", "anna@mergington.edu"]
        }
    }
    
    # Clear existing activities
    activities.clear()
    
    # Populate with initial state (deep copy of participants lists)
    for activity_name, activity_data in initial_activities.items():
        activities[activity_name] = {
            "description": activity_data["description"],
            "schedule": activity_data["schedule"],
            "max_participants": activity_data["max_participants"],
            "participants": activity_data["participants"].copy()
        }
    
    yield  # Run the test
    
    # Cleanup after test (not strictly necessary but good practice)
    activities.clear()


@pytest.fixture
def client():
    """
    Fixture providing a TestClient for making HTTP requests to the app.
    
    Arrange Phase: Provides the test client for making requests.
    """
    return TestClient(app)


@pytest.fixture
def valid_email():
    """
    Fixture providing a valid email address not in initial participant lists.
    
    Useful for signup tests where we need a fresh email to add.
    """
    return "test_student@mergington.edu"


@pytest.fixture
def alt_email():
    """
    Fixture providing an alternative valid email address.
    
    Useful for tests that need multiple different emails.
    """
    return "another_student@mergington.edu"


@pytest.fixture
def activity_names():
    """
    Fixture providing list of all valid activity names.
    
    Arrange Phase: Provides activity names for parametrized tests.
    """
    return [
        "Chess Club",
        "Programming Class",
        "Gym Class",
        "Basketball",
        "Tennis",
        "Drama Club",
        "Art Studio",
        "Debate Team",
        "Science Club"
    ]
