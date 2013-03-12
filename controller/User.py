#!/usr/bin/python
# -*- coding: utf-8 -*-

import cherrypy
from mako.template import Template
from mako.lookup import TemplateLookup
lookup = TemplateLookup(directories=['template/user', 'template'])
import string
import sys

import Email

sys.path.append('utils/')
import Encryption
from Auth import *

from DatabaseParser import *
import DatabaseParser
db = DatabaseParser
import Splitpot
import logging
log = logging.getLogger('appLog')

from Regex import emailRegex
from Regex import activatenCode


@cherrypy.expose
def register(key=''):
    """
  Provides the Register form
  """

    log.info('provide register form')
    email = 'invalid invitation'
    if activatenCode.match(key):
        email = db.getUserFromPassword(key)
        log.info('found email address: ' + str(email))
    return lookup.get_template('register.html'
                               ).render(givenKey=str(key),
            givenEmail=email)


@cherrypy.expose
def forgot():
    """
  Provides the "Forgot pwd" Form
  """

    log.info('provide forgot form')
    return lookup.get_template('forgot_pwd.html').render()


@cherrypy.expose
def resend(email=''):
    return lookup.get_template('resend.html').render(email=email)


@cherrypy.expose
def doResend(email):
    log.info("do a resend request for '" + str(email) + "'")
    if email is None or not emailRegex.match(email) \
        or not db.userExists(email, True):
        tmpl = lookup.get_template('resend.html')
        return tmpl.render(bad_news='we could not find your email',
                           email=email)
    Email.sendInvitationMail(email, db.getResetUrlKey(email))
    tmpl = lookup.get_template('register.html')
    return tmpl.render(good_news='We resent your invitation code :)',
                       email=email)


@cherrypy.expose
def doRegister(
    email=None,
    key=None,
    nick=None,
    pwd1=None,
    pwd2=None,
    ):
    """
  Processes a register-request: checks email & pwd & if user exists. Sends activation email, if successfull.
  """

    log.info('register ' + str(email) + ' (' + str(nick) + ')')
    tmpl = lookup.get_template('register.html')
    errors = ''
    escapeRegex = False  # Quick checking some values against the DB
    if email is None:
        errors += '<li>You have to provide an email adress</li>'
    if key is None:
        errors += \
            "<li>You have to provide a registration key(<a href='resend?email=" \
            + str(email) + "'>resend</a>)</li>"
    if emailRegex.match(email) == None:
        errors += '<li>Your email is invalid</li>'
        escapeRegex = True
    if not escapeRegex and not db.isValidResetUrlKey(email, key, True):
        errors += \
            "<li>The registration key is invalid. You have to enter the same emailadress you've been invited to.(<a href='resend?email=" \
            + str(email) + "'>resend</a>)</li>"
    if nick is None or str(nick).__len__() < 3:
        errors += \
            '<li>Please enter a nick, with a minimum length of 3</li>'
    if str(pwd1).__len__() < 6:
        errors += '<li>Your password is too short</li>'
    if not pwd1 == pwd2:
        errors += '<li>Passwort repition incorrect</li>'
    if not escapeRegex and db.userExists(email, False):
        errors += '<li>User already exists</li>'
    if not errors == '':
        return tmpl.render(bad_news='<ul>' + errors + '</ul>',
                           givenKey=key, givenEmail=email)
    else:
        if db.activateUser(email, nick, pwd1, True):
            Email.signupConfirm(email)
            return tmpl.render(good_news="You'll hear from us - check your mailbox"
                               )
        else:
            return tmpl.render(bad_news='Something went wrong. Please try again later'
                               )


@cherrypy.expose
def requestForgot(email=None):
    """
  Processes the "If-forgot-my-pwd" request from the form. Generates confirmation key & sends email, if username is correct.
  """

    log.info('request forgot for ' + email)
    tmpl = lookup.get_template('forgot_pwd.html')
    if not db.userExists(email):
        return tmpl.render(bad_news='Email not found')
    else:
        Email.forgotConfirmation(email, db.getResetUrlKey(email))
        return tmpl.render(good_news='We sent you further instructions via email'
                           )


