"""
Unit tests for audio device selection with variance validation.

Tests that the RealRNG library correctly:
1. Rejects devices that only produce silence/zeros
2. Selects devices with actual audio variance
3. Produces different random numbers on consecutive calls
"""

import unittest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from RealRNG.RealRNG import RealRNG


class TestDeviceSelection(unittest.TestCase):
    """Test that device selection validates audio variance"""

    def setUp(self):
        """Create a fresh RealRNG instance for each test"""
        # Enable debug logging for detailed output
        os.environ['REALRNG_DEBUG'] = '1'

    def tearDown(self):
        """Clean up environment"""
        if 'REALRNG_DEVICE_INDEX' in os.environ:
            del os.environ['REALRNG_DEVICE_INDEX']

    def test_auto_selection_rejects_silent_device(self):
        """Test that auto-detection rejects device 3 (silent) and selects device 6 (active)"""
        with RealRNG() as rng:
            # Device 3 should be rejected for having no variance
            # Device 6 (pulse) should be selected
            self.assertIsNotNone(rng.device_index, "Should find a working device")
            self.assertEqual(rng.device_index, 6, "Should select device 6 (pulse), not device 3 (silent)")
            self.assertTrue(rng.microphone_available, "Microphone should be available")

    def test_manual_device_with_no_variance_falls_back(self):
        """Test that manually specifying a silent device (3) falls back to auto-detection"""
        os.environ['REALRNG_DEVICE_INDEX'] = '3'

        with RealRNG() as rng:
            # Even with manual override, should reject device 3 and fall back
            # The current implementation will try device 3, fail variance check,
            # then fall back to auto-detection which should select device 6
            if rng.microphone_available:
                # If a device was found, it should be device 6 (not the silent device 3)
                self.assertNotEqual(rng.device_index, 3,
                                  "Should not use device 3 (no variance)")

    def test_working_device_produces_variance(self):
        """Test that the selected device actually produces varying audio"""
        with RealRNG() as rng:
            self.assertTrue(rng.microphone_available, "Should have microphone available")

            # Capture 5 samples
            samples = []
            for i in range(5):
                # Open stream and read data
                source = rng.getSource()
                self.assertEqual(source, "microphone", "Should use microphone source")

                if rng.stream:
                    data = rng.stream.read(4, exception_on_overflow=False)
                    samples.append(data)
                    rng.stream.stop_stream()
                    rng.stream.close()
                    rng.stream = None

            # Validate variance
            unique_samples = len(set(samples))
            self.assertGreaterEqual(unique_samples, 2,
                                  f"Should have at least 2 unique samples, got {unique_samples}")

            # Check not all zeros
            all_zero = all(sample == b'\x00' * len(sample) for sample in samples)
            self.assertFalse(all_zero, "Samples should not all be zero")


class TestRandomNumberVariance(unittest.TestCase):
    """Test that random number generation produces varying outputs"""

    def test_consecutive_calls_produce_different_numbers(self):
        """Test that calling getRand() multiple times produces different numbers"""
        with RealRNG() as rng:
            # Generate 10 random numbers
            random_numbers = []
            for i in range(10):
                rand = rng.getRand()
                random_numbers.append(rand)
                self.assertGreaterEqual(rand, 0.0, "Random number should be >= 0")
                self.assertLess(rand, 1.0, "Random number should be < 1")

            # Check that we have multiple unique values
            unique_numbers = len(set(random_numbers))
            self.assertGreater(unique_numbers, 1,
                             f"Should have more than 1 unique value, got {unique_numbers}. "
                             f"Numbers: {random_numbers}")

            # For a truly random source with 10 samples, we should have at least 8 unique
            self.assertGreaterEqual(unique_numbers, 8,
                                  f"Should have at least 8 unique values out of 10, got {unique_numbers}")

    def test_source_reporting(self):
        """Test that getSource() correctly reports microphone or fallback"""
        with RealRNG() as rng:
            source = rng.getSource()
            self.assertIn(source, ["microphone", "fallback"],
                         "Source should be either 'microphone' or 'fallback'")

            # If microphone is available, it should report microphone
            if rng.microphone_available:
                self.assertEqual(source, "microphone",
                               "Should report 'microphone' when available")


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
