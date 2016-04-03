from kivy.uix.popup import Popup
from kivy.uix.label import Label
import sys

""" This module contains the error handling in the perfect melody application. """

class ErrorGUI:
	"""Class handling the display of errors on the user interface."""

	@staticmethod
	def displayError(errorTitle = "Error", message = "An error as Ocurred", windowSize = (300,200)):
		""" Displays a runtime error on the GUI.
			params: 
				errorTitle (str) -> the error's title
				message (str) -> the message to display
				windowSize (tuple) -> the popup's size. Defaults to (300, 200)
		"""
		popupError = Popup(title = errorTitle, content=Label(text = message), size_hint=(None,None), size= windowSize)
		popupError.open()

	@staticmethod
	def fatalError(errorTitle = "Fatal error", message = "A critical error as occured", windowSize = (300,200)):
		""" Displays a fatal error on the GUI. The application is closed thereafter.
			params: 
				errorTitle (str) -> the error's title
				message (str) -> the message to display
				windowSize (tuple) -> the popup's size
		"""
		def _terminate(instance):
			sys.exit()

		popupError = Popup(title = errorTitle, content=Label(text = message + "\n the app is shutting down"), size_hint=(None,None), size= windowSize)
		popupError.bind(on_dismiss = _terminate)
		popupError.open()