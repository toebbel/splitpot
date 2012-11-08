# This class has static methods to create salts, and hashes consiting of salt and secret.

import string
import random
import hashlib

CHAR_POOL = string.ascii_uppercase + string.ascii_lowercase + string.digits

  # generates a salt with alphanumeric characters with a given length
def generateRandomChars(length):
  return ''.join(random.choice(CHAR_POOL) for x in range(length))

# create a salted hash value from password and salt
def hashPassword(salt, password):
  return hashlib.sha256(salt + password).hexdigest()
