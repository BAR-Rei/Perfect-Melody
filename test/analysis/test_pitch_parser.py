# coding: utf-8
import unittest
import numpy as np
from scipy.signal import medfilt
from music21 import *
from analysis.pitch_parser import PitchParser

class TestPitchParser(unittest.TestCase):
    """ Test class for PitchParser """

    def test_ToMidi(self, pitches=[(440, 69), (1318, 88)]):
        """ params:
                - pitches : list of (Hz pitch, MIDI pitch) couples
            description :
                testDoFFTs() is the unit test function for analysis.pitch_parser.PitchParser.toMidi()
                It tests that each detected pitch in the given list is approximate to the closest midi value.
        """
        for (hz, midi) in pitches:
            self.assertEqual(PitchParser.toMidi([hz]), [midi])


    def test_toNote(self, midi=[69,69,69,23,23,23,23,23,23], sr=22050):
        """ Unitary test for the method PitchParser.toNote().
            It tests that the correct list of notes is returned within the midi input.
            
            params: 
                midi(list) -> the midi input used for the test
        """
        result = []
        result.append({'onset': 0.0, 'duration': 3/float(sr), 'pitch':69})
        result.append({'onset':  3/float(sr), 'duration':6/float(sr), 'pitch':23})
        self.assertEqual(PitchParser.toNote(midi), result)

    def test_removeShortNotes(self):
        """ Unitary test for the  PitchParser.removeShortNotes method
            It tests that the notes under min duration are removed or added to the nearest note.
        """

        notes = []
        notes.append({'onset': 0.0, 'duration': 0.5, 'pitch':69})
        notes.append({'onset': 0.0, 'duration': 0.01, 'pitch':68})
        notes.append({'onset': 0.0, 'duration': 0.5, 'pitch':69})
        notes.append({'onset': 0.0, 'duration': 0.01, 'pitch':23})
        notes.append({'onset': 0.0, 'duration': 0.01, 'pitch':21})

        result = [{'onset': 0.0, 'duration': 1.01, 'pitch':69}]

        self.assertEqual(PitchParser.removeShortNotes(notes), result)

    def test_createScore(self, pulse=24):
        """ unitary test for the PitchParser.createScore method
            It test that the score object is correctly created and containing the correct Note.
        """

        notes = []
        notes.append({'onset': 0.0, 'duration': 2.5, 'pitch':69})
        notes.append({'onset': 0.0, 'duration': 1.25, 'pitch':65})

        score = PitchParser.createScore(notes, pulse)
        self.assertEqual(type(score), stream.Score)

        self.assertEqual(type(score.pop(0)), tempo.MetronomeMark)
        note = score.pop(0)
        self.assertEqual(note.pitch.ps, 69)
        self.assertEqual(note.duration.quarterLength, 1)

        note = score.pop(0)
        self.assertEqual(note.pitch.ps, 65)
        self.assertEqual(note.duration.quarterLength, 0.5)

        # mal codé
        for note in score:
            if note.pitch.ps == 69:
                self.assertEqual(note.duration.quarterLength, 1)
            else:
                self.assertEqual(note.duration.quarterLength, 0.5)