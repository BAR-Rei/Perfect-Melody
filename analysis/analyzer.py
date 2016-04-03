#coding: utf-8
from music21 import *
from analysis.pitch_analyser import PitchAnalyzer
from analysis.pitch_cleaner import PitchCleaner
from analysis.pitch_parser import PitchParser
from threading import Thread
import gui.errorGUI as error

""" This module contains the class that starts the analysis and updates the caller popup."""

class Analyzer:
    """ This class starts the analysis in a different thread and, from this thread, updates the caller popup and the scorewidget. """
   
    def __init__(self, fileName, popup):
        """ Constructor
            params:
                fileName (str) -> the file to analyze
                popup (gui.popup.AnalyzeInterface) -> popup which called the analysis
        """
        super().__init__()
        self.fileName = fileName
        self.score = stream.Score()
        self.popup = popup

    def thread(self):
        """ Runs the analysis and makes the Kivy main thread update progression and results.
            This method is executed in a different thread, in order not to block the GUI.
            This method should not be called directly. Call analyze().
        """
        self.popup.progression = (0, "Détection du tempo")
        try:
            pulse = PitchAnalyzer.detectTempo(self.fileName)
        except IndexError:
            error.ErrorGUI.displayError("IndexError", "the record is too short")
            return
        try:
            self.popup.progression = (10, "Détection des hauteurs")
            midi = PitchAnalyzer.detectPitch(self.fileName)
        except NameError as e:
            error.ErrorGUI.displayError("NameError", "unresolved problem with pYAAPT.py\nlast time it was line 509\nmore on that\n" + str(e.args))
        
        self.popup.progression = (50, "Lissage")
        midi = PitchCleaner.smooth(midi)
        midi = PitchCleaner.trim(midi)

        self.popup.progression = (70, "Création de la partition")
        notes = PitchParser.toNote(midi)
        notes = PitchParser.removeShortNotes(notes)


        score = PitchParser.createScore(notes, pulse)
        final = PitchParser.initMeasure(score)

        self.score = final
        
        self.popup.progression = (100, "Analyse terminée")
        self.popup.score = self.score


    
    def analyze(self):
        """ Starts the complete analysis on the fileName file in a different thread """
        Thread(target=self.thread).start()