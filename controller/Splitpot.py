#!/usr/bin/python
# -*- coding: utf-8 -*-

import cherrypy
from mako.template import Template
from mako.lookup import TemplateLookup
lookup = TemplateLookup(directories=['template/', 'template/splitpot/'])
import sys
sys.path.append('utils')

from DatabaseParser import *
import User
from Auth import *
from datetime import date
from TransactionGraph import *
from Regex import *
import Email

from datetime import date
import logging
log = logging.getLogger('appLog')


class splitpot_controller(object):

    @cherrypy.expose
    @require()
    def index(self):
        """
        [users] Returns the overview of the accounting of the current user. Contains debts and link to overview as well as creation of new events.
        """

        log.info('deliver index')
        tmpl = lookup.get_template('index.html')
        return tmpl.render(debts=12.2, others_debts=0.2, entries=[])

                      # TODO ensure that users can only see events, they are participating/hosting

    @cherrypy.expose
    @require()
    def event(self, id):
        """
        Return a detail view of a given event, if the user requesting the event was a hoster or a participant.
        """

        log.info('deliver event page')
        tmpl = lookup.get_template('event.html')
        if not eventIdRegex.match(id):
            return self.index()
        elif getEvent(id) == None:
            return tmpl.render(event=None)
        elif not isUserInEvent(getCurrentUserName(), id):
            return tmpl.render(event='denied')
        return tmpl.render(event=getEvent(id))

    @cherrypy.expose
    @require()
    def add(self):
        """
        [users] Delivers the "Add-Event form"
        """

        log.info('deliver add form')
        return lookup.get_template('add.html').render()

    @cherrypy.expose
    def about(self):
        """
        [users] Delivers a static page, which is the welcome screen for users, that are not logged in
        """

        log.info('deliver about page')
        return lookup.get_template('about.html').render()

  # signature of insertEvent: insertEvent(owner, date, amount, participants, comment)

    @cherrypy.expose
    @require()
    def doAdd(
        self,
        amount,
        others,
        comment,
        ):
        """
    Adds an event with the current user as owner and users with emails in 'others' as participants
    If one of the given emails in other is not a known user, an invitation email will be sent.
    """

        othersList = [x.strip() for x in str(others).split(',')]

        log.info('removing duplicates from others list, if there are any.'
                 )
        duplicates = set()
        duplicates_add = duplicates.add
        othersList = [x for x in othersList if x not in duplicates
                      and not duplicates_add(x)]

        tmpl = lookup.get_template('add.html')
        if not amountRegex.match(amount):
            log.info('mal formed amount')
            return tmpl.render(bad_news='Amount is mal formed. Please correct & try again'
                               )

        for other in othersList:
            if not emailRegex.match(other):
                log.info('Email: ' + str(other) + ' is malformed.')
                return tmpl.render(bad_news='Email ' + other
                                   + ' is mal formed. Please correct')
            if other == getCurrentUserName():  # TODO check if user adds himself via alias (issue 23)
                log.info('user tried to add himself to participants')
                return tmpl.render(bad_news="You can't add yourself to the list of participants"
                                   )

        if not entryCommentRegex.match(comment):
            log.info('Comment is malformed.')
            return tmpl.render(bad_news='Comment is malformed. Plase correct & try again'
                               )

        for curParticipant in othersList:
            if not userExists(curParticipant, True):
                tmpPassword = generateRandomChars(DEFAULT_PWD_LENGTH)
                log.info('participant: ' + curParticipant
                         + ' is not registered yet, registering now.')
                registerUser(curParticipant)

            addAutocompleteEntry(getCurrentUserName(), curParticipant)

        log.info('Add ' + amount + ' Euro to ' + str(othersList)
                 + ', comment: ' + comment)
        eventId = insertEvent(getCurrentUserName(), date.today(),
                              amount, othersList, comment)
        event = getEvent(eventId)

        for participant in othersList:
            Email.participantEmail(participant, event)
        Email.ownerEmail(getCurrentUserName(), event)

        tmpl = lookup.get_template('index.html')
        return tmpl.render(good_news="created event :)")

    @cherrypy.expose
    @require()
    def list(self):
        """
      Lists all events of a user, which he is participating/is owner
      """

        tmpl = lookup.get_template('list.html')
        log.info('Get all events for ' + getCurrentUserName())

        totalDebts = 0
        totalEarnings = 0
        events = listAllEventsFor(getCurrentUserName())
        for event in events:
            if event.amount < 0:
                totalDebts += event.amount
            else:
                totalEarnings += event.amount
        return tmpl.render(debts=totalDebts,
                           others_debts=totalEarnings, entries=events)

    def payday():
        log.info('PayDay! Build Transactiongraph')
        keys = buildTransactionTree()

        log.info('Optimize graph')
        changed = True
        while changed:
            changed = False
            cycles = getAllCycles()

        # TODO sort cycles by their amount (<1>)

            for c in cycles:
                if c[1] > 0:
                    changed = True
                    minimizePath(c[0])
        log.info('Finished optimization')

    # Generate emails from Tree

        for userId in graphNodes.keys():
            incoming = 0
            outgoing = 0
            for i in graphNodes[userId].incoming:
                incoming += i.amount
            for o in graphNodes[userId].outgoing:
                outgoing += o.amount
            payday(userId, graphNodes[userId].incoming,
                   graphNodes[userId].outgoing, incoming, outgoing)
        log.info('writing graphBack')
        TransactionGraphWriteback(keys)

    @cherrypy.expose
    @require()
    def merge(self):
        tmpl = lookup.get_template('merge.html')

        return tmpl.render(newUser=getCurrentUserName())

    @cherrypy.expose
    @require()
    def doMerge(self, email=None, key=None):
        """
    Merge two accounts together. Will send a confirmation mail to the to-be-merged email.
    """

        tmpl = lookup.get_template('merge.html')

        errors = ''
        if key is not None and isValidMergeUrlKey(key):
            newUser = getPassword(newMail)[:MERGE_KEY_LEN / 2]
            oldUser = getPassword(oldMail, True)[:MERGE_KEY_LEN / 2]

            log.info('valid merging key, merging "' + newUser
                     + '" and "' + oldUser + '" now')

            if mergeUser(newUser, oldUser):
                return self.index()
            else:
                log.warning('couldn\'t merge "' + newUser + '" and "'
                            + oldUser + '" for some unexpected reason')
                return tmpl.render(bad_news='Oh no! Something went wrong. Please try again later.'
                                   , newUser=getCurrentUserName())
        else:

            log.info('merge "' + email.lower() + '" with "'
                     + getCurrentUserName() + '"')
            if email is None:
                errors += \
                    '<li>You have to provide an email address</li>'
            if emailRegex.match(email) == None:
                errors += '<li>Your email is invalid</li>'
            elif not userExists(email, True):
                errors += '<li>' + str(email.lower()) \
                    + ' doesn\'t exist</li>'
            if userExists(getCurrentUserName()):
                events = listAllEventsFor(getCurrentUserName())
                for event in events:
                    if str(event.participants).find(email) != -1:
                        log.info('found instance where "'
                                 + email.lower() + '" and "'
                                 + getCurrentUserName().lower()
                                 + '" are listed as hoster and participant. Can\'t merge'
                                 )
                        errors = \
                            '<li>Can\'t merge these two accounts, because there are events, where host and participant are the same person.</li>'
                    if str(event.owner).find(email) != -1:
                        log.info('found instance where owner and to-be-merged user are the same'
                                 )
                        errors = \
                            '<li>Can\'t merge two same accounts.</li>'
            if not errors == '':
                return tmpl.render(bad_news='<ul>' + errors + '</ul>',
                                   newUser=getCurrentUserName())
            else:
                mergeKey = getMergeUrlKey(getCurrentUserName(), email)
                Email.mergeRequest(getCurrentUserName(), email, (),
                                   mergeKey)

                return tmpl.render(good_news='An email has be sent to "'
                                    + email.lower()
                                   + '" for further information',
                                   newUser=getCurrentUserName())


