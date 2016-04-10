# coding: utf-8
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager

from input_output.recorder import Recorder
from gui.popup import *
import gui.errorGUI as error


class RecordButton(Button):
    """ Starts and stops a recording and saves the wave file. """
   
    def __init__(self, **kwarg):
        """ Creates the recorder and sets the _recording flag to false """
        super().__init__(**kwarg)
        self._recorder = Recorder("temp.wav");
        self._recording = False
        
    def toggle(self):
        """ Starts or stops the recording depending of the value of the  _recording attributes.
            When the recording is stopped, the analysis is launched from the ScreenManager.
        """
        # if the recording has not begun
        if not self._recording:
            try:
                self._recorder.start()
                self._recording=True

            except OSError as e:
                message = "Invalid input device (no default output device)" if e.errno == -9996 else "An error with your setup has occured"
                error.ErrorGUI.fatalError(message = message, windowSize = (400,200))
        # if the recording has begun
        else:
            try:
                self._recording=False
                self._recorder.stop()
            except RuntimeError as e:
                error.ErrorGUI.displayError(errorTitle = "Record error", message="Record too short", windowSize = (400,100))
                return
            except PermissionError as e:
                error.ErrorGui.displayError(errorTitle = "Permission error", message="You are not allowed to save a file here", windowSize = (400,100))

            # Getting ScreenManager 
            screenManager = self.parent
            while not issubclass(type(screenManager), ScreenManager):
                screenManager = screenManager.parent

            screenManager.analyze()


                
class ExportButton(Button):
    """ This Button exports a score to the MIDI format. """

    def exportMidi(self):
        """ Creates a file explorer popup which allows the user to save the file at the desired location. """
        FileInterface(self._score).open()


class EmailButton(Button):
    """ This Button sends an email with a MIDI attachment. """

    def exportEmail(self):
        """ Creates a pop-up object which sends an email to the specified address. """
        EmailInterface(self._score).open()
        

class PlayButton(Button):
    """This Button plays a midi file"""

    def playFile(self):
        """ Creates a pop-up object which plays the midi file in the application """
        PlayInterface(self._score).open()