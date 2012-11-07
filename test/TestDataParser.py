import unittest
import sys
from datetime import datetime

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

  @unittest.skip("interface not finished")
  def testListEvents(self):
    db.registerUser("a", "alpha", "1")
    db.registerUser("b", "beta", "2")
    db.registerUser("c", "charlie", "3")
    date_a = datetime.now
    id_a = db.insertEvent("a", str(date_a), 10, ["b"], "Event1")
    print db.listEvents()
    self.assertTrue(db.listEvents() == [(id_a, str(date_a), "Event1")])


if __name__ == '__main__':
  unittest.main()
