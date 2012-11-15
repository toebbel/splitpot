import unittest
import sys
from datetime import datetime

sys.path.append('controller/')
from DatabaseParser import *

class TestDatabaseParser(unittest.TestCase):

  def setUp(self):
    """
    Called before *each* testcase. We want to operate on a fresh database
    """
    clear()

  def testVerifyLoginOnEmptyDb(self):
    self.assertFalse(verifyLogin("test@0xabc.de", "asfelkj"))

  def testRegister(self):
    self.assertTrue(registerUser("benjamin@flowerpower.org", "Beni", "schokolade"))
    self.assertFalse(registerUser("benJamin@flowerpower.org", "Benjamin", "schokolade"))
    self.assertTrue(registerUser("karlaColumna@bild.de", "Carla", "pwd"))
    self.assertTrue(userExists("benjamin@flowerpower.org"))
    self.assertTrue(userExists("karlaColumna@bild.de"))

  def testListEvents(self):
    registerUser("a", "alpha", "1")
    registerUser("b", "beta", "2")
    registerUser("c", "charlie", "3")
    date_a = datetime.now
    id_a = insertEvent("a", "1.4.2013", 10, ["b"], "Event1")
    print listEvents()
    self.assertEqual(listEvents(), [(id_a, u"a", "1.4.2013", 10, u"['b']", u"Event1")])

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

  def testResetUrl(self):
    registerUser("dummy@0xabc.de", "dummy", "thisIsMyPwd")
    reset = getResetUrlKey("dummy@0xabc.de")
    self.assertTrue(str(reset).__len__() == 8)
    self.assertTrue(isValidResetUrlKey("dummy@0xabc.de", reset))

  def testResetLogin(self):
    registerUser("userA@0xabc.de", "A", "123456")
    registerUser("userB@0xabc.de", "B", "654321")
    self.assertFalse(updateLogin("userC@0xabc.de", "ffffff"))
    self.assertTrue(updateLogin("userb@0xabc.de", "abcdef"))
    self.assertFalse(verifyLogin("userB@0xabc.de", "654321"))
    self.assertTrue(verifyLogin("userB@0xabc.de", "abcdef"))
    self.assertTrue(verifyLogin("userA@0xabc.de", "123456"))

  def testGetEvent(self):
    registerUser("userA@0xabc.de", "A", "123456")
    id = insertEvent("userA@0xabc.de", "10.4.2013", 101.12, ["tobstu@gmail.com"], "comment")
    self.assertEqual(getEvent(id + 1), None)
    self.assertEqual(getEvent(id), (u'userA@0xabc.de', u'10.4.2013', 101.12, u"['tobstu@gmail.com']", u'comment'))

if __name__ == '__main__':
  unittest.main()
