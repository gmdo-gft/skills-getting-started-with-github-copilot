"""Pytest configuration and shared fixtures."""

import pytest
import copy
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Provide a TestClient for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def fresh_activities():
    """Reset activities to initial state before each test."""
    # Store original activities
    original = copy.deepcopy(activities)
    
    # Reset the global activities dict
    activities.clear()
    activities.update(original)
    
    yield activities
    
    # Cleanup: restore original state
    activities.clear()
    activities.update(original)
