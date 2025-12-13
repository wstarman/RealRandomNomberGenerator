import pyaudio
import hashlib
import logging
import os
import sys

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

class SuppressStderr:
    """Context manager to suppress stderr (ALSA errors)"""
    def __enter__(self):
        self.null_fd = os.open(os.devnull, os.O_RDWR)
        self.save_fd = os.dup(2)
        os.dup2(self.null_fd, 2)
        return self

    def __exit__(self, *_):
        os.dup2(self.save_fd, 2)
        os.close(self.null_fd)
        os.close(self.save_fd)

class RealRNGError(Exception):
    def __init__(self,code):
        self.code = code
        self.messageTable = {
            0:"No audio input detected"
        }
    def __str__(self):
        return self.messageTable[self.code]

class RealRNG:
    def __init__(self):
        logger.info("Initializing RealRNG")

        # Check for debug mode
        if os.environ.get('REALRNG_DEBUG'):
            logger.setLevel(logging.DEBUG)
            logger.debug("Debug logging enabled")

        with SuppressStderr():
            self.audio = pyaudio.PyAudio()

        self.stream = None
        self.max_num = 2**256

        self.SOURCE_MICROPHONE = "microphone"
        self.SOURCE_FALLBACK = "fallback"

        # Recovery mechanism tracking
        self.last_retry_attempt = None
        self.retry_interval = 30  # seconds between recovery attempts

        # Find working device at startup
        self.device_index = self._find_working_device()
        self.microphone_available = (self.device_index is not None)

        if self.microphone_available:
            logger.info(f"RealRNG initialized with microphone (device {self.device_index})")
        else:
            logger.warning("RealRNG initialized in fallback mode (no microphone)")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end()
        return False

    def _enumerate_devices(self):
        """List all available input devices"""
        devices = []
        with SuppressStderr():
            device_count = self.audio.get_device_count()
            logger.info(f"Found {device_count} audio devices")

            for i in range(device_count):
                try:
                    info = self.audio.get_device_info_by_index(i)
                    if info['maxInputChannels'] > 0:
                        devices.append({
                            'index': i,
                            'name': info['name'],
                            'channels': info['maxInputChannels'],
                            'sample_rate': int(info['defaultSampleRate'])
                        })
                        logger.debug(f"Input device {i}: {info['name']}")
                except Exception as e:
                    logger.debug(f"Error querying device {i}: {e}")

        return devices

    def _validate_audio_variance(self, samples: list) -> bool:
        """
        Validate that audio samples contain actual variance.

        This prevents selecting devices that only output silence or constant data,
        which would cause the RNG to always return the same hash value.

        Args:
            samples: List of raw audio byte data

        Returns:
            True if samples show variance, False if silent/constant
        """
        if not samples:
            logger.debug("No samples to validate")
            return False

        # Check 1: At least one sample is non-zero
        all_zero = all(sample == b'\x00' * len(sample) for sample in samples)
        if all_zero:
            logger.debug("All samples are zero (silence)")
            return False

        # Check 2: Samples are not all identical (need at least 2 unique)
        unique_samples = len(set(samples))
        if unique_samples < 2:
            logger.debug(f"Only {unique_samples} unique sample(s) - no variance detected")
            return False

        # Passed variance checks
        logger.debug(f"Audio variance validated: {unique_samples} unique samples")
        return True

    def _test_device(self, device_index):
        """
        Test if a device can be opened and produces varying audio data.

        Captures multiple samples and validates that they contain actual variance,
        not just silence or constant data.
        """
        try:
            with SuppressStderr():
                test_stream = self.audio.open(
                    format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    input_device_index=device_index,
                    frames_per_buffer=CHUNK,
                    start=False
                )
                test_stream.start_stream()

                # Capture 3 samples to test for variance
                samples = []
                for i in range(3):
                    data = test_stream.read(CHUNK, exception_on_overflow=False)
                    samples.append(data)

                    # Show sample preview in debug mode
                    if logger.isEnabledFor(logging.DEBUG):
                        preview = data[:16].hex() if len(data) >= 16 else data.hex()
                        logger.debug(f"Device {device_index} sample {i+1}: {preview}")

                test_stream.stop_stream()
                test_stream.close()

            # Validate audio variance
            if not self._validate_audio_variance(samples):
                logger.info(f"Device {device_index} rejected: no audio variance (likely silent or inactive)")
                return False

            logger.info(f"Device {device_index} test successful: audio variance confirmed")
            return True

        except Exception as e:
            logger.debug(f"Device {device_index} test failed: {type(e).__name__}")
            return False

    def _find_working_device(self):
        """Find a working input device"""
        # Check for manual device override
        manual_device = os.environ.get('REALRNG_DEVICE_INDEX')
        if manual_device is not None:
            try:
                device_index = int(manual_device)
                logger.info(f"Testing manually specified device {device_index}")
                if self._test_device(device_index):
                    logger.info(f"Using manually specified device {device_index}")
                    return device_index
                else:
                    logger.warning(f"Manually specified device {device_index} failed")
            except ValueError:
                logger.warning(f"Invalid REALRNG_DEVICE_INDEX: {manual_device}")

        # Auto-detect working device
        logger.info("Auto-detecting working audio device...")
        devices = self._enumerate_devices()

        for device in devices:
            logger.debug(f"Testing device {device['index']}: {device['name']}")
            if self._test_device(device['index']):
                logger.info(f"Found working device {device['index']}: {device['name']}")
                return device['index']

        logger.warning("No working audio devices found")
        return None

    def getRand(self) -> float:
        try:
            num = self._hashInput() / self.max_num
            return num
        except RealRNGError:
            logger.debug("Using fallback random number generator")
            from random import Random
            r = Random()
            return r.random()
        except Exception as e:
            logger.warning(f"Unexpected error in getRand: {e}, using fallback")
            from random import Random
            r = Random()
            return r.random()

    def getSource(self) -> str:
        # Try to recover from previous failure periodically
        if not self.microphone_available:
            import time
            current_time = time.time()

            if (self.last_retry_attempt is None or
                current_time - self.last_retry_attempt > self.retry_interval):

                logger.info("Attempting to recover microphone connection...")
                self.last_retry_attempt = current_time

                # Re-scan for working device
                self.device_index = self._find_working_device()
                self.microphone_available = (self.device_index is not None)

                if self.microphone_available:
                    logger.info(f"Microphone recovered on device {self.device_index}")
                else:
                    logger.debug("Microphone still unavailable")
                    return self.SOURCE_FALLBACK
            else:
                return self.SOURCE_FALLBACK

        # If stream exists and active, return microphone
        if self.stream and self.stream.is_active():
            return self.SOURCE_MICROPHONE

        # Try to open stream with cached device index
        try:
            with SuppressStderr():
                self.stream = self.audio.open(
                    format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    input_device_index=self.device_index,
                    frames_per_buffer=CHUNK
                )
            logger.debug("Microphone stream opened successfully")
            return self.SOURCE_MICROPHONE

        except Exception as e:
            logger.warning(f"Failed to open microphone: {type(e).__name__}: {e}")
            self.stream = None
            self.microphone_available = False
            return self.SOURCE_FALLBACK

    # private method
    def _hashInput(self) -> int:
        # Check stream is ready before reading
        if not self.stream or not self.stream.is_active():
            if self.getSource() == self.SOURCE_FALLBACK:
                raise RealRNGError(0)

        try:
            data = self.stream.read(4, exception_on_overflow=False)
            hash_value = int(hashlib.sha256(data).hexdigest(), 16)
            logger.debug("Generated hash from microphone input")
            return hash_value

        except IOError as e:
            logger.error(f"IOError reading from microphone: {e}")
            raise RealRNGError(0)
        except Exception as e:
            logger.error(f"Unexpected error reading from microphone: {type(e).__name__}: {e}")
            raise RealRNGError(0)

    def end(self):
        """Clean up resources - safe to call multiple times"""
        logger.debug("Cleaning up RealRNG resources")

        # Close stream
        if hasattr(self, 'stream') and self.stream:
            try:
                if self.stream.is_active():
                    self.stream.stop_stream()
                self.stream.close()
                self.stream = None
            except Exception as e:
                logger.warning(f"Error closing stream: {e}")

        # Terminate PyAudio
        if hasattr(self, 'audio') and self.audio:
            try:
                self.audio.terminate()
                self.audio = None
            except Exception as e:
                logger.warning(f"Error terminating PyAudio: {e}")

    @staticmethod
    def list_devices():
        """List all available audio input devices"""
        print("Available audio input devices:")
        print("-" * 60)

        with SuppressStderr():
            audio = pyaudio.PyAudio()
            device_count = audio.get_device_count()

            for i in range(device_count):
                try:
                    info = audio.get_device_info_by_index(i)
                    if info['maxInputChannels'] > 0:
                        print(f"Device {i}: {info['name']}")
                        print(f"  Channels: {info['maxInputChannels']}")
                        print(f"  Sample Rate: {int(info['defaultSampleRate'])} Hz")
                        print()
                except Exception:
                    pass

            audio.terminate()

if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(
        description='RealRNG - True Random Number Generator',
        epilog='For running tests, use: python -m unittest discover tests'
    )
    parser.add_argument('--list-devices', action='store_true',
                       help='List all available audio input devices')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug logging')

    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    if args.list_devices:
        RealRNG.list_devices()
        sys.exit(0)

    # If no arguments, show help
    parser.print_help()