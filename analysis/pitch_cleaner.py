# coding: utf-8

from numpy import *
from scipy.signal import medfilt
from music21 import *
from itertools import chain, islice

class PitchCleaner:
    """ Cleans up an array of pitches, to make the note decomposition easier. 
        Toolbox class, containing only static methods.
    """

    @staticmethod
    def trim(pitches):
        """ Trims the detected pitches, removing silence at the end and beginning of the array of detected pitches.
            params:
                pitches(list): the list of pitches which may contain residual empty data at the end or the beginning
            returns:
                the list of pitches without the silence at the end and the beginning 
        """
        i = 0
        # allows to remove the first pitches for which the frequencies == 0
        while((i<len(pitches)) and (pitches[i] == 0)):
            i+=1

        pitches = pitches[i:]

        i = 0

        lengthPitch = len(pitches)
        # allows to remove the last pitches for which the frequencies ==0
        while((i<lengthPitch) and (pitches[(lengthPitch - i - 1)] == 0)):
            i+=1

        pitches = pitches[:lengthPitch-i]
        return pitches


    @staticmethod
    def smooth(pitches, smooth=0.1, sr=22050):
        """ Applies a median filter to smooth the detected pitches 
            params:
                smooth (float) -> length of the mediane filter
                sr (int) -> the used sampling rate
            returns:
                 a list of smoothed pitches
        """
        filter_duration = smooth # in seconds
        filter_size = int(filter_duration * sr)
        if filter_size % 2 == 0:
            filter_size += 1
        
        return medfilt(pitches, filter_size)
  