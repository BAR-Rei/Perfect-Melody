# coding: utf-8
from builtins import staticmethod

import music21
import music21.audioSearch as m21

import analysis.lib.amfm_decompy.pYAAPT as pyaapt
import analysis.lib.amfm_decompy.pyQHM as pyqhm
import analysis.lib.amfm_decompy.basic_tools as basic
import matplotlib.pyplot as pplt

import librosa

import numpy as np

from analysis.fft_pda import FFT_PitchDetector
from analysis.pitch_cleaner import PitchCleaner
from analysis.pitch_parser import PitchParser

class PitchAnalyzer :
    """ description :
            This class is a toolbox containing static methods for pitch detection.
            The intended use of this class is calling detectPitch() which will run multiple
            Pitch Detection Algorithms (PDA) and cross-examine the results to determine the
            most probable pitch.
            However, calling other methods directly is not deprecated, as one may want to
            apply a specific PDA to their file.
    """

    PYAAPT_WEIGHT = 2
    FFTPDA_WEIGHT = 1

    @staticmethod
    def detectPitch(fileName, windowDuration=0.075):
        """ params :
                - fileName (str) : Name of the file of interest
                    Defaults to "toast.wav"
                - windowDuration (float) : duration of the windows used by PDAs (in seconds)
                    Defaults to 0.075
            return :
                - data : A list of pitches
            description :
                detectPitch() will apply various pitch detection algorithms to the signal in the file
                described by fileName, compare results, and determine the best estimate for each window.
                The best pitch estimation for each window +is saved in a list which is the return value.
        """
        ## Multi-expert's idea
        # Each PDA is called, it result and weight are stored in a list.
        # Using results and weight, a vote is setled and decides the true value
        
        pitches = []
        pitches.append([PitchAnalyzer.yaapt(fileName, windowDuration, f0_max=2500, bp_high=3000).values, PitchAnalyzer.PYAAPT_WEIGHT])
        #pitches.append([PitchAnalyzer.fftPDA(fileName, windowDuration), PitchAnalyzer.FFTPDA_WEIGHT])

        # Approximation of pitches
        for i in range(len(pitches)):
            pitches[i][0] = PitchParser.toMidi(pitches[i][0])

        # Data creation
        data = pitches[0][0].copy()
        for i in range(len(data)):
            values = []

            # Regroup all values for frame i
            for element in pitches:
                weight = element[1]
                result = element[0]
                for j in range(weight):
                    values.append(result[i])

            # adds the most seen element
            data[i] = max(set(values), key=values.count)

        return data

    @staticmethod
    def detectTempo(fileName):
        """ Detects the tempo used in the file name using the beat_track method of librosa.
            params:
                fileName (str) -> the file name used for tempo extraction
            returns:
                the extracted tempo
        """
        y, sr = librosa.load(fileName)
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
        return tempo

    @staticmethod
    def show(array):
        """ This method displays a plot of the array parameter
            params: 
                array(ndarray) -> the array to plot
        """
        pplt.plot(array)
        pplt.show()


    @staticmethod
    def yaapt(fileName, windowDuration, **kwargs):
        """ params :
                - fileName (str) : Name of the file of interest
                - windowDuration (float) : duration of the windows used by PDAs (in seconds)
            return :
                - pitch : A PitchObj containing the list of pitches.
            description :
                yaapt() will apply the YAAPT PDA to the signal in the file
                described by fileName and return the result as a PitchObj.
                yaapt() uses amfm_decompy's pYAAPT.
        """
        # Create the signal object.
        signal = basic.SignalObj(fileName)
        # Initialize the window
        window = pyqhm.SampleWindow(windowDuration, signal.fs)
        # Create the pitch object and calculate its attributes.
        pitch = pyaapt.yaapt(signal, **kwargs)

        # Set the number of modulated components.
        #signal.set_nharm(pitch.values, 25)
        return pitch;

    @staticmethod
    def fftPDA(fileName, windowDuration):
        """ params :
                - fileName (str) : Name of the file of interest
                - windowDuration (float) : duration of the windows used by PDAs (in seconds)
            return :
                - pitches : A list of pitches.
            description :
                fftPDA() will apply a PDA based solely on the FFT to the signal in the
                file described by fileName and return the result as a list of pitches.
        """
        pitches = FFT_PitchDetector.trackPitch(fileName=fileName, windowSize=44100*windowDuration)
        return pitches;

if __name__ == '__main__':
    PitchAnalyzer.detectPitch();
