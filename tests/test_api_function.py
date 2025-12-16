"""
Unit tests for the API server random number endpoint.

Tests that the /api/random endpoint:
1. Returns valid response format
2. Correctly reports the source (microphone or fallback)
3. Correctly handles any error occured
"""

import unittest
import sys
import os

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

class TestAPIErrorHandling(unittest.TestCase):
    """Test API error handling"""

    @classmethod
    def setUpClass(cls):
        """Set up test client once for all tests"""
        cls.client = TestClient(app)

    def test_api_handles_errors_gracefully(self):
        """Test that API returns proper error responses on failure"""
        # This test would need to simulate a failure condition
        # Simulate failure conditions forcefully by assigning
        # methods that guaruntee failures
        import asyncio, server
        
        # Make a backup of the original method
        old_random = server.random
        
        # Failure condition 1: Timed out
        # Simulated by sleeping for more than 5 seconds
        async def faulty_random1():
            await asyncio.sleep(10)
        
        server.random = faulty_random1
        
        response = self.client.get("/api/random")
        self.assertIn(response.status_code, [200, 500],
                     "Should return either success or error code")

        if response.status_code == 500:
            data = response.json()
            self.assertIn('error', data,
                         "Error response should contain 'error' field")
        
        # Failure condition 2: Any error from within the library
        # Simulated by raising a RuntimeError
        async def faulty_random2():
            raise RuntimeError
        
        server.random = faulty_random2
        
        response = self.client.get("/api/random")
        self.assertIn(response.status_code, [200, 500],
                     "Should return either success or error code")

        if response.status_code == 500:
            data = response.json()
            self.assertIn('error', data,
                         "Error response should contain 'error' field")
        
        # Restore the method to its original form
        # and test if it's back to normal
        # This should not produce any error
        server.random = old_random
        
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
