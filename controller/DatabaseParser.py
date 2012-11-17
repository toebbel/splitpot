#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# Parse database
#

import sqlite3 as lite
import sys
import random
import hashlib
import logging
import json

sys.path.append('utils/')
from Encryption import *
sys.path.append('model/')
from Event import Event

DB_FILE = 'resource/splitpotDB_DEV.sqlite'
SALT_LENGTH = 30
DEFAULT_PWD_LENGTH = 6
ACTIVATE_CODE_LEN = 8

log = logging.getLogger('appLog')

# connects to a given database file

log.info('connecting to database...')
connection = lite.connect(DB_FILE, check_same_thread=False)


def clear():
    """
  Clears *ALL THE FUCKING DATA* from the Database
  """

    log.info('kill database - right now')
    with connection:
        cur = connection.cursor()
        cur.execute('DELETE FROM splitpot_participants')
        cur.execute('DELETE FROM splitpot_events')
        cur.execute('DELETE FROM splitpot_users')


def updateLogin(email, newPassword):
    log.info("resetting the pwd for user '" + email + "'")
    if not userExists(email):
        return False
    with connection:
        cur = connection.cursor()
        salt = generateRandomChars(SALT_LENGTH)
        hashedPwd = hashPassword(salt, newPassword)
        cur.execute('UPDATE splitpot_users SET password = ?, salt = ? WHERE email = ?'
                    , [hashedPwd, salt, email.lower()])
        return cur.rowcount == 1


def verifyLogin(email, password):
    if not userExists(email.lower()):
        return False
    log.info('verify user and given password')
    with connection:
        cur = connection.cursor()
        cur.execute('SELECT salt FROM splitpot_users WHERE email = ?',
                    [email.lower()])
        userSalt = cur.fetchone()[0]
        if userSalt == '':
            return False
        cur.execute('SELECT password FROM splitpot_users WHERE email = ?'
                    , [email.lower()])
        hashedPw = cur.fetchone()[0]

    return (True if hashPassword(userSalt, password)
            == hashedPw else False)


# returns a list with all events

def listEvents():
    with connection:
        cur = connection.cursor()
        cur.execute('SELECT * FROM splitpot_events')
        events = cur.fetchall()

    return events


def listHostingEventsFor(user):
    events = []
    with connection:
        cur = connection.cursor()
        cur.execute('SELECT ID, date, amount, participants, comment FROM splitpot_events WHERE splitpot_events.owner = ?'
                    , [user.lower()])
        result = cur.fetchall()
        for curEvent in result:
            events.append(Event(
                id=curEvent[0],
                owner=str(user),
                date=curEvent[1],
                amount=curEvent[2],
                participants=curEvent[3],
                comment=curEvent[4],
                ))
    return events


def listInvitedEventsFor(user):
    events = []
    with connection:
        cur = connection.cursor()
        cur.execute('SELECT splitpot_events.ID, date, amount, comment, owner FROM splitpot_events, splitpot_participants WHERE splitpot_participants.event = splitpot_events.ID AND splitpot_participants.user = ?'
                    , [user.lower()])
        result = cur.fetchall()
        for curEvent in result:

            # events.append(Event(curEvent[0], "?", curEvent[1], -curEvent[2], "?", curEvent[3]))

            events.append(Event(id=curEvent[0], owner=curEvent[4],
                          date=curEvent[1], amount=-curEvent[2],
                          comment=curEvent[3]))

    return events


def listAllEventsFor(user):
    return listHostingEventsFor(user) + listInvitedEventsFor(user)


def getEvent(id):
    log.info('retrieve event ' + str(id))
    with connection:
        cur = connection.cursor()
        cur.execute('SELECT owner, date, amount, participants, comment FROM splitpot_events where id = ?'
                    , [id])
        e = cur.fetchone()
        if e:
            return Event(
                id=id,
                owner=str(e[0]),
                date=e[1],
                amount=e[2],
                participants=json.loads(e[3]),
                comment=e[4],
                )
        return None


# inserting a new event with the given parameters and return the event ID. "participants" contains the IDs of the participants as list.

