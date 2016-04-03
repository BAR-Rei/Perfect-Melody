# coding: utf-8
from music21 import *
import os

from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
from kivy.uix.progressbar import ProgressBar
from kivy.properties import ObjectProperty
from kivy.clock import mainthread

from analysis.analyzer import Analyzer
from input_output.email import Email

import gui.errorGUI as error

import pygame

""" This module contains all the popups used in the PerfectMelody application.
    Graphical instructions are contained in perfectmelody.kv.
"""

class AnalyzeInterface(Popup):
    """ Analysis pop-up. Starts the analysis and displays its progression.
        Can't be dismissed before the end of the analysis.
    """

    score = ObjectProperty()
    progression = ObjectProperty()

    def __init__(self, parent):
        """ Constructor.
            Binds score and progress bar events. 
            params: 
                parent (Screen) -> the screen on which the popup is displayed
        """
        super().__init__()
        self._screen = parent
        self.bind(score=self.setScore)
        self.bind(progression=self.setProgress)

    def analyze(self, fileName="temp.wav"):
        """ Starts the analysis in an other thread.
            params: 
                fileName (str) -> the file to analyze
        """
        analyzer = Analyzer(fileName, self)
        analyzer.analyze()

    @mainthread
    def setScore(self, *args):
        """ Sets the score on the current screen and dismisses the popup.
            This method should be executed by the main Kivy thread and is called when score value has changed
            params:
                *args -> This method is called automatically and Kivy passes unused params.
        """
        self._screen.setScore(self.score)
        self.dismiss()

    @mainthread
    def setProgress(self, *args):
        """ Sets the progress of the analysis in a progress bar and label.
            This method should be executed in Kivy's main thread and is called when progression has changed.
            params:
                *args -> This method is called automatically and Kivy passes unused params.
        """
        self.ids["progress"].value = self.progression[0]
        self.ids["label"].text = self.progression[1]



class FileInterface(Popup):
    """ FileChooser pop up. Allows to set a location for the MIDI file """

    def __init__(self, score):
        """ Constructor.
            params: 
                score (stream.Score) -> the score to export
        """
        super().__init__()
        self.score = score

    def getUserInput(self):
        """ Saves the midi file at the choosen location.
            The file name is completed with a (n) if the choosen name already exists.
            The popup is automatically closed after the execution of this method
        """
        fileName = self.ids["textInput"].text
        
        fileName = os.path.join(self.ids["fileChooser"].path, fileName)
        
        i = 1
        temp = fileName
        while os.path.exists(temp + '.mid'):
            temp = fileName + '('+str(i)+')'
            i+=1

        fileName = temp + '.mid'
        try:
            self.score.write("midi", fileName)
        except PermissionError:
            error.ErrorGUI.displayError("You are not allowed to save this file here")
        self.dismiss()    


class EmailInterface(Popup):
    """ Email sender pop up. Allows to send a email containing a midi file. """

    email_recipient = StringProperty()
    email_subject = StringProperty()
    email_password = StringProperty()

    def __init__(self, score):
        """ Constructor
            params: score (music21.stream.Score) -> the score to send
        """
        super().__init__()
        self.score = score

    def send_email(self):
        """ Sends the e-mail at the choosen adress. The sender and receiver use the same adress.
            Neither adress nor password are saved in the application.
            The popup is automatically closed after the e-mail has been sent.
        """
        addr = self.email_recipient
        subject = self.email_subject
        password = self.email_password
        Email.write_email(addr, password,  self.score, email_subject = subject)

        self.dismiss()


class PlayInterface(Popup):
    """ Midi player popup. Handles the playing of a midi file in the application.  """

    def __init__(self, score):
        """ Sets the score to export at midi format.
            params: score (music21.stream.Score) -> the score to play
        """
        super().__init__()
        self.score = score

    def playMidiFile(self):
        """ Play the MIDI file associated to the score argument.
            The score is exported to a midi file and played by the application.
            Then, the file is removed and the pop up is automatically closed.

            This code is inspired by https://www.daniweb.com/programming/software-development/code/216979/embed-and-play-midi-music-in-your-code-python.
        """

        self.score.write("midi", "temp.mid")

        freq = 44100    # audio CD quality
        bitsize = -16   # unsigned 16 bit
        channels = 2    # 1 is mono, 2 is stereo
        buffr = 1024    # number of samples

        # initialisation of the reading
        pygame.mixer.init(freq, bitsize, channels, buffr)
        pygame.mixer.music.set_volume(0.8)

        # variable use to check if the playing has finished
        clock = pygame.time.Clock()

        # loading of the midi file
        pygame.mixer.music.load("temp.mid")
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            # check if playback has finished
            clock.tick(30)

        os.remove("temp.mid")
        self.dismiss()
        