#!/usr/bin/python
#
# Parse database
#

import sqlite3 as lite
import sys
import random
import hashlib
import logging

sys.path.append('utils/')
from Encryption import EncryptionHelper

DB_FILE = 'resource/splitpotDB_DEV.sqlite'
SALT_LENGTH = 30

# connects to a given database file
connection = None
log = logging.getLogger("appLog")

class DBParser:

    # instantiate 'connection'
    def connectToDB(self):
        log.info("connecting to database...")
        global connection
        connection = lite.connect(DB_FILE)

        with connection:
            log.info("database connection successful.")

    def verifyLogin(self, email, password):
        log.info("verify user and given password")
        with connection:
            cur = connection.cursor()
            cur.execute("SELECT salt FROM splitpot_users WHERE email = ?", [email])
            userSalt = cur.fetchone()[0] 
            cur.execute("SELECT password FROM splitpot_users WHERE email = ?", [email])
            hashedPw = cur.fetchone()[0]
        return True if (EncryptionHelper.hashPassword(userSalt, password) == hashedPw) else False 

    # returns a list with all events
    def listEvents(self):
        with connection:
            cur = connection.cursor()
            cur.execute("SELECT * FROM splitpot_events")
            events = cur.fetchall()

        return events

    # inserting a new event with the given parameters and return the event ID
    def insertEvent(self, participants, date, owner, amount, comment):
        newUsers = []
        with connection:
            cur = connection.cursor()
            # TODO: split participants and create new ghost user for non registered user
            for email in participants:
                if self.userExists(email):
                    cur.execute("INSERT INTO splitpot_events VALUES (?,?,?,?,?,?)", (None, email, date, amount, owner, comment))
                else:
                    tmpPassword = Encryption.generateSalt(6)
                    self.registerUser(self, email, "Not Registered", tmpPassword) 
                    cur.execute("INSERT INTO splitpot_events VALUES (?,?,?,?,?,?)", (None, email, date, amount, owner, comment))
                    # return dictionaries with email:tmpPassword
                    newUsers.append({email:tmpPassword})

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
                salt = EncryptionHelper.generateSalt(SALT_LENGTH)
                print "salt: " + salt
                hashedPassword = EncryptionHelper.hashPassword(salt, password)
                print "hashed Password: " + hashedPassword

                cur = connection.cursor()
                cur.execute("INSERT INTO splitpot_users VALUES (?, ?, ?, ?, ?)", (email, name, 0, salt, hashedPassword))

                return True
        else:
            print "User already exists"
            return False

    # return hashedPassword
    def getPassword(self, email):
        if self.userExists(email):
            with connection:
                cur = connection.cursor()
                cur.execute("SELECT password FROM splitpot_users WHERE email = ?", [email])
                pw = cur.fetchone()[0]
                return pw
        else:
            print "User doesn't exist"
    
    # set the event status for a given user
    def setEventStatus(self, email, event, status):
        with connection:
            cur = connection.cursor()
            cur.execute("SELECT COUNT(*) FROM splitpot_participants WHERE user = ? AND event = ?", (email, event))
            curEvent = cur.fetchone()[0]
            if curEvent != 0:
                cur.execute("UPDATE splitpot_participants SET status = ? WHERE user = ? AND event = ?", (status, email, event))
                return True
            else:
                print "Event and/or email doesn't exist"

def main():
    x = DBParser()
    x.connectToDB()
    x.registerUser("test@0xabc.de", "Test Account", "Test")
    print x.verifyLogin("test@0xabc.de", "asfelkj")
    print x.verifyLogin("test@0xabc.de", "Test")
    x.listEvents()
    print x.getPassword("martin@0xabc.de")
    print x.setEventStatus("tobstu@gmail.com", 2, "paid")

# call main method
main()

# isValidResetUrl
    # email
    # url-key
