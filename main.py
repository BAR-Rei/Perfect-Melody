# coding: utf-8
from gui.screen import PerfectMelodyApp
import sys

if sys.version_info.major!= 3  or sys.version_info.minor != 4:
    print("\n\nYou are using Python {}.{}. This application requires Python 3.4.".format(sys.version_info.major, sys.version_info.minor))
    input("Press <Enter> to exit")
else:
    PerfectMelodyApp().run()
