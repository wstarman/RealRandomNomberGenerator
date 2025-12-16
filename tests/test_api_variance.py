"""
Unit tests for the API server random number endpoint.

Tests that the /api/random endpoint:
1. Produces different random numbers on consecutive requests
2. Produces random numbers with enough variance
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


class TestAPIRandomVariance(unittest.TestCase):
    """Test the result variance of /api/random endpoint"""
    # These tests require access to a working microphone

    @classmethod
    def setUpClass(cls):
        """Set up test client once for all tests"""
        cls.client = TestClient(app)

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

if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