def insertEvent(
    owner,
    date,
    amount,
    participants,
    comment,
    ):

    log.info('Owner: ' + owner + ', date: ' + str(date) + ', amount: '
             + str(amount) + ', participants: ' + str(participants)
             + ', comment: ' + comment)

    with connection:
        cur = connection.cursor()
        if not userExists(owner, True):
            tmpPassword = generateRandomChars(DEFAULT_PWD_LENGTH)
            log.info('owner: ' + owner
                     + ' is not registered yet, registering now.')
            registerUser(owner, 'Not Registered', tmpPassword) #TODO I don't think we should allow this

        cur.execute('INSERT INTO splitpot_events VALUES (?,?,?,?,?,?)',
                    (
            None,
            owner,
            date,
            amount,
            json.dumps(participants),
            comment,
            ))

        cur.execute('SELECT * FROM splitpot_events ORDER BY ID DESC limit 1'
                    )
        eventID = cur.fetchone()[0]
        updateParticipantTable(participants, eventID, 'new')
    return eventID


# update the participant table with a given event and list of
# participants

def updateParticipantTable(participants, eventID, status):
    log.info('update participants table')
    with connection:
        cur = connection.cursor()
        for curParticipant in participants:
            cur.execute('INSERT INTO splitpot_participants VALUES (?, ?, ?)'
                        , (curParticipant, eventID, status))
    return True


# checks if an user already exists

def userExists(email, includeGhosts=False):
    log.info('check if email: ' + email + ' exists. isGhost?' + str(includeGhosts))
    with connection:
        cur = connection.cursor()
	if includeGhosts:
	        cur.execute('SELECT count(*) FROM splitpot_users WHERE email = ?', [email.lower()])
	else:
		cur.execute('SELECT count(*) FROM splitpot_users WHERE email = ? AND registered == 0', [email.lower()])
        exists = cur.fetchone()[0]
    return (False if exists == 0 else True)

def registerUser(email):
	if (not userExists(email, True)):
		log.info('register user ' + email)
		with connection:
			activateKey = generateRandomChars(ACTIVATE_CODE_LEN)
			cur = connection.cursor()
			cur.execute('INSERT INTO splitpot_users VALUES (?, ?, 1, ?, ?)', (email.lower(), email, activateKey, activateKey))
		return True
	log.info('did not register ' + email + ' because the email is attached to another user')
	return False

# register a new user

def activateUser(email, name, password, force = False): #activate previously registered user. Force revokes register, if needed.
    log.info('activate user ' + email + ', force ' + str(force))
    if not userExists(email, True) and force:
	registerUser(email)
    if (not userExists(email)): #Only Ghost users can register, or they are new ghosts
        with connection:
            salt = generateRandomChars(SALT_LENGTH)
            hashedPassword = hashPassword(salt, password)

            cur = connection.cursor()
            cur.execute('UPDATE splitpot_users SET name = ?, registered = 0, salt = ?, password = ? WHERE email = ? AND registered != 0'
                        , (name, salt, hashedPassword, email.lower()))

        return True
    else:
	if not userExists(email, True):
        	print 'user is not invited'
	else:
		print 'user already exists' #TODO return this info as result
        return False


# return hashedPassword

def getPassword(email):
    if userExists(email):
        with connection:
            cur = connection.cursor()
            cur.execute('SELECT password FROM splitpot_users WHERE email = ?'
                        , [email])
            pw = cur.fetchone()[0]
            return pw
    else:
        log.warning("Can't return password of " + email
                    + ", because user doesn't exist")


# set the event status for a given user

def setEventStatus(email, event, status):
    with connection:
        cur = connection.cursor()
        cur.execute('SELECT COUNT(*) FROM splitpot_participants WHERE user = ? AND event = ?'
                    , (email, event))
        curEvent = cur.fetchone()[0]
        if curEvent != 0:
            cur.execute('UPDATE splitpot_participants SET status = ? WHERE user = ? AND event = ?'
                        , (status, email, event))
            return True
        else:
            log.warning(str(event) + ' or ' + email + " doesn't exist")


def isValidResetUrlKey(email, key):
    """
    ~ for pwd reset (forgot pwd feature)
    """

    if userExists(email) and getPassword(email)[:ACTIVATE_CODE_LEN] == key:
        return True
    else:
        return False


def getResetUrlKey(email):
    """
    ~ for a pwd-reset (forgot pwd feature)
    """

    if userExists(email):
        return getPassword(email)[:8]