@cherrypy.expose
def forgot_reenter(email=None, resetKey=None):
    """
  Processes the confirmed reset of a pwd (user clicke on link in email). Generates new password and sends it via mail
  """

    log.info('forgot ' + email + ', key ' + resetKey)
    tmpl = lookup.get_template('forgot_pwd_reenter.html')
    if not emailRegex.match(email):
        return tmpl.render(bad_news='your email is invalid')

    if activatenCode.match(resetKey) and db.isValidResetUrlKey(email,
            resetKey):
        return tmpl.render(good_news='Choose your new password.',
                           email=email, resetKey=resetKey)
    else:
        return tmpl.render(bad_news="Your reset key is invalid :'-(")


@cherrypy.expose
def forgot_doReenter(
    email=None,
    resetKey=None,
    pwd1=None,
    pwd2=None,
    ):

    tmpl = lookup.get_template('forgot_pwd_reenter.html')

    if not emailRegex.match(email):
        return tmpl.render(bad_news='Your email is invalid.',
                           resetKey=resetKey, email=email)

    if email is None:
        return tmpl.render(bad_news='please enter your emai!',
                           resetKey=resetKey)

    if pwd1 is None:
        return tmpl.render(bad_news='please enter a password!',
                           resetKey=resetKey, email=email)

    if pwd1 != pwd2:
        return tmpl.render(bad_news='you have to enter the same password twice ;)'
                           , resetKey=resetKey, email=email)

    if resetKey is None:
        return tmpl.render(bad_news='You have to enter a reset key')

    if str(pwd1).__len__() < 6:
        return tmpl.render(bad_news='your password is too short',
                           resetKey=resetKey, email=email)

    if not activatenCode.match(resetKey) \
        or not db.isValidResetUrlKey(email, resetKey):
        return tmpl.render(good_news='Your reset key is invalid or has expired.'
                           , resetKey=resetKey, email=email)

    db.updateLogin(email, pwd1)
    return tmpl.render(good_news="You'r password has been set successfully"
                       )


@cherrypy.expose
def login(usr=''):
    tmpl = lookup.get_template('login.html')
    return tmpl.render(username=usr)


@cherrypy.expose
def doLogin(username, password):
    """
  Checks the login data against utils/auth. redirects to from_page or to "/" after successfull login
  """

    tmpl = lookup.get_template('login.html')
    if username is None or password is None:
        return tmpl.render(username=username,
                           bad_news='please enter your login information'
                           )

    error_msg = check_credentials(username, password)
    if error_msg:
        return tmpl.render(username=username,
                           bad_news='wrong login information')
    else:
        cherrypy.session[CURRENT_USER_NAME] = cherrypy.request.login = \
            username
        raise cherrypy.HTTPRedirect(cherrypy.url('/'))


@cherrypy.expose
def logout():
    """
    Destroys complete Session and redirects to about page or from_page, if given
    """

    sess = cherrypy.session
    username = sess.get(CURRENT_USER_NAME, None)
    sess[CURRENT_USER_NAME] = None
    if username:
        cherrypy.request.login = None
    raise cherrypy.HTTPRedirect(cherrypy.url('/about'))


@cherrypy.expose
@require()
def merge():
    tmpl = lookup.get_template('merge.html')

    return tmpl.render(newUser=getCurrentUserName())


