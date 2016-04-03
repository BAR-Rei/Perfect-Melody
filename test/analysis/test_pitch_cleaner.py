
import unittest
import os

from numpy import *
from music21 import *

from analysis.pitch_cleaner import PitchCleaner

class TestPitchCleaner(unittest.TestCase):
    """ Tests the methods of the PitchCleaner class """

    def test_trim(self):
        """ Unitary test for the PitchCleaner.trim() method.
            This method remove silence at the beginning and end of the detected pitches.
        """
        pitches=[0, 0, 442, 455.1234988, 47.456, 1450.1987426, 0, 25.854, 5199.654, 0, 0, 0]
        self.assertEquals(PitchCleaner.trim(pitches), [442, 455.1234988, 47.456, 1450.1987426, 0, 25.854, 5199.654])