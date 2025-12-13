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

        # Find working device at startup
        self.device_index = self._find_working_device()
        self.microphone_available = (self.device_index is not None)

        if self.microphone_available:
            logger.info(f"RealRNG initialized with microphone (device {self.device_index})")
        else:
            logger.warning("RealRNG initialized in fallback mode (no microphone)")

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

    def _test_device(self, device_index):
        """Test if a device can be opened and read from"""
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
                data = test_stream.read(1, exception_on_overflow=False)
                test_stream.stop_stream()
                test_stream.close()

            logger.info(f"Device {device_index} test successful")
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
        # If microphone unavailable, return fallback immediately
        if not self.microphone_available:
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

    def selfTest(self):
        import matplotlib.pyplot as plt
        numbers = []
        for i in range(10000):
            numbers.append(self.getRand())
        plt.hist(numbers, bins=64, edgecolor='black')
        plt.title("Number Distribution")
        plt.xlabel("Value")
        plt.ylabel("Count")
        plt.show()

    # private method
    def _hashInput(self) -> int:
        if not self.stream:
            if self.getSource() == self.SOURCE_FALLBACK:
                raise RealRNGError(0)

        try:
            data = self.stream.read(4, exception_on_overflow=False)
            self.stream.stop_stream()
            hash_value = int(hashlib.sha256(data).hexdigest(), 16)
            logger.debug("Generated hash from microphone input")
            return hash_value

        except IOError as e:
            logger.error(f"IOError reading from microphone: {e}")
            if self.stream:
                self.stream.stop_stream()
            raise RealRNGError(0)
        except Exception as e:
            logger.error(f"Unexpected error reading from microphone: {type(e).__name__}: {e}")
            if self.stream:
                self.stream.stop_stream()
            raise RealRNGError(0)

    def end(self):
        """Clean up resources"""
        logger.debug("Cleaning up RealRNG resources")
        try:
            if self.stream:
                if self.stream.is_active():
                    self.stream.stop_stream()
                self.stream.close()
        except Exception as e:
            logger.warning(f"Error closing stream: {e}")

        try:
            self.audio.terminate()
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

# selfTest
if __name__ == "__main__":
    import sys
    import argparse
    import time

    parser = argparse.ArgumentParser(description='RealRNG - True Random Number Generator')
    parser.add_argument('--list-devices', action='store_true',
                       help='List all available audio input devices')
    parser.add_argument('--test', action='store_true',
                       help='Run RNG test (100 samples)')
    parser.add_argument('--selftest', action='store_true',
                       help='Run comprehensive self-test with histogram')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug logging')

    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    if args.list_devices:
        RealRNG.list_devices()
        sys.exit(0)

    realRNG = RealRNG()

    if args.test:
        print("Testing RNG (100 samples)...")
        for i in range(100):
            source = realRNG.getSource()
            rand = realRNG.getRand()
            print(f"{i+1}. Source: {source}, Random: {rand:.6f}")
            time.sleep(0.1)
    elif args.selftest:
        realRNG.selfTest()
    else:
        parser.print_help()

    realRNG.end()