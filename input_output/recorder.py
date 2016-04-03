# coding: utf-8
import pyaudio
import wave
import threading
import atexit
from analysis.pitch_analyser import PitchAnalyzer

""" Module used to start and stop a recording. When the recording is stopped, a wave file is created at the given file name. """

class Recorder(object):
    """ Allows to start a record from a microphone and to stop it later.
        When the record is stopped, a WAV file is created.
    """

    MIN_NUMBER_FRAME = 5

    def __init__(self, fileName, rate=22050, chunksize=1024, channels=1):
        """ Constructor
            params:
                fileName (str) -> name of the created wav file
                rate(int) -> the recording's sampling rate
                chunksize(int) -> buffer's size
                channels(int) -> recording's number of channels
        """
        self.fileName = fileName
        self.rate = rate
        self.chunksize = chunksize
        self.channels = channels
        self.p = pyaudio.PyAudio()
        self.frames = [] 


    def newFrame(self, data, frame_count, time_info, status):
        """ Creates a new frame and adds it to data saved.
            None and continue order is returned
            params: 
                data (int) -> the new data to add
                frame_count (int) -> number of frames
                time_info -> time information
                status -> status information
            return: 
                Returns the tuple (None, pyaudio.paContinue) to make the record continue
        """
        self.frames.append(data)
        return None, pyaudio.paContinue
    
    def getFrames(self):
        """ Returns the frames and resets their values. """
        frames = self.frames
        self.frames = []
        return frames
    

    def start(self, *args):
        """ Starts the recording
            params:
                args -> some args can be given to the function, like the pressed button.
        """
        self.stream = self.p.open(format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunksize,
            stream_callback=self.newFrame)
        self.stream.start_stream()

    def stop(self, *args):
        """ Stops the recording and saves the wav file.
            params: 
                args -> some args can be given to the function, like the pressed button.
        """
        self.stream.close()

        frames = self.getFrames()
        if(len(frames) < self.MIN_NUMBER_FRAME):
            raise RuntimeError("Record too short")

        # creation of the wav file
        waveFile = wave.open(self.fileName, 'wb')
        waveFile.setnchannels(self.channels)
        waveFile.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
        waveFile.setframerate(self.rate)
        waveFile.writeframes(b''.join(frames))
        waveFile.close()
