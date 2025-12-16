"""
Unit tests for the RealRNG class.

Tests cover:
- Basic functionality of getRand() and getSource()
- Value range validation
- Fallback mode when no microphone available
- Error handling
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@pytest.fixture
def mock_pyaudio():
    """
    Fixture that provides a mocked PyAudio instance.

    This prevents tests from trying to access actual audio hardware.
    """
    mock = MagicMock()
    mock_instance = MagicMock()
    mock.return_value = mock_instance

    # Configure mock to simulate no devices
    mock_instance.get_device_count.return_value = 0

    return mock


@pytest.fixture
def mock_pyaudio_with_device():
    """
    Fixture that provides a mocked PyAudio instance with a working device.
    """
    mock = MagicMock()
    mock_instance = MagicMock()
    mock.return_value = mock_instance

    # Configure mock to simulate one input device
    mock_instance.get_device_count.return_value = 1
    mock_instance.get_device_info_by_index.return_value = {
        'name': 'Mock Microphone',
        'maxInputChannels': 2,
        'defaultSampleRate': 44100.0
    }

    # Configure mock stream
    mock_stream = MagicMock()
    mock_stream.is_active.return_value = True
    mock_stream.read.return_value = b'\x01\x02\x03\x04\x05\x06\x07\x08'
    mock_instance.open.return_value = mock_stream

    return mock


def test_rng_getrand_returns_float():
    """
    Test that getRand() returns a float value.
    """
    with patch('pyaudio.PyAudio') as mock_pyaudio:
        mock_pyaudio.return_value.get_device_count.return_value = 0

        from RealRNG.RealRNG import RealRNG
        rng = RealRNG()
        result = rng.getRand()

        assert isinstance(result, float)
        rng.end()


def test_rng_getrand_in_range():
    """
    Test that getRand() returns a value between 0 and 1.

    This is the fundamental requirement for a normalized RNG.
    """
    with patch('pyaudio.PyAudio') as mock_pyaudio:
        mock_pyaudio.return_value.get_device_count.return_value = 0

        from RealRNG.RealRNG import RealRNG
        rng = RealRNG()

        # Test multiple calls
        for _ in range(10):
            result = rng.getRand()
            assert 0.0 <= result <= 1.0, f"Value {result} outside [0, 1] range"

        rng.end()


def test_rng_getsource_returns_string():
    """
    Test that getSource() returns a string value.
    """
    with patch('pyaudio.PyAudio') as mock_pyaudio:
        mock_pyaudio.return_value.get_device_count.return_value = 0

        from RealRNG.RealRNG import RealRNG
        rng = RealRNG()
        result = rng.getSource()

        assert isinstance(result, str)
        rng.end()


def test_rng_getsource_valid_values():
    """
    Test that getSource() returns one of the expected source values.
    """
    with patch('pyaudio.PyAudio') as mock_pyaudio:
        mock_pyaudio.return_value.get_device_count.return_value = 0

        from RealRNG.RealRNG import RealRNG
        rng = RealRNG()
        result = rng.getSource()

        assert result in ["microphone", "fallback"]
        rng.end()


def test_rng_fallback_mode_no_microphone():
    """
    Test that RNG uses fallback mode when no microphone is available.

    This verifies the graceful degradation when hardware is unavailable.
    """
    with patch('pyaudio.PyAudio') as mock_pyaudio:
        # Simulate no audio devices
        mock_pyaudio.return_value.get_device_count.return_value = 0

        from RealRNG.RealRNG import RealRNG
        rng = RealRNG()

        # Should use fallback mode
        assert rng.getSource() == "fallback"

        # getRand should still work (using Python's random)
        result = rng.getRand()
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

        rng.end()


def test_rng_microphone_mode_with_device():
    """
    Test that RNG uses microphone mode when a device is available.
    """
    with patch('pyaudio.PyAudio') as mock_pyaudio:
        mock_instance = mock_pyaudio.return_value

        # Simulate one input device
        mock_instance.get_device_count.return_value = 1
        mock_instance.get_device_info_by_index.return_value = {
            'name': 'Mock Microphone',
            'maxInputChannels': 2,
            'defaultSampleRate': 44100.0
        }

        # Configure mock stream with varying data to pass variance check
        mock_stream = MagicMock()
        mock_stream.is_active.return_value = True
        # Return different data each time to simulate real audio variance
        mock_stream.read.side_effect = [
            b'\x01' * 1024,  # Sample 1
            b'\x02' * 1024,  # Sample 2 (different)
            b'\x03' * 1024,  # Sample 3 (different)
            b'\x01\x02\x03\x04\x05\x06\x07\x08',  # For getRand
        ]
        mock_instance.open.return_value = mock_stream

        from RealRNG.RealRNG import RealRNG
        rng = RealRNG()

        # Should detect microphone
        assert rng.microphone_available is True
        assert rng.getSource() == "microphone"

        rng.end()


def test_rng_cleanup():
    """
    Test that end() method cleans up resources properly.
    """
    with patch('pyaudio.PyAudio') as mock_pyaudio:
        mock_instance = mock_pyaudio.return_value
        mock_instance.get_device_count.return_value = 0

        from RealRNG.RealRNG import RealRNG
        rng = RealRNG()
        rng.end()

        # Verify terminate was called
        mock_instance.terminate.assert_called_once()


def test_rng_context_manager():
    """
    Test that RealRNG works as a context manager.

    This verifies proper resource cleanup using with statement.
    """
    with patch('pyaudio.PyAudio') as mock_pyaudio:
        mock_instance = mock_pyaudio.return_value
        mock_instance.get_device_count.return_value = 0

        from RealRNG.RealRNG import RealRNG

        with RealRNG() as rng:
            result = rng.getRand()
            assert isinstance(result, float)

        # After exiting context, terminate should have been called
        mock_instance.terminate.assert_called_once()


def test_rng_multiple_calls_consistent():
    """
    Test that multiple calls to getRand() work correctly.

    Verifies the RNG can be called repeatedly without errors.
    """
    with patch('pyaudio.PyAudio') as mock_pyaudio:
        mock_pyaudio.return_value.get_device_count.return_value = 0

        from RealRNG.RealRNG import RealRNG
        rng = RealRNG()

        results = [rng.getRand() for _ in range(5)]

        # All should be valid floats in range
        for result in results:
            assert isinstance(result, float)
            assert 0.0 <= result <= 1.0

        rng.end()


def test_rng_source_constants():
    """
    Test that RealRNG has the expected source constants.
    """
    with patch('pyaudio.PyAudio') as mock_pyaudio:
        mock_pyaudio.return_value.get_device_count.return_value = 0

        from RealRNG.RealRNG import RealRNG
        rng = RealRNG()

        assert hasattr(rng, 'SOURCE_MICROPHONE')
        assert hasattr(rng, 'SOURCE_FALLBACK')
        assert rng.SOURCE_MICROPHONE == "microphone"
        assert rng.SOURCE_FALLBACK == "fallback"

        rng.end()
