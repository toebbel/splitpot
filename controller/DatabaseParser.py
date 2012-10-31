#!/usr/bin/python
#
# Parse database 
#

import sqlite3 as lite
import sys
import random 
import hashlib

DB_FILE = '../resource/splitpotDB_DEV.sqlite'
ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

# connects to a given database file
connection = None

class DatabaseParser:

    # instantiate 'connection'
    def connectToDB(self):
        print "connecting to database..."
        global connection
        connection = lite.connect(DB_FILE)

        with connection:
            print "connection successful."

    def verifyLogin(self):
        print "nothing"

    # returns a list with all events
    def listEvents(self):
        with connection:
            cur = connection.cursor()
            cur.execute("SELECT * FROM splitpot_events")
            events = cur.fetchall()

        return events

    # inserting a new event with the given parameters and return the event ID
    def insertEvent(self, participants, date, owner, amount, comment):
        with connection:
            cur = connection.cursor()   
            cur.execute("INSERT INTO splitpot_events VALUES (?,?,?,?,?,?)", (None, participants, date, amount, owner, comment))
            
            cur.execute("SELECT * FROM splitpot_events ORDER BY ID DESC limit 1")
            eventID = cur.fetchone()[0]
        return eventID 

    # checks if an user already exists
    def userExists(self, email):
        print "check if email: " + email + " exists."
        with connection:
            cur = connection.cursor()
            cur.execute("SELECT count(*) FROM splitpot_users WHERE email = ?", [email])
            exists = cur.fetchone()[0]
        return False if exists == 0 else True

    # register a new user
    def registerUser(self, email, name, password):
        if not self.userExists(email):
            with connection:
                salt = self.createSalt(30)
                print "salt: " + salt
                hashedPassword = self.hashPassword(salt, password)
                print "hashed Password: " + hashedPassword
                
                cur = connection.cursor()
                cur.execute("INSERT INTO splitpot_users VALUES (?, ?, ?, ?)", (email, name, salt, hashedPassword)) 

                return True
        else:
            print "User already exists"
            return False
    
    # create a salt value with a given length 
    def createSalt(self, length):
        salt = ''.join(random.choice(ALPHABET) for i in range(length))
        return salt

    # create a salted hash value from password and salt
    def hashPassword(self, salt, password):
        return hashlib.sha256(salt + password).hexdigest()

def main():
    x = DatabaseParser()
    x.connectToDB()
    x.verifyLogin()
    x.listEvents()
    x.insertEvent("blub, test, uni", "21.01.2012", "martin@dinhmail.de", 33.2, "This is another comment")
    x.registerUser("martin@0xabc.de", "Martin Dinh", "blub")

# call main method
main()
# login
    # email
    # password

# isValidResetUrl
    # email
    # url-key

# setEventStatus
    # ID
    # status
