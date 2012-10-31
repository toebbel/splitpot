#!/usr/bin/python
#
# Parse database 
#

import sqlite3 as lite
import sys

DB_FILE = '../resource/splitpotDB_DEV.sqlite'

# connects to a given database file
connection = None

class DatabaseParser:

    def connectToDB(self):
        print "connecting to database..."
        global connection
        connection = lite.connect(DB_FILE)

        with connection:
            print "connection successful."

    def verifyLogin(self):
        print "nothing"

    def listEvents(self):
        with connection:
            cur = connection.cursor()
            cur.execute("SELECT * FROM splitpot_events")
            events = cur.fetchall()

        for row in events:
            print row

    def insertEvent(self, participants, date, owner, amount, comment):
        with connection:
            cur = connection.cursor()   
            cur.execute("INSERT INTO splitpot_events VALUES (?,?,?,?,?,?)", (None, participants, date, owner, amount, comment,))

    def userExists(self, email):
        with connection:
            cur = connection.cursor()
            cur.execute("SELECT ? FROM splitpot_users", [email])
            exists = cur.fetchall()
        
        print True if exists!=None else False

def main():
    x = DatabaseParser()
    x.connectToDB()
    x.verifyLogin()
    x.listEvents()
    x.userExists("martin@dinhmail.de")
    x.insertEvent("blub, test, uni", "21.01.2012", "martin@dinhmail.de", 33.2, "This is another comment")

# call main method
main()
# login
    # email
    # password

# userExists
    # email

# register
    # email
    # passwort

# isValidResetUrl
    # email
    # url-key

# listEvents

# insertEvent
    # ID[]
    # date
    # comment
    # amount
    # owner.ID
    # return Event.ID

# setEventStatus
    # ID
    # status
