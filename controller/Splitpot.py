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
        return tmpl.render()

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
                               , comment=comment, others=others)

        if float(amount) <= 0:
            log.info('amount <= 0')
            return tmpl.render(bad_news='Amount has to be greater than zero ;)'
                               , comment=comment, others=others)

        for other in othersList:
            if not emailRegex.match(other):
                log.info('Email: ' + str(other) + ' is malformed.')
                return tmpl.render(bad_news='Email ' + other
                                   + ' is mal formed. Please correct',
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
            return tmpl.render(bad_news='Comment is malformed. Plase correct & try again'
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
        eventId = insertEvent(getCurrentUserName(), date.today(),
                              amount, othersList, comment)
        event = getEvent(eventId)

        for participant in othersList:
            Email.participantEmail(participant, event)
        Email.ownerEmail(getCurrentUserName(), event)

        tmpl = lookup.get_template('index.html')
        return tmpl.render(good_news='created event :)')

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

            newMail = getUserFromPassword(key[:8])
            oldMail = getUserFromPassword(key[8:])

            log.info('valid merging key, merging "' + newMail
                     + '" and "' + oldMail + '" now')
            if mergeUser(newMail, oldMail):
                return self.index()
            else:
                log.warning('couldn\'t merge "' + newMail + '" and "'
                            + oldMail + '" for some unexpected reason')
                return tmpl.render(feedback='Oh no! Something went wrong. Please try again later.'
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
                Email.mergeRequest(getCurrentUserName(), email,
                                   mergeKey)

                return tmpl.render(good_news='An email has be sent to "'
                                    + email.lower()
                                   + '" for further information',
                                   newUser=getCurrentUserName())

    @cherrypy.expose
    @require()
    def alias(self):
        """
        Return the template for adding alias.
        """

        return lookup.get_template('alias.html').render(aliases = getAliasesFor(getCurrentUserName()))

    @cherrypy.expose
    @require()
    def doRemoveAlias(self, email):
        """
        Removes an alias from the current user
        """
        tmpl = lookup.get_template('alias.html')
        if not emailRegex.match(email):
            return tmpl.render(bad_news='The given email is invalid')
        removeAlias(getCurrentUserName(), email)
        raise cherrypy.HTTPRedirect(cherrypy.url('alias'))

    @cherrypy.expose
    @require()
    def doAddAlias(
        self,
        alias=None,
        mainMail=None,
        key=None,
        ):
        """
        Add an alias to this account.
        """

        tmpl = lookup.get_template('alias.html')
        errors = ''

        if key is not None and isValidMergeUrlKey(key):
            mainMail = getUserFromPassword(key[:8])
            alias = getUserFromPassword(key[8:])

            log.info('valid alias key, add "' + alias
                     + '" as alias to "' + mainMail)

            if mergeUser(mainMail, alias):
                addAlias(mainMail, alias)
                return tmpl.render(good_news='Your alias has been added',
                        aliases = getAliasesFor(getCurrentUserName()))
            else:
                log.warning('couldn\'t alias/merge "' + newUser
                            + '" and "' + oldUser
                            + '" for some unexpected reason')
                return tmpl.render(bad_news='Oh no! Something went wrong. Please try again later.'
                                   , newUser=getCurrentUserName(), aliases = getAliasesFor(getCurrentUserName()))
        elif alias is not None:
            log.info('alias is not not')

            alias = [x.strip() for x in alias.split(',')]
            for user in alias:
                if emailRegex.match(user) == None:
                    errors += '<li>' + user + ' is invalid</li>'
                else:

                    if userExists(user, True):
                        errors += '<li>' + user \
                            + ' already exists, use <a href="../merge">Merge E-Mails</a> instead</li>'
                    elif aliasUserExists(user):
                        errors += '<li>' + user \
                            + ' is already an alias for someone else</li>'

            if not errors == '':
                return tmpl.render(bad_news='<ul>' + errors + '</ul>', aliases = getAliasesFor(getCurrentUserName()))
            else:

                info = ''
                for user in alias:
                    if activateUser(user, 'Alias for ' + user, 'random'
                                    , True):
                        log.info('register ' + user
                                 + ' for the purpose of adding as alias'
                                 )
                        aliasKey = getMergeUrlKey(getCurrentUserName(),
                                user)

                        Email.aliasRequest(getCurrentUserName(), user,
                                aliasKey)
                        info += '<li>An email has been sent to "' \
                            + user.lower() \
                            + '" for further information</li>'

                return tmpl.render(good_news=info, aliases = getAliasesFor(getCurrentUserName()))
        else:

            return tmpl.render(good_news='Nothing to add to aliases list'
                               )


