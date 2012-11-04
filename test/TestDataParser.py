import unittest
import sys

sys.path.append('controller/')
import DatabaseParser
db = DatabaseParser

class TestDatabaseParser(unittest.TestCase):

  def setUp(self):
    """
    Called before *each* testcase. We want to operate on a fresh database
    """
    db.clear()

  def testVerifyLoginOnEmptyDb(self):
    self.assertFalse(db.verifyLogin("test@0xabc.de", "asfelkj"))

  def testRegister(self):
    self.assertTrue(db.registerUser("benjamin@flowerpower.org", "Beni", "schokolade"))
    self.assertFalse(db.registerUser("benJamin@flowerpower.org", "Benjamin", "schokolade"))
    self.assertTrue(db.registerUser("karlaColumna@bild.de", "Carla", "pwd"))
    self.assertTrue(db.userExists("benjamin@flowerpower.org"))
    self.assertTrue(db.userExists("karlaColumna@bild.de"))






if __name__ == '__main__':
  unittest.main()
