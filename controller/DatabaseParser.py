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
import datetime

sys.path.append('utils/')
from Encryption import *
from TransactionGraph import *
sys.path.append('model/')
from Event import Event

DB_FILE = 'resource/splitpotDB.sqlite'
SALT_LENGTH = 30
DEFAULT_PWD_LENGTH = 6
ACTIVATE_CODE_LEN = 8
MERGE_KEY_LEN = 16
DATEFORMAT = '%d-%m-%Y'

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
        cur.execute('DELETE FROM splitpot_autocomplete')


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
                date=datetime.datetime.strptime(curEvent[1],
                        DATEFORMAT),
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
                date=datetime.datetime.strptime(curEvent[2],
                        DATEFORMAT),
                amount=-curEvent[3],
                participants=json.loads(curEvent[4]),
                comment=curEvent[5],
                ))

    return events


def listAllEventsFor(user):
    """
    List all events for a given user.
    """

    log.info('list all events for "' + user.lower() + '"')
    return sorted(listHostingEventsFor(user) + listInvitedEventsFor(user), key = lambda e: e.date, reverse=True)


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
                date=datetime.datetime.strptime(e[1], DATEFORMAT),
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

    if type(date) is datetime.date:
        date = date.strftime(DATEFORMAT)

    log.info('Owner: ' + owner + ', date: ' + str(date) + ', amount: '
             + str(amount) + ', participants: ' + str(participants)
             + ', comment: ' + comment)

    with connection:
        cur = connection.cursor()
        if not userExists(owner, True):
            tmpPassword = generateRandomChars(DEFAULT_PWD_LENGTH)
            log.info('owner: ' + owner
                     + ' is not registered yet, registering now.')
            registerUser(owner, 'Not Registered', tmpPassword)  # TODO I don't think we should allow this

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


def userExists(email, includeGhosts=False):
    """
    Check if a given user already exists.
    """

    log.info('check if email: ' + email + ' exists. isGhost?'
             + str(includeGhosts))
    with connection:
        cur = connection.cursor()
        if includeGhosts:
            cur.execute('SELECT count(*) FROM splitpot_users WHERE email = ?'
                        , [email.lower()])
        else:
            cur.execute('SELECT count(*) FROM splitpot_users WHERE email = ? AND registered == 0'
                        , [email.lower()])
        exists = cur.fetchone()[0]
    return (False if exists == 0 else True)


def registerUser(email):
    if not userExists(email, True):
        log.info('register user ' + email)
        with connection:
            activateKey = generateRandomChars(ACTIVATE_CODE_LEN)
            cur = connection.cursor()
            cur.execute('INSERT INTO splitpot_users VALUES (?, ?, 1, ?, ?)'
                        , (email.lower(), email, activateKey,
                        activateKey))
        return True
    log.info('did not register ' + email
             + ' because the email is attached to another user')
    return False


def activateUser(  # activate previously registered user. Force revokes register, if needed.
    email,
    name,
    password,
    force=False,
    ):

    log.info('activate user ' + email + ', force ' + str(force))
    if not userExists(email, True) and force:
        registerUser(email)
    if not userExists(email):  # Only Ghost users can register, or they are new ghosts
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
            print 'user already exists'  # TODO return this info as result
        return False


def getPassword(email, forGhost=False):
    """
    Return the hashed password of a given user.
    """

    if userExists(email, forGhost):
        with connection:
            cur = connection.cursor()
            cur.execute('SELECT password FROM splitpot_users WHERE email = ?'
                        , [email.lower()])
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


def isValidResetUrlKey(email, key, forGhost=False):
    """
    ~ for pwd reset (forgot pwd feature)
    """

    if userExists(email, forGhost) and getResetUrlKey(email,
            forGhost)[:ACTIVATE_CODE_LEN] == key:
        return True
    else:
        return False


def getResetUrlKey(email, forGhost=False):
    """
    ~ for a pwd-reset (forgot pwd feature)
    """

    if userExists(email, forGhost):
        return getPassword(email, forGhost)[:ACTIVATE_CODE_LEN]


def getMergeUrlKey(newMail, oldMail):
    """
    Generate a key for merge of two accounts.
    """

    log.info('generate key for merging user "' + newMail + '" and "'
             + oldMail + '"')
    key = ''
    if userExists(newMail) and userExists(oldMail, True):
        key += getPassword(newMail)[:MERGE_KEY_LEN / 2]
        key += getPassword(oldMail, True)[:MERGE_KEY_LEN / 2]

    return key


