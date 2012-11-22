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

log = logging.getLogger('appLog')

# connects to a given database file

log.info('connecting to database...')
connection = lite.connect(DB_FILE, check_same_thread=False)


def clear():
    """
    Clear *ALL THE FUCKING DATA* from the database.
    """

    log.info('kill database - right now')
    with connection:
        cur = connection.cursor()
        cur.execute('DELETE FROM splitpot_participants')
        cur.execute('DELETE FROM splitpot_events')
        cur.execute('DELETE FROM splitpot_users')


def updateLogin(email, newPassword):
    """
    Update the login for a given user with a given password.
    """

    log.info("resetting the password for user '" + email.lower() + "'")
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
    """
    Check if the given email and password match.
    """

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


def listEvents():
    """
    List all events that are in the database.
    """

    log.info('list all events in database')
    with connection:
        cur = connection.cursor()
        cur.execute('SELECT * FROM splitpot_events')
        events = cur.fetchall()

    return events


def listHostingEventsFor(user):
    """
    List all events of a given user, where the user was the host.
    """

    events = []
    with connection:
        log.info("list all hosting events for '" + user.lower() + "'")
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
                participants=json.loads(curEvent[3]),
                comment=curEvent[4],
                ))
    return events


def listInvitedEventsFor(user):
    """
    List all events of a given user, where the user was the guest.
    """

    events = []
    with connection:
        log.info("list all invited to events for '" + user.lower() + "'"
                 )
        cur = connection.cursor()
        cur.execute('SELECT splitpot_events.ID, owner, date, amount, splitpot_events.participants, comment FROM splitpot_events, splitpot_participants WHERE splitpot_participants.event = splitpot_events.ID AND splitpot_participants.user = ?'
                    , [user.lower()])
        result = cur.fetchall()
        for curEvent in result:
            events.append(Event(
                id=curEvent[0],
                owner=curEvent[1],
                date=curEvent[2],
                amount=-curEvent[3],
                participants=curEvent[4],
                comment=curEvent[5],
                ))

    return events


def listAllEventsFor(user):
    """
    List all events for a given user.
    """

    log.info('list all events for "' + user.lower() + '"')
    return listHostingEventsFor(user) + listInvitedEventsFor(user)


def getEvent(id):
    """
    Return an event with a given id, if existent.
    """

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


def insertEvent(
    owner,
    date,
    amount,
    participants,
    comment,
    ):
    """
    Insert a new event with the given parameters and return the event ID.
    The 'participants' table contains the IDs of the participants
    as a list in JSON format.
    """

    log.info('Owner: ' + owner + ', date: ' + str(date) + ', amount: '
             + str(amount) + ', participants: ' + str(participants)
             + ', comment: ' + comment)

    with connection:
        cur = connection.cursor()
        if not userExists(owner):
            tmpPassword = generateRandomChars(DEFAULT_PWD_LENGTH)
            log.info('owner: ' + owner
                     + ' is not registered yet, registering now.')
            registerUser(owner, 'Not Registered', tmpPassword)

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

        # updateParticipantTable(participants, eventID, 'new')

    return eventID


def updateParticipantTable(participants, eventID, status):
    """
    Update the participant table with a given event and list of participants.
    """

    log.info('update participants table')
    with connection:
        cur = connection.cursor()
        for curParticipant in participants:
            cur.execute('INSERT INTO splitpot_participants VALUES (?, ?, ?)'
                        , (curParticipant, eventID, status))
    return True


def userExists(email):
    """
    Check if a given user already exists.
    """

    log.info('check if email: ' + email + ' exists.')
    with connection:
        cur = connection.cursor()
        cur.execute('SELECT count(*) FROM splitpot_users WHERE email = ?'
                    , [email.lower()])
        exists = cur.fetchone()[0]
    return (False if exists == 0 else True)


def registerUser(email, name, password):
    """
    Register a new user.
    """

    log.info('register user "' + email.lower() + '"')
    if not userExists(email):
        with connection:
            salt = generateRandomChars(SALT_LENGTH)
            hashedPassword = hashPassword(salt, password)

            cur = connection.cursor()
            cur.execute('INSERT INTO splitpot_users VALUES (?, ?, ?, ?, ?)'
                        , (email.lower(), name, 0, salt,
                        hashedPassword))

        return True
    else:
        log.info('"' + email.lower() + '" already exists')
        return False


def getPassword(email):
    """
    Return the hashed password of a given user.
    """

    log.info('get hashed password of "' + email.lower() + '"')
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


def setEventStatus(email, event, status):
    """
    Set the event status for a given user.
    """

    log.info('set event status of "' + email.lower() + '" with id "'
             + str(event) + '" to "' + status + '"')
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

    if userExists(email) and getPassword(email)[:8] == key:
        return True
    else:
        return False


def getResetUrlKey(email):
    """
    ~ for a pwd-reset (forgot pwd feature)
    """

    if userExists(email):
        return getPassword(email)[:8]


def mergeUser(newUser, oldUser):
    """
    Merge to given users.
    """

    log.info('replace "' + oldUser.lower() + '" with "'
             + newUser.lower() + '"')

    with connection:
        cur = connection.cursor()
        if (userExists(newUser) and userExists(oldUser)):
            log.info('replacing every "' + oldUser.lower() + '" with "'
                     + newUser.lower() + ' in events.participants')
            events = listInvitedEventsFor(oldUser)

            for event in events:
                oldParticipants = event.participants
                newParticipants = \
                    oldParticipants.replace(str(oldUser.lower()),
                        str(newUser.lower()))

                cur.execute('UPDATE splitpot_events SET participants = ? WHERE participants = ?'
                            , [newParticipants, oldParticipants])

            log.info('replacing every "' + oldUser.lower() + '" with "'
                     + newUser.lower() + ' in participants table')
            cur.execute('UPDATE splitpot_participants SET user = ? WHERE user = ?'
                        , [newUser.lower(), oldUser.lower()])

            log.info('replacing events where owner is "'
                     + oldUser.lower() + '" with "' + newUser.lower()
                     + '"')
            cur.execute('UPDATE splitpot_events SET owner = ? WHERE owner = ?'
                        , [newUser.lower(), oldUser.lower()])

            log.info('deleting the user "' + oldUser.lower() + '"')
            cur.execute('DELETE FROM splitpot_users WHERE email = ?',
                        [oldUser.lower()])

            return True

    return False


