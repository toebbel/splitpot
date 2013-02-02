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
        errors += "<li>Your email is invalid</li>"
        escapeRegex = True
    if not escapeRegex and not db.isValidResetUrlKey(email, key, True):
        errors += \
            "<li>The registration key is invalid. You have to enter the same emailadress you've been invited to.(<a href='resend?email=" \
            + str(email) + "'>resend</a>)</li>"
    if nick is None or str(nick).__len__() < 3:
        errors += \
            '<li>Please enter a nick, with a minimum length of 3</li>'
    if str(pwd1).__len__() < 6:
        errors += "<li>Your password is too short</li>"
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
