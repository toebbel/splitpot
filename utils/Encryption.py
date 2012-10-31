# This class has static methods to create salts, and hashes consiting of salt and secret.

import string
import random
import hashlib

CHAR_POOL = chars=string.ascii_uppercase + string.ascii_lowercase + string.digits

class Encryption(object):
    @staticmethod
    def generateSalt(length):
       return ''.join(random.choice(CHAR_POOL) for x in range(length)) 

    @staticmethod
    # create a salted hash value from password and salt   
    def hashPassword(salt, password):               
        return hashlib.sha256(salt + password).hexdigest()
