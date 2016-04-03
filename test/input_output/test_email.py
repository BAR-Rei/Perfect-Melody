# coding: utf-8

import unittest
import os

import pyaudio

from input_output.email import Email

class TestEmail(unittest.TestCase):
    """ Tests the methods of the Email class """

    def test_extract_server(self):
        """ Unitary test for the input_output.Email.extract_server method. 
        	Tests that the server name is correctly extracted when an email adress is given.
        """
        self.assertEquals(Email.extract_server("toto.toto@hotmail.com"), 'hotmail')
        self.assertEquals(Email.extract_server("toto.toto.com"), '')
        self.assertEquals(Email.extract_server("toto.toto@"), '')
        