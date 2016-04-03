#coding: utf-8
from analysis.analyzer import Analyzer
from gui.popup import AnalyzeInterface
import unittest
import threading

""" Test module for analysis.analyzer module """
class PlaceHolderPopup:
    pass

class TestAnalyzer(unittest.TestCase):
    """ Test class for analysis.analyzer.Analyzer class """
   
    def test_analyze(self):
        """ Unitary test for the analysis.analyzer.Analyzer.analyze() method .
            Tests that two tests are running when the analyse is started. 
        """
        a = Analyzer("analysis/samples/Do3.wav", PlaceHolderPopup)
        try :
            a.analyze()
        except AttributeError:
            pass
        finally :
            self.assertEqual(threading.activeCount(), 2)