def isValidMergeUrlKey(key):
    """
    Check if a given key is a valid key to merge two accounts.
    """

    log.info('checking if merging key is correct')

    if key != None and len(key) == MERGE_KEY_LEN:
        newMail = getUserFromPassword(key[:MERGE_KEY_LEN / 2])
        oldMail = getUserFromPassword(key[MERGE_KEY_LEN / 2:])
        if newMail != None and oldMail != None:
            return True
    return False


def getUserFromPassword(pwd):
    """
    Return the user to which the pwd is part of the whole password.
    """

    log.info('getting user with following string in password "'
             + str(pwd) + '"')

    with connection:
        cur = connection.cursor()
        cur.execute('SELECT email FROM splitpot_users WHERE password LIKE ?'
                    , [pwd + '%'])
        user = cur.fetchone()

        return (user[0] if user else None)


def mergeUser(newUser, oldUser):
    """
    Merge two given users.
    """

    log.info('replace "' + oldUser.lower() + '" with "'
             + newUser.lower() + '"')

    with connection:
        cur = connection.cursor()
        if userExists(newUser, True) and userExists(oldUser, True):
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

            log.info('replacing all aliases')
            cur.execute('UPDATE splitpot_aliases SET user = ? WHERE user = ?'
                        , [newUser.lower(), oldUser.lower()])

            log.info('replacing every "' + oldUser.lower() + '" with "'
                     + newUser.lower() + ' in participants table')
            cur.execute('UPDATE splitpot_participants SET user = ? WHERE user = ?'
                        , [newUser.lower(), oldUser.lower()])

            log.info('replacing events where owner is "'
                     + oldUser.lower() + '" with "' + newUser.lower()
                     + '"')
            cur.execute('UPDATE splitpot_events SET owner = ? WHERE owner = ?'
                        , [newUser.lower(), oldUser.lower()])

            log.info('replacing autocomplete entries from "'
                     + oldUser.lower() + '" to "' + newUser.lower()
                     + '"')
            cur.execute('UPDATE splitpot_autocomplete SET [from] = ? WHERE [from] = ?'
                        , [newUser.lower(), oldUser.lower()])

            log.info('removing all autocomplete entries that are pointing to "'
                      + oldUser.lower() + '"')  # TODO maybe leave this entries as they are (references to an alias)

            cur.execute('DELETE FROM splitpot_autocomplete WHERE [to] = ?'
                        , [oldUser.lower()])

            log.info('deleting the user "' + oldUser.lower() + '"')
            cur.execute('DELETE FROM splitpot_users WHERE email = ?',
                        [oldUser.lower()])

            return True

    return False


def resolveNick(userId):
    log.info('resolve nick ' + str(userId))
    if userExists(userId, True):
        result = userId
        if userExists(userId, False):
            with connection:
                cur = connection.cursor()
                cur.execute("SELECT name from splitpot_users where email = '"
                             + userId + "';")
                result = cur.fetchone()[0]
        return result
    else:
        return 'unknown user'


def addAlias(mainUser, alias):
    """
    Add alias to given user.
    """

    log.info('add ' + alias.lower() + ' as alias to '
             + mainUser.lower())

    with connection:
        cur = connection.cursor()
        if userExists(mainUser):
            cur.execute('INSERT INTO splitpot_aliases VALUES(?,?)',
                        (mainUser.lower(), alias.lower()))
        return True

    return False


def resolveAlias(alias):
    """
    Get main user from alias.
    """

    log.info('get main user for ' + alias.lower())

    with connection:
        cur = connection.cursor()
        cur.execute('SELECT user FROM splitpot_aliases WHERE alias = ?'
                    , [alias.lower()])

        result = cur.fetchone()
        if result != None:
            if len(result) > 0:
                return result[0]

    return None


def aliasUserExists(alias, mainMail=None):
    """
    Checks if an alias already exists.
    """

    log.info('checks if ' + alias.lower() + ' exists as an alias')
    exists = ''
    with connection:
        cur = connection.cursor()
        if mainMail != None:
            cur.execute('SELECT COUNT(*) FROM splitpot_aliases WHERE alias = ? AND user = ?'
                        , [alias.lower(), mainMail.lower()])
            exists = cur.fetchone()[0]
        else:
            cur.execute('SELECT COUNT(*) FROM splitpot_aliases WHERE alias = ?'
                        , [alias.lower()])
            exists = cur.fetchone()[0]

    return (False if exists == 0 else True)


def addAlias(mainUser, alias):
    """
    Add alias to given user.
    """

    log.info('add ' + alias.lower() + ' as alias to '
             + mainUser.lower())

    with connection:
        cur = connection.cursor()
        if userExists(mainUser):
            cur.execute('INSERT INTO splitpot_aliases VALUES(?,?)',
                        (mainUser.lower(), alias.lower()))
        return True

    return False


