#!/usr/bin/python
# -*- coding: utf-8 -*-

import cherrypy
from mako.template import Template
from mako.lookup import TemplateLookup
lookup = TemplateLookup(directories=['template/email', 'template'],
                        input_encoding='utf-8')

import string
import smtplib
from email.mime.text import MIMEText

import DatabaseParser
import sys
sys.path.append('model')
from Event import Event
db = DatabaseParser

import Splitpot
import logging
log = logging.getLogger('appLog')

RUNNING_URL = 'http://0xabc.de/splitpot/'


def sendMail(
    host,
    sender,
    to,
    subject,
    body,
    ):
    """
    Wrapper for the smtplib
    """

    msg = MIMEText(body)
    msg['From'] = sender
    msg['To'] = to
    msg['Subject'] = subject
    server = smtplib.SMTP(host)
    server.sendmail(sender, to, msg.as_string())
    server.quit()


def sendInvitationMail(to, code):
    log.info('sending invitation to ' + str(to) + ' with code '
             + str(code))
    tmpl = lookup.get_template('ghost_user_link.email')
    SettingsWrapper(to, 'Splitpot Invitation',
                    tmpl.render(activateUrl=RUNNING_URL
                    + '/user/register?code=' + str(code)))


def SettingsWrapper(to, subject, body):
    """
    Sends mail using sendMail-method. Adds the required parameters like host & sender from the config file
    """

    settingsFile = open('resource/mail.settings')
    settings = {
        'host': 'localhost',
        'sender': 'splitpot@0xabc.de',
        'port': 25,
        'timeout': 1,
        }
    for l in settingsFile.readlines():
        if not (l.startswith('#') or l.strip() == ''):
            key = l[:l.find(':')].lower()
            val = l[l.find(':') + 1:].strip()
            settings[key] = val
    settingsFile.close()
    msg = MIMEText(body, 'plain', 'utf-8')
    msg['From'] = settings['sender']
    msg['To'] = to
    msg['Subject'] = subject

    log.info('sending mail to "' + to + '" with subject: "' + subject
             + '" and body "' + body + '" via "' + settings['host']
             + ':' + settings['port'] + '"')

    server = smtplib.SMTP(host=settings['host'],
                          port=int(settings['port']),
                          timeout=float(settings['timeout']))
    if 'user' in settings and not settings['user'] == '':
        if settings['encryption'].lower() == 'yes':
            server.ehlo()
            server.starttls()
            server.ehlo()
        server.login(settings['user'], settings['password'])
    server.sendmail(settings['sender'], [to], msg.as_string())
    server.quit()


def signupConfirm(email):
    """
    Sends the mail, that welcomes the user 
    """

    log.info('sending signup confirmation to ' + email)
    tmpl = lookup.get_template('signup_confirmation.email')
    SettingsWrapper(email, 'Signup Confirmation',
                    tmpl.render(url=RUNNING_URL))


def forgotConfirmation(email, key):
    """
    Sends the email with the url to confirm a password reset
    """

    log.info('sending a forgot-pwd-conf-key to ' + email + ': ' + key)
    tmpl = lookup.get_template('forgot_confirmation.email')
    SettingsWrapper(email, 'Password Reset',
                    tmpl.render(url=RUNNING_URL
                    + 'user/forgot_reenter?email=' + email
                    + '&resetKey=' + key))


def forgotNewPwd(email, pwd):
    """
    Sends the mail, that contains the freshly generated password for a user
    """

    log.info('sending a new pwd to ' + email + ': ' + pwd)  # TODO remove password from logging
    tmpl = lookup.get_template('forgot_success.email')
    SettingsWrapper(email, 'Info: Password reset successfully',
                    tmpl.render(pwd=pwd))


def payday(
    email,
    inPayments,
    outPayments,
    inDebt,
    outDebt,
    ):
    """
    Sends a mail with all payments of specific user. No changes on database/payments. This is only the helper for the template-retrieval
    """

    tmpl = lookup.get_template('payday.email')

    SettingsWrapper(email, "Payday!", tmpl.render(InPayments,outPayments, inDebt, outDebt)) #TODO enough data or more?

    return tmpl.render(inPayments=inPayments, outPayments=outPayments,
                       inDebts=inDebt, outDebts=outDebt)


def mergeRequest(newEmail, oldEmail, key):
    """
    Send a confirmation mail to the mail address that is going to be merged.
    """

    log.info('sending an account merge confirmation link to "'
             + oldEmail.lower() + '"')

    tmpl = lookup.get_template('merge_request.email')
    SettingsWrapper(oldEmail, 'Account Merge Request',
                    tmpl.render(newEmail=newEmail, oldEmail=oldEmail,
                    url=RUNNING_URL + 'user/doMerge?key=' + key))


def aliasRequest(currentUser, aliasUser, key):
    """
    Send a confirmation mail to the mail address that is going to be added as alias.
    """

    log.info('sending an alias confirmation link to "'
             + aliasUser.lower() + '"')

    tmpl = lookup.get_template('alias_request.email')
    SettingsWrapper(aliasUser, 'Add Alias Request',
                    tmpl.render(oldEmail=currentUser, url=RUNNING_URL
                    + 'doAddAlias?key=' + key))


def participantEmail(userId, event):
    assert isinstance(event, Event)
    num_part = len(event.participants) + 1
    text = lookup.get_template('add_event_participant.email').render(
        owner=event.owner,
        total=event.amount,
        num_participants=num_part,
        amount=event.amount / float(num_part),
        comment=event.comment,
        nick=db.resolveNick(userId),
        event_url=RUNNING_URL + 'event/' + str(event.id),
        )
    if not db.userExists(userId, False):
        text += lookup.get_template('ghost_user_link.email'
                                    ).render(activateUrl=RUNNING_URL
                + 'user/register?key=' + db.getResetUrlKey(userId,
                True))
    SettingsWrapper(userId, 'New Splitpot Entry', text)


def ownerEmail(userId, event):
    assert isinstance(event, Event)
    num_part = len(event.participants) + 1
    body = lookup.get_template('add_event_owner.email').render(
        total=event.amount,
        num_participants=num_part,
        amount=event.amount / float(num_part),
        comment=event.comment,
        nick=db.resolveNick(event.owner),
        event_url=RUNNING_URL + 'event/' + str(event.id),
        )
    SettingsWrapper(userId, 'Your new Splitpot Entry', body)


