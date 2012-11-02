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
import Encryption

DB_FILE = 'resource/splitpotDB_DEV.sqlite'
SALT_LENGTH = 30

# connects to a given database file
connection = None

class DBParser:

    # instantiate 'connection'
    def connectToDB(self):
        logging.info("connecting to database...")
        global connection
        connection = lite.connect(DB_FILE)

        with connection:
            logging.info("database connection successful.")

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
            # TODO: split participants and create new ghost user for non registered user
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
                salt = Encryption.generateSalt(SALT_LENGTH)
                print "salt: " + salt
                hashedPassword = Encryption.hashPassword(salt, password)
                print "hashed Password: " + hashedPassword

                cur = connection.cursor()
                cur.execute("INSERT INTO splitpot_users VALUES (?, ?, ?, ?)", (email, name, salt, hashedPassword))

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
    x.verifyLogin()
    x.listEvents()
    print x.getPassword("martin@0xabc.de")
    print x.setEventStatus("tobstu@gmail.com", 2, "paid")

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
