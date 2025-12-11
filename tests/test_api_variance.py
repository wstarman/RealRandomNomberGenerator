"""
Unit tests for the API server random number endpoint.

Tests that the /api/random endpoint:
1. Returns valid response format
2. Produces different random numbers on consecutive requests
3. Correctly reports the source (microphone or fallback)
"""

import unittest
import sys
import os
import time
from typing import List, Dict

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import the FastAPI app
from server import app, rng

# Import test client
from fastapi.testclient import TestClient


class TestAPIRandomEndpoint(unittest.TestCase):
    """Test the /api/random endpoint"""

    @classmethod
    def setUpClass(cls):
        """Set up test client once for all tests"""
        cls.client = TestClient(app)

    def test_api_response_format(self):
        """Test that the API returns the expected JSON format"""
        response = self.client.get("/api/random")

        self.assertEqual(response.status_code, 200, "Should return 200 OK")

        data = response.json()
        self.assertIn('rand', data, "Response should contain 'rand' field")
        self.assertIn('source', data, "Response should contain 'source' field")
        self.assertIn('timestamp', data, "Response should contain 'timestamp' field")

        # Validate types
        self.assertIsInstance(data['rand'], float, "'rand' should be a float")
        self.assertIsInstance(data['source'], str, "'source' should be a string")
        self.assertIsInstance(data['timestamp'], str, "'timestamp' should be a string")

        # Validate range
        self.assertGreaterEqual(data['rand'], 0.0, "'rand' should be >= 0")
        self.assertLess(data['rand'], 1.0, "'rand' should be < 1")

        # Validate source value
        self.assertIn(data['source'], ['microphone', 'fallback'],
                     "'source' should be 'microphone' or 'fallback'")

    def test_consecutive_requests_produce_different_numbers(self):
        """Test that multiple API requests return different random numbers"""
        random_numbers: List[float] = []
        responses: List[Dict] = []

        # Make 10 requests
        for i in range(10):
            response = self.client.get("/api/random")
            self.assertEqual(response.status_code, 200,
                           f"Request {i+1} should return 200 OK")

            data = response.json()
            responses.append(data)
            random_numbers.append(data['rand'])

            # Small delay to ensure different audio samples
            time.sleep(0.1)

        # Check that we have multiple unique values
        unique_numbers = len(set(random_numbers))
        self.assertGreater(unique_numbers, 1,
                         f"Should have more than 1 unique value, got {unique_numbers}. "
                         f"Numbers: {random_numbers}")

        # For a truly random source with 10 samples, we should have at least 8 unique
        self.assertGreaterEqual(unique_numbers, 8,
                              f"Should have at least 8 unique values out of 10, "
                              f"got {unique_numbers}. Numbers: {random_numbers}")

        print(f"\nGenerated {len(random_numbers)} numbers with {unique_numbers} unique values:")
        for i, (num, resp) in enumerate(zip(random_numbers, responses)):
            print(f"  {i+1}. {num:.6f} (source: {resp['source']})")

    def test_api_uses_microphone_source(self):
        """Test that the API uses microphone source when available"""
        # Make a request
        response = self.client.get("/api/random")
        self.assertEqual(response.status_code, 200)

        data = response.json()

        # If the RNG has microphone available, API should report it
        if rng.microphone_available:
            self.assertEqual(data['source'], 'microphone',
                           "Should use 'microphone' source when available")
        else:
            self.assertEqual(data['source'], 'fallback',
                           "Should use 'fallback' when microphone unavailable")

    def test_rapid_consecutive_requests(self):
        """Test that rapid consecutive requests (no delay) still produce different numbers"""
        random_numbers: List[float] = []

        # Make 5 rapid requests without delay
        for i in range(5):
            response = self.client.get("/api/random")
            self.assertEqual(response.status_code, 200)
            random_numbers.append(response.json()['rand'])

        # Even with rapid requests, should have variance
        unique_numbers = len(set(random_numbers))
        self.assertGreater(unique_numbers, 1,
                         f"Rapid requests should still produce different numbers. "
                         f"Got {unique_numbers} unique out of 5: {random_numbers}")


class TestAPIErrorHandling(unittest.TestCase):
    """Test API error handling"""

    @classmethod
    def setUpClass(cls):
        """Set up test client once for all tests"""
        cls.client = TestClient(app)

    def test_api_handles_errors_gracefully(self):
        """Test that API returns proper error responses on failure"""
        # This test would need to simulate a failure condition
        # For now, just verify the endpoint is accessible
        response = self.client.get("/api/random")
        self.assertIn(response.status_code, [200, 500],
                     "Should return either success or error code")

        if response.status_code == 500:
            data = response.json()
            self.assertIn('error', data,
                         "Error response should contain 'error' field")


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
