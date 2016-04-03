# coding: utf-8
from music21 import *

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition

from gui.scorewidget import ScoreLayout
from gui.button import RecordButton
from gui.popup import AnalyzeInterface

""" This module contains all the screens used in the perfect melody application.
    Major parts of graphical instructions are contained in the perfectmelody.kv file.
"""

class Manager(ScreenManager):
    """ Class handling the transition beetween screens. 
        Contains A RecordScreen and a ScoreScreen.
        A SlideTransition is used and the transition is started when a recording has been completed.
    """
    ANALYZED_FILE = "temp.wav"

    def __init__(self):
        """ Constructor """
        super().__init__()
        self.add_widget(RecordScreen(name='rec'))
        self.add_widget(ScoreScreen(name='score'))

    def analyze(self):
        """ Starts the analysis on the ANALYZED_FILE.
            Once the score is created, it displays it on the score screen
        """
        self.current = 'score'
        popup = AnalyzeInterface(self.current_screen).open()
        

class RecordScreen(Screen):
    """ The application's record screen """
    pass


class ScoreScreen(Screen):
    """ The application's score display screen """
       
    def setScore(self, score=None):
        """ Displays a score on the score widget and defines the score to export/send/play into each button 
            params: 
                score (music21.stream.Score) -> the score to display on the screen.
        """
        self._score = score
        self.ids["_scoreDisplayer"].displayScore(score) 
        self.ids["_emailSender"]._score = self._score
        self.ids["_scoreSaver"]._score = self._score
        self.ids["_MidiPlayer"]._score = self._score
        

class PerfectMelodyApp(App):
    """ Main class in the application.
    """
    def build(self):
        return Manager()

