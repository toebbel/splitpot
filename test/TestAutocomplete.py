#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import sys

sys.path.append('controller/')
from Autocomplete import *
from DatabaseParser import clear

import json


class TestAutocomplete(unittest.TestCase):
    def setUp(self):
        clear()
    
    def testInvalidRequest(self):
        self.assertEqual(autocomplete(';DROP *'), json.dumps([]))

if __name__ == '__main__':
    unittest.main()
