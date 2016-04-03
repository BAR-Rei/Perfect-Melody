# coding: utf-8

import unittest

runner = unittest.TextTestRunner() 
test = unittest.defaultTestLoader.discover("./")
runner.run(test)

input("Press [ENTER] to continue..")
