# coding: utf-8

import unittest
import os

import pyaudio

from input_output.recorder import Recorder

class TestRecorder(unittest.TestCase):
    """ Tests the methods of the Recorder class """

    def setUp(self):
        """ Inits each tests, creating a Recorder object. """
        self.recorder = Recorder("test.wav")

    def test_getFrames(self, testedList = [1,2,3]):
        """ 
            Tests that the getFrames method returns the frames list and reset it. 
            params:     
                testedList -> the list used in the test
        """
        print("Recorder's test")
        self.recorder.frames = testedList
        self.assertEqual(self.recorder.getFrames(), testedList)
        self.assertEqual(len(self.recorder.frames), 0)

    def test_newFrame(self, data=1):
        """ Unitary test for the input_output.recorder.Recorder.newFrame() method.
            Tests that a new frame is created when the newFrame method is called. 
            The return of this method is tested also.
            params: 
                data -> the added data in the test
        """
        self.assertEqual(self.recorder.newFrame(data, 0, 0, 0), (None, pyaudio.paContinue))
        self.assertEqual(self.recorder.frames, [data])


    def test_record(self):
        """ Tests the behaviour of the start and stop methods.
            A recording is started and stopped, the file must be created and must have the WAV format.
        """
        self.recorder.start()
        for i in range(self.recorder.MIN_NUMBER_FRAME):
            self.recorder.frames.append(bytes(i))
        self.recorder.stop()
        self.assertTrue(os.path.exists("test.wav"))
        os.remove("test.wav")


    def recordTooShortCreation(self):
        """ Creates a record too short, this method should raise an RuntimeError. """
        self.recorder.start()
        self.recorder.stop()
        self.assertTrue(os.path.exists("test.wav"))
        os.remove("test.wav")

    def test_recordTooShortException(self):
        """ Tests that an RuntimeException is raised when a record too short is created """
        self.assertRaises(RuntimeError, self.recordTooShortCreation)