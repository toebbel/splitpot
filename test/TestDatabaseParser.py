import unittest

import sys
sys.path.append('controller')
import DatabaseParser
db = DatabaseParser

class TestDatabaseParser(unittest.TestCase):

  def setUp(self):
    db.clear()

  def testListEvents_emptyDB(self):
    listEvents()

  def testGetPassword_NonexistentUser(self):
    getPassword("martin@0xabc.de")

  def testGetPassword(self):
    registerUser("awesome@0xabc.de", "Bluemchen", "blume")
    getPassword("awesome@0xabc.de")

  def testInsertEvent(self):
    registerUser("awesome@0xabc.de", "Bluemchen", "blume")
    insertEvent("awesome@0xabc.de", "4.1.2010", 12.1, ["tobstu@0xabc.de"], "An Event")

  def testSetEventStatus(self):
    setEventStatus("tobstu@gmail.com", 2, "paid")

