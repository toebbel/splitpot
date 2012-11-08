import unittest
import sys

sys.path.append('utils/')
import Encryption
enc = Encryption

class TestEncryption(unittest.TestCase):

  def testHashPassword(self):
    self.assertNotEqual(enc.hashPassword("1", "abc"), enc.hashPassword("2", "abc")) #slightly different parameter -> different hashedPwds
    self.assertEqual(enc.hashPassword("1", "abc"), enc.hashPassword("1", "abc"))    #deterministic behavior

  def testGenerateSalt(self):
    self.assertTrue(len(enc.generateRandomChars(1)) == 1)
    self.assertTrue(len(enc.generateRandomChars(40)) == 40)
    self.assertNotEqual(enc.generateRandomChars(10), enc.generateRandomChars(10)) #non-deterministic

if __name__ == '__main__':
  unittest.main()
