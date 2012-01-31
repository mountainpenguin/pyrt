#!/usr/bin/env python
'''
Core module of Cheetah's Unit-testing framework

TODO
================================================================================
# combo tests
# negative test cases for expected exceptions
# black-box vs clear-box testing
# do some tests that run the Template for long enough to check that the refresh code works
'''

import sys
import unittest

from modules.Cheetah.Tests import SyntaxAndOutput
from modules.Cheetah.Tests import NameMapper
from modules.Cheetah.Tests import Misc
from modules.Cheetah.Tests import Filters
from modules.Cheetah.Tests import Template
from modules.Cheetah.Tests import Cheps
from modules.Cheetah.Tests import Parser
from modules.Cheetah.Tests import Regressions
from modules.Cheetah.Tests import Unicode
from modules.Cheetah.Tests import CheetahWrapper
from modules.Cheetah.Tests import Analyzer

SyntaxAndOutput.install_eols()

suites = [
   unittest.findTestCases(SyntaxAndOutput),
   unittest.findTestCases(NameMapper),
   unittest.findTestCases(Filters),
   unittest.findTestCases(Template),
   #unittest.findTestCases(Cheps),
   unittest.findTestCases(Regressions),
   unittest.findTestCases(Unicode),
   unittest.findTestCases(Misc),
   unittest.findTestCases(Parser),
   unittest.findTestCases(Analyzer),
]

if not sys.platform.startswith('java'):
    suites.append(unittest.findTestCases(CheetahWrapper))

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    if 'xml' in sys.argv:
        import xmlrunner
        runner = xmlrunner.XMLTestRunner(filename='Cheetah-Tests.xml')
    
    results = runner.run(unittest.TestSuite(suites))