@cherrypy.expose
@require()
def doMerge(email=None, key=None):
    """
Merge two accounts together. Will send a confirmation mail to the to-be-merged email.
"""

    tmpl = lookup.get_template('merge.html')

    errors = ''
    if key is not None and isValidMergeUrlKey(key):

        newMail = getUserFromPassword(key[:8])
        oldMail = getUserFromPassword(key[8:])

        log.info('valid merging key, merging "' + newMail + '" and "'
                 + oldMail + '" now')
        if mergeUser(newMail, oldMail):
            tmpl = lookup.get_template('index.html')
            return tmpl.render(good_news='Merge was successful!')
        else:
            log.warning('couldn\'t merge "' + newMail + '" and "'
                        + oldMail + '" for some unexpected reason')
            return tmpl.render(feedback='Oh no! Something went wrong. Please try again later.'
                               , newUser=getCurrentUserName())
    elif email is not None:

        log.info('merge "' + email.lower() + '" with "'
                 + getCurrentUserName() + '"')
        if email is None:
            errors += '<li>You have to provide an email address</li>'
        if emailRegex.match(email) == None:
            errors += '<li>Your email is invalid</li>'
        elif not userExists(email, True):
            errors += '<li>' + str(email.lower()) \
                + ' doesn\'t exist</li>'
        if userExists(getCurrentUserName()):
            events = listAllEventsFor(getCurrentUserName())
            for event in events:
                if str(event.participants).find(email) != -1:
                    log.info('found instance where "' + email.lower()
                             + '" and "' + getCurrentUserName().lower()
                             + '" are listed as hoster and participant. Can\'t merge'
                             )
                    errors = \
                        '<li>Can\'t merge these two accounts, because there are events, where host and participant are the same person.</li>'
                if str(event.owner).find(email) != -1:
                    log.info('found instance where owner and to-be-merged user are the same'
                             )
                    errors = '<li>Can\'t merge two same accounts.</li>'
        if not errors == '':
            return tmpl.render(bad_news='<ul>' + errors + '</ul>',
                               newUser=getCurrentUserName())
        else:
            mergeKey = getMergeUrlKey(getCurrentUserName(), email)
            Email.mergeRequest(getCurrentUserName(), email, mergeKey)

            return tmpl.render(good_news='An email has be sent to "'
                               + email.lower()
                               + '" for further information',
                               newUser=getCurrentUserName())
    else:
        tmpl = lookup.get_template('index.html')
        return tmpl.render(bad_news="Something went wrong, merge wasn't successful (maybe you already merged?)"
                           )


@cherrypy.expose
@require()
def alias():
    """
    Return the template for adding alias.
    """

    return lookup.get_template('alias.html'
                               ).render(aliases=getAliasesFor(getCurrentUserName()))


@cherrypy.expose
@require()
def doRemoveAlias(email):
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

    if key is not None and isValidAliasUrlKey(key):
        mainMail = getUserFromPassword(key[:8])
        alias = getUserFromPassword(key[8:])

        log.info('valid alias key, add "' + alias + '" as alias to "'
                 + mainMail)

        if mergeUser(mainMail, alias):
            return tmpl.render(good_news='Your alias has been added',
                               aliases=getAliasesFor(getCurrentUserName()))
        else:
            log.warning('couldn\'t alias/merge "' + newUser + '" and "'
                        + oldUser + '" for some unexpected reason')
            return tmpl.render(bad_news='Oh no! Something went wrong. Please try again later.'
                               , newUser=getCurrentUserName(),
                               aliases=getAliasesFor(getCurrentUserName()))
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
            return tmpl.render(bad_news='<ul>' + errors + '</ul>',
                               aliases=getAliasesFor(getCurrentUserName()))
        else:

            info = ''
            for user in alias:
                if activateUser(user, 'Alias for ' + user, 'random',
                                True):
                    log.info('register ' + user
                             + ' for the purpose of adding as alias')
                    aliasKey = getMergeUrlKey(getCurrentUserName(),
                            user)

                    Email.aliasRequest(getCurrentUserName(), user,
                            aliasKey)
                    info += '<li>An email has been sent to "' \
                        + user.lower() \
                        + '" for further information</li>'

            return tmpl.render(good_news=info,
                               aliases=getAliasesFor(getCurrentUserName()))
    else:

        return tmpl.render(good_news='Nothing to add to aliases list')

@cherrypy.expose
def profile(self):
    """
    Delivers the profile page for the current logged in user, where he then can change his username and password
    """

    return lookup.get_template('profile.html'
                               ).render(currentUser=resolveNick(getCurrentUserName()))

# @require()

@cherrypy.expose
def updateProfile(self):
    return None