def resolveAlias(alias):
    """
    Get main user from alias.
    """

    log.info('get main user for ' + alias.lower())

    with connection:
        cur = connection.cursor()
        cur.execute('SELECT user FROM splitpot_aliases WHERE alias = ?'
                    , [alias.lower()])

        result = cur.fetchone()
        if result != None:
            if len(result) > 0:
                return result[0]

    return None


def aliasUserExists(alias, mainMail=None):
    """
    Checks if an alias already exists.
    """

    log.info('checks if ' + alias.lower() + ' exists as an alias')
    exists = ''
    with connection:
        cur = connection.cursor()
        if mainMail != None:
            cur.execute('SELECT COUNT(*) FROM splitpot_aliases WHERE alias = ? AND user = ?'
                        , [alias.lower(), mainMail.lower()])
            exists = cur.fetchone()[0]
        else:
            cur.execute('SELECT COUNT(*) FROM splitpot_aliases WHERE alias = ?'
                        , [alias.lower()])
            exists = cur.fetchone()[0]

    return (False if exists == 0 else True)


def resolveNick(userId):
    log.info('resolve nick ' + str(userId))
    if userExists(userId, True):
        result = userId
        if userExists(userId, False):
            with connection:
                cur = connection.cursor()
                cur.execute("SELECT name from splitpot_users where email = '"
                             + userId + "';")
                result = cur.fetchone()[0]
        return result
    else:
        return 'unknown user'


def buildTransactionTree():
    """
    Takes all participation entries with status 'new' and puts them into the Transaction Graph (which is cleard before).
    Returns a list of tuples with all <eventId, userId> keys, that were taken.
    """

    clearTransactionGraph()
    with connection:
        cur = connection.cursor()
        cur.execute("select id, amount, owner, user, tmp.num_parts FROM splitpot_participants, splitpot_events, (SELECT event, count(event) as 'num_parts' FROM splitpot_participants group by event) tmp WHERE splitpot_participants.event = splitpot_events.id AND tmp.event = splitpot_participants.event AND splitpot_participants.status != 'payday';"
                    )
        data = cur.fetchall()
        keys = []
        for entry in data:
            keys.append((entry[0], entry[3]))
            e = TransactionEdge(entry[3], entry[2], entry[1]
                                / (entry[4] + 1))
            print 'insert ' + str(e)
            insertEdge(e)
    return keys


def TransactionGraphWriteback(keys):
    """
    Bulk update for participant table. Sets all tuples <eventId, userId> in the participants table to status = 'payday'
    """

    update = ''
    for (event, usr) in keys:
        update += ' OR (event = ' + str(event) + " AND user = '" + usr \
            + "')"
    if len(update) == 0:
        log.info('empty transaction graph - no write back')
        return
    update = \
        "UPDATE splitpot_participants SET status = 'payday' WHERE " \
        + update[3:] + ';'
    log.info('transactiongraph Writeback: ' + update)
    with connection:
        cur = connection.cursor()
        cur.execute(update)


def isUserInEvent(email, event):
    """
    Check is a given user is in a given event.
    """

    log.info('check if "' + email.lower() + '" is in event: "'
             + str(event) + '"')
    with connection:
        if userExists(email) and getEvent(event) != None:
            events = listAllEventsFor(email)
            for curEvent in events:
                if str(curEvent.id) == str(event):
                    return True
            return


def addAutocompleteEntry(fromUser, toUser):
    """
    Adds a visibility conection from fromUser to toUser, if it doesn't exist yet. No checks if user exists. Returns true if connection was created, false if it already existed
    """

    with connection:
        cur = connection.cursor()
        cur.execute("SELECT count([to]) FROM splitpot_autocomplete WHERE [from] = '"
                     + fromUser.lower() + "' AND [to] = '"
                    + toUser.lower() + "';")
        num = cur.fetchone()[0]
        if num == 0:
            log.info('create autocomplete entry from ' + fromUser
                     + ' to ' + toUser)
            cur.execute("INSERT INTO splitpot_autocomplete VALUES('"
                        + fromUser.lower() + "', '" + toUser.lower()
                        + "');")
            return True
        return False


def getAutocompleteUser(fromUser, term):
    """
    Returns all emails that are visible for the fromUser id, that start with the given term (email or name). No checks against sql injection here
    """

    reply = []
    with connection:
        cur = connection.cursor()
        cur.execute("select [to] as 'value', name from splitpot_autocomplete, splitpot_users where splitpot_users.email = splitpot_autocomplete.[to] AND ([to] LIKE '"
                     + term + "%' OR name LIKE '" + term
                    + "%') and [from] = '" + fromUser + "';")

        data = cur.fetchall()
        for r in data:
            reply.append({'value': r[0], 'name': r[1] + ' (' + r[0]
                         + ')'})
    return json.dumps(reply)


