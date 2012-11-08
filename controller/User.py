import cherrypy
from mako.template import Template
from mako.lookup import TemplateLookup
lookup = TemplateLookup(directories=['template/user', 'template'])
import re #gex
import string
import sys

import Email

sys.path.append('utils/')
import Encryption

import DatabaseParser
db = DatabaseParser
import Splitpot
import logging
log = logging.getLogger("appLog")

class user_controller(object):

  mail_regex = """^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$"""

  @cherrypy.expose
  def register(self):
    """
    Provides the Register form
    """
    log.info("provide register form")
    return lookup.get_template("register.html").render()

  @cherrypy.expose
  def forgot(self):
    """
    Provides the "Forgot pwd" Form
    """
    log.info("provide forgot form")
    return lookup.get_template("forgot_pwd.html").render()

  @cherrypy.expose
  def doRegister(self, email = None, pwd1 = None, pwd2 = None):
    """
    Processes a register-request: checks email & pwd & if user exists. Sends activation email, if successfull.
    """
    log.info("register " + email + ":" + pwd1 + " == " + pwd2) #TODO remove pwd from loggin!
    tmpl = lookup.get_template("register.html")
    if(email is None):
      tmpl.render(feedback="You have to provide an email adress")
    if(str(email).__len__() < 6):
      return tmpl.render(feedback="You'r password is too short")
    if(re.match(email_regex, email) == None):
      return tmpl.render(feedback="You'r email is invalid")
    if(not pwd1 == pwd2):
      return tmpl.render(feedback="Passwort repition incorrect")
    if (db.userExists(email)):
      return tmpl.render(feedback="User already exists")
    else:
      if (db.user.register(email, pwd1)):
        MailHelper.signupConfirm(email, "") #TODO get signup confirmation key from db
        return tmpl.render(feedback="You'll hear from us - check your mailbox")
      else:
        return tmpl.render(feedback="Something went wrong. Please try again later")

  @cherrypy.expose
  def requestForgot(self, email = None):
    """
    Processes the "If-forgot-my-pwd" request from the form. Generates confirmation key & sends email, if username is correct.
    """
    log.info("request forgot for " + email)
    tmpl = lookup.get_template("forgot.html")
    if(not db.userExists(email)):
      return tmpl.render(feedback="Email not found")
    else:
      MailHelper.forgotConfirmation(email, "")#TODO get forgot-key from db
      return tmpl.render(feedback="We sent you further instructions via email")

  @cherrypy.expose
  def doForgot(self, email = None, resetKey = None):
    """
    Processes the confirmed reset of a pwd (user clicke on link in email). Generates new password and sends it via mail
    """
    log.info("forgot " + email + ", key " + resetKey)
    tmpl = lookup.get_template("forgot.html")
    if(db.isValidResetUrl(email, resetKey)):
      new_pwd = EncryptionHelper.generateRandomChars(8)
      MailHelper.forgotNewPwd(email, new_pwd)
      #todo store pwd in user entry
      return tmpl.render(feedback="You'r password has been reset and in on it's way to your mailbox")
    else:
      return tmpl.render(feedback="You'r reset key is invalid")
