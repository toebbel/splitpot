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
        log.info("found email address: " + str(email))
    return lookup.get_template('register.html').render(feedback='',
            givenKey=str(key), givenEmail=email)


@cherrypy.expose
def forgot():
    """
  Provides the "Forgot pwd" Form
  """

    log.info('provide forgot form')
    return lookup.get_template('forgot_pwd.html').render(feedback='')


@cherrypy.expose
def resend(email=''):
    return lookup.get_template('resend.html').render(feedback='',
            email=email)


@cherrypy.expose
def doResend(email):
    log.info("do a resend request for '" + str(email) + "'")
    if email is None or not emailRegex.match(email) \
        or not db.userExists(email, True):
        tmpl = lookup.get_template('resend.html')
        return tmpl.render(feedback='we could not find your email',
                           email=email)
    Email.sendInvitationMail(email, db.getResetUrlKey(email))
    tmpl = lookup.get_template('register.html')
    return tmpl.render(feedback='We resent your invitation code :)',
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
        errors += "<li>You'r email is invalid</li>"
        escapeRegex = True
    if not escapeRegex and not db.isValidResetUrlKey(email, key, True):
        errors += \
            "<li>The registration key is invalid. You have to enter the same emailadress you've been invited to.(<a href='resend?email=" \
            + str(email) + "'>resend</a>)</li>"
    if nick is None or str(nick).__len__() < 3:
        errors += \
            '<li>Please enter a nick, with a minimum length of 3</li>'
    if str(pwd1).__len__() < 6:
        errors += "<li>You'r password is too short</li>"
    if not pwd1 == pwd2:
        errors += '<li>Passwort repition incorrect</li>'
    if not escapeRegex and db.userExists(email, False):
        errors += '<li>User already exists</li>'
    if not errors == '':
        return tmpl.render(feedback='<ul>' + errors + '</ul>',
                           givenKey=key)
    else:
        if db.activateUser(email, nick, pwd1, True):
            Email.signupConfirm(email)
            return tmpl.render(feedback="You'll hear from us - check your mailbox"
                               )
        else:
            return tmpl.render(feedback='Something went wrong. Please try again later'
                               )


@cherrypy.expose
def requestForgot(email=None):
    """
  Processes the "If-forgot-my-pwd" request from the form. Generates confirmation key & sends email, if username is correct.
  """

    log.info('request forgot for ' + email)
    tmpl = lookup.get_template('forgot_pwd.html')
    if not db.userExists(email):
        return tmpl.render(feedback='Email not found')
    else:
        Email.forgotConfirmation(email, db.getResetUrlKey(email))
        return tmpl.render(feedback='We sent you further instructions via email'
                           )


@cherrypy.expose
def doForgot(email=None, resetKey=None):
    """
  Processes the confirmed reset of a pwd (user clicke on link in email). Generates new password and sends it via mail
  """

    log.info('forgot ' + email + ', key ' + resetKey)
    tmpl = lookup.get_template('forgot.html')
    if db.isValidResetUrl(email, resetKey):
        new_pwd = EncryptionHelper.generateRandomChars(8)  # TODO use default length from utils/auth
        Email.forgotNewPwd(email, new_pwd)
        db.updateLogin(email, newPassword)
        return tmpl.render(feedback="You'r password has been reset and in on it's way to your mailbox"
                           )
    else:
        return tmpl.render(feedback="You'r reset key is invalid")


@cherrypy.expose
def login(usr='', msg='Enter login information', from_page='/'):
    tmpl = lookup.get_template('login.html')
    return tmpl.render(username=usr, msg=msg, from_page=from_page)


@cherrypy.expose
def doLogin(username=None, password=None, from_page='/'):
    """
  Checks the login data against utils/auth. redirects to from_page or to "/" after successfull login
  """

    if username is None or password is None:
        return self.get_loginform('', from_page=from_page)

    error_msg = check_credentials(username, password)
    if error_msg:
        return login(username, error_msg, from_page)
    else:
        cherrypy.session[CURRENT_USER_NAME] = cherrypy.request.login = \
            username
        raise cherrypy.HTTPRedirect(from_page or '/')


@cherrypy.expose
def logout(from_page='/'):
    """
    Destroys complete Session and redirects to about page or from_page, if given
    """

    sess = cherrypy.session
    username = sess.get(CURRENT_USER_NAME, None)
    sess[CURRENT_USER_NAME] = None
    if username:
        cherrypy.request.login = None
    raise cherrypy.HTTPRedirect(from_page or '/about')
