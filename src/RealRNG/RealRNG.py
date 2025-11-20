import pyaudio
import hashlib

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

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
        self.audio = pyaudio.PyAudio()
        self.stream:pyaudio.Stream | None = None
        self.max_num = 2**256
        
        self.SOURCE_MICROPHONE = "microphone"
        self.SOURCE_FALLBACK = "fallback"

    def getRand(self)->float:
        try:
            num = self._hashInput()/self.max_num
            return num
        except:
            from random import Random
            r = Random()
            return r.random()

    def getSource(self)->str:
        if not self.stream:
            # try to get microphone again
            self.audio.terminate()
            self.audio = pyaudio.PyAudio()
        try:
            self.stream = self.audio.open(format=FORMAT,
                                    channels=CHANNELS,
                                    rate=RATE,
                                    input=True,
                                    frames_per_buffer=CHUNK)
            return self.SOURCE_MICROPHONE
        except:
            self.stream = None
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
    def _hashInput(self)->int:
        if not self.stream:
            if self.getSource() == self.SOURCE_FALLBACK:
                raise RealRNGError(0)
        try:
            data = self.stream.read(4)
            self.stream.stop_stream()
            return int(hashlib.sha256(data).hexdigest(),16)
        except:
            raise RealRNGError(0)

    def end(self):
        if self.stream:
            self.stream.close()
        self.audio.close()
            
# selfTest
if __name__ == "__main__":
    import time
    realRNG = RealRNG()
    for i in range(100):
        print(realRNG.getSource())
        print(realRNG.getRand())
        time.sleep(1)
    realRNG.selfTest()