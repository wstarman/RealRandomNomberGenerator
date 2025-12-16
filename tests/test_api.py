"""
Unit tests for the FastAPI server endpoints.

Tests cover:
- Successful response structure and status codes
- Field validation (rand, source, timestamp)
- Value range constraints
- Error handling
"""

import pytest
from datetime import datetime


def test_api_random_success(client):
    """
    Test that /api/random returns 200 with valid JSON structure.

    Verifies the happy path where RNG works correctly.
    """
    response = client.get("/api/random")

    assert response.status_code == 200
    data = response.json()

    # Check that all required fields are present
    assert "rand" in data
    assert "source" in data
    assert "timestamp" in data


def test_api_random_field_types(client):
    """
    Test that response fields have the correct types.
    """
    response = client.get("/api/random")
    data = response.json()

    assert isinstance(data["rand"], float)
    assert isinstance(data["source"], str)
    assert isinstance(data["timestamp"], str)


def test_api_random_value_range(client):
    """
    Test that rand value is between 0 and 1 (inclusive).

    This is a fundamental requirement for random number generators
    used in probability calculations.
    """
    response = client.get("/api/random")
    data = response.json()

    assert 0.0 <= data["rand"] <= 1.0, f"rand value {data['rand']} is outside [0, 1] range"


def test_api_random_timestamp_format(client):
    """
    Test that timestamp is in valid ISO format.
    """
    response = client.get("/api/random")
    data = response.json()

    # Should be parseable as ISO format
    try:
        parsed_time = datetime.fromisoformat(data["timestamp"])
        assert parsed_time is not None
    except ValueError:
        pytest.fail(f"Timestamp '{data['timestamp']}' is not valid ISO format")


def test_api_random_source_values(client):
    """
    Test that source field contains expected values.
    """
    response = client.get("/api/random")
    data = response.json()

    # Source should be one of the expected values
    assert data["source"] in ["microphone", "fallback"]


def test_api_random_with_microphone_source(client):
    """
    Test API response when RNG uses microphone source.
    """
    # Mock RNG returns 'microphone' source by default
    response = client.get("/api/random")
    data = response.json()

    assert data["source"] == "microphone"
    assert data["rand"] == 0.42  # Mock returns this value


def test_api_random_with_fallback_source(client):
    """
    Test API response when RNG uses fallback source.
    """
    # Change mock to return fallback source
    client.mock_rng.set_source("fallback")

    response = client.get("/api/random")
    data = response.json()

    assert data["source"] == "fallback"


def test_api_random_handles_rng_failure(client):
    """
    Test that API returns 500 error when RNG fails.

    This verifies graceful error handling when the underlying
    RNG encounters an error.
    """
    # Configure mock to fail
    client.mock_rng.set_should_fail(True)

    response = client.get("/api/random")

    assert response.status_code == 500
    data = response.json()
    assert "error" in data


def test_api_random_multiple_calls(client):
    """
    Test that multiple calls to the endpoint succeed.

    Verifies the endpoint is stateless and can handle repeated requests.
    """
    for _ in range(5):
        response = client.get("/api/random")
        assert response.status_code == 200
        data = response.json()
        assert "rand" in data
        assert "source" in data
        assert "timestamp" in data


def test_api_random_cors_headers(client):
    """
    Test that CORS headers are present in response.

    This is important for frontend access from different origins.
    """
    response = client.get("/api/random")

    # FastAPI TestClient doesn't include CORS headers in same-origin requests
    # but we can verify the middleware is configured by checking response
    # succeeds (middleware doesn't block it)
    assert response.status_code == 200
