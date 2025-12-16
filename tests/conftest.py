"""
Pytest configuration and fixtures for backend tests.

This module provides shared test fixtures including:
- FastAPI TestClient for API testing
- Mock RealRNG class that returns predictable values
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add src directory to path so we can import server and RealRNG
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class MockRealRNG:
    """
    Mock implementation of RealRNG that returns predictable values.

    This allows testing the API without requiring actual audio hardware.
    """

    def __init__(self):
        self.SOURCE_MICROPHONE = "microphone"
        self.SOURCE_FALLBACK = "fallback"
        self._source = self.SOURCE_MICROPHONE
        self._should_fail = False

    def getRand(self) -> float:
        """Return a predictable random value for testing."""
        if self._should_fail:
            raise Exception("Simulated RNG failure")
        return 0.42

    def getSource(self) -> str:
        """Return the current source (microphone or fallback)."""
        return self._source

    def set_source(self, source: str):
        """Test helper to change the source."""
        self._source = source

    def set_should_fail(self, should_fail: bool):
        """Test helper to simulate failures."""
        self._should_fail = should_fail

    def end(self):
        """Mock cleanup method."""
        pass


@pytest.fixture
def mock_rng():
    """
    Fixture that provides a MockRealRNG instance.

    This can be used to patch the RNG in tests that need fine-grained
    control over RNG behavior.
    """
    return MockRealRNG()


@pytest.fixture
def client(mock_rng):
    """
    Fixture that provides a FastAPI TestClient with mocked RNG.

    The RNG instance is patched on the server module to ensure
    the mock is used throughout the application.
    """
    # Import server module
    import server

    # Save original rng instance
    original_rng = server.rng

    # Replace rng instance with mock
    server.rng = mock_rng

    # Create test client
    test_client = TestClient(server.app)

    # Make mock_rng accessible via client for test manipulation
    test_client.mock_rng = mock_rng

    yield test_client

    # Restore original rng
    server.rng = original_rng
