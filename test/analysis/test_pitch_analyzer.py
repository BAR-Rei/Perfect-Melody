# coding: utf-8
import unittest
import numpy as np

from analysis.pitch_analyser import PitchAnalyzer
import analysis.lib.amfm_decompy.pYAAPT as pyaapt

class TestPitchAnalyzer(unittest.TestCase):
    """ Tests the methods of PitchAnalyzer Class"""

    def test_pyaapt(self, fileName="test/toast.wav", windowDuration=0.015):
        """ Unitary tests for the analysis.pitch_analyzer.PitchAnalyzer.yaapt() methode.
            It should return a PitchObj containing a ndarray named values.
        """
        pitch = PitchAnalyzer.yaapt(fileName, windowDuration)
        self.assertEqual(type(pitch), pyaapt.PitchObj)
        self.assertEqual(type(pitch.values), np.ndarray)

    def test_detectPitch(self, fileName="test/toast.wav", windowDuration=0.015):
        """ Tests the return of the analysis.pitch_analyzer.PitchAnalyzer.detectPitch() method.
            It should return a ndarray containing the estimated pitches.
        """
        pitch = PitchAnalyzer.detectPitch(fileName, windowDuration)
        yaaptPitch = PitchAnalyzer.yaapt(fileName, windowDuration)
        self.assertEqual(type(pitch), np.ndarray)
        self.assertEqual(len(pitch), len(yaaptPitch.values))
