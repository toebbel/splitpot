#!/usr/bin/python
# -*- coding: utf-8 -*-

import cherrypy
from mako.template import Template
from mako.lookup import TemplateLookup
lookup = TemplateLookup(directories=['template/', 'template/splitpot/', 'template/error/'])
import sys
sys.path.append('utils')

from DatabaseParser import *
import User
from Auth import *
from datetime import date
from TransactionGraph import *
from Regex import *
import Email
import re

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
        return tmpl.render()

    @cherrypy.expose
    def error_page_404(status, message, traceback, version):
        tmpl = lookup.get_template('404.html')
        return tmpl.render()
    cherrypy.config.update({'error_page.404': error_page_404})

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
        curDate,
        amount,
        others,
        comment,
        ):
        """
    Adds an event with the current user as owner and users with emails in 'others' as participants
    If one of the given emails in other is not a known user, an invitation email will be sent.
    """

        # in case a comma was used, instead of a dot

        amount = amount.replace(',', '.')

        othersList = [x.strip() for x in str(others).split(',')]

        log.info('removing duplicates from others list, if there are any.'
                 )
        duplicates = set()
        duplicates_add = duplicates.add
        othersList = [x for x in othersList if x not in duplicates
                      and not duplicates_add(x)]

        tmpl = lookup.get_template('add.html')
        if not dateRegex.match(curDate):
            log.info('date is malformed')
            return tmpl.render(bad_news='Date is malformed. Just use the datepicker.'
                               , comment=comment, others=others)

        if not amountRegex.match(amount):
            log.info('malformed amount')
            return tmpl.render(bad_news='Amount is malformed. Please correct & try again.'
                               , comment=comment, others=others)

        if float(amount) <= 0:
            log.info('amount <= 0')
            return tmpl.render(bad_news='Amount has to be greater than zero ;)'
                               , comment=comment, others=others)

        for other in othersList:
            if not emailRegex.match(other):
                log.info('Email: ' + str(other) + ' is malformed.')
                return tmpl.render(bad_news='Email ' + other
                                   + ' is malformed. Please correct',
                                   comment=comment, others=others,
                                   amount=amount)
            if other == getCurrentUserName() or resolveAlias(other) \
                == getCurrentUserName():
                log.info('user tried to add himself to participants')
                return tmpl.render(bad_news="You can't add yourself to the list of participants"
                                   , comment=comment, others=others,
                                   amount=amount)

        if not entryCommentRegex.match(comment):
            log.info('Comment is malformed.')
            return tmpl.render(bad_news='Comment is malformed. Please correct & try again'
                               , comment=comment, others=others,
                               amount=amount)

        for curParticipant in othersList:
            if not userExists(curParticipant, True) \
                and resolveAlias(curParticipant) == None:
                tmpPassword = generateRandomChars(DEFAULT_PWD_LENGTH)
                log.info('participant: ' + curParticipant
                         + ' is not registered yet, registering now.')
                registerUser(curParticipant)

            if resolveAlias(curParticipant) != None:
                log.info('found an alias in participant\'s list, replace with main user'
                         )
                log.info(othersList)
                log.info(resolveAlias(curParticipant))
                othersList = [(resolveAlias(curParticipant) if x
                              == curParticipant else x) for x in
                              othersList]
                curParticipant = resolveAlias(curParticipant)
                log.info('main user: ' + str(curParticipant))

            addAutocompleteEntry(getCurrentUserName(), curParticipant)

        log.info('Add ' + amount + ' Euro to ' + str(othersList)
                 + ', comment: ' + comment)

        splitDate = re.findall(r"[\d]+", curDate)
        splitDate = [int(x) for x in splitDate]
        today = datetime.date(splitDate[2], splitDate[1], splitDate[0])
        eventId = insertEvent(getCurrentUserName(), today, amount,
                              othersList, comment)
        event = getEvent(eventId)

        for participant in othersList:
            Email.participantEmail(participant, event)
        Email.ownerEmail(getCurrentUserName(), event)

        tmpl = lookup.get_template('index.html')
        return tmpl.render(good_news='successfully created event :)')

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
                totalDebts += event.amount \
                    / float(len(event.participants) + 1)
            else:
                totalEarnings += event.amount - event.amount \
                    / float(len(event.participants) + 1)
        return tmpl.render(debts=totalDebts,
                           others_debts=totalEarnings, entries=events)

    def payday(self):
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
            incomingTransactions = []
            outgoingTransactions = []
            for i in graphNodes[userId].incoming:
                edge = \
                    graphEdges[graphNodes[userId].incoming[i].keyify()]
                if edge.amount > 0:
                    incoming += edge.amount
                    incomingTransactions.append(edge)
                    print str(edge)
            for o in graphNodes[userId].outgoing:
                edge = \
                    graphEdges[graphNodes[userId].outgoing[o].keyify()]
                if edge.amount > 0:
                    outgoing += edge.amount
                    outgoingTransactions.append(edge)
                    print str(edge)

            Email.payday(userId, incomingTransactions,
                         outgoingTransactions, incoming, outgoing)
        log.info('writing graphBack')
        TransactionGraphWriteback(keys)


