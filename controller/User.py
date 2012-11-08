import cherrypy
from mako.template import Template
from mako.lookup import TemplateLookup
lookup = TemplateLookup(directories=['template/user', 'template'])
import string
import sys

import Email

sys.path.append('utils/')
import Encryption
import Auth

import DatabaseParser
db = DatabaseParser
import Splitpot
import logging
log = logging.getLogger("appLog")

from Regex import emailRegex

@cherrypy.expose
def register():
  """
  Provides the Register form
  """
  log.info("provide register form")
  return lookup.get_template("register.html").render()

@cherrypy.expose
def forgot():
  """
  Provides the "Forgot pwd" Form
  """
  log.info("provide forgot form")
  return lookup.get_template("forgot_pwd.html").render()

@cherrypy.expose
def doRegister(email = None, pwd1 = None, pwd2 = None):
  """
  Processes a register-request: checks email & pwd & if user exists. Sends activation email, if successfull.
  """
  log.info("register " + str(email) + ":" + str(pwd1) + " == " + str(pwd2)) #TODO remove pwd from loggin!
  tmpl = lookup.get_template("register.html")
  if(email is None):
    tmpl.render(feedback="You have to provide an email adress")
  if(str(pwd1).__len__() < 6):
    return tmpl.render(feedback="You'r password is too short")
  if(emailRegex.match(email) == None):
    return tmpl.render(feedback="You'r email is invalid")
  if(not pwd1 == pwd2):
    return tmpl.render(feedback="Passwort repition incorrect")
  if (db.userExists(email)):
    return tmpl.render(feedback="User already exists")
  else:
    if (db.registerUser(email,"nick", pwd1)): #TODO issue 10
      Email.signupConfirm(email, "") #TODO get signup confirmation key from db
      return tmpl.render(feedback="You'll hear from us - check your mailbox")
    else:
      return tmpl.render(feedback="Something went wrong. Please try again later")

@cherrypy.expose
def requestForgot(email = None):
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
def doForgot(email = None, resetKey = None):
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

  @cherrypy.expose
  def get_loginform(username, msg="Enter login information", from_page="/"):
    tmpl = lookup.get_template("login.html")
    return tmpl.render(username = username, msg = msg, from_page = from_page)


  @cherrypy.expose
  def login(username=None, password=None, from_page="/"):
      """
      Checks the login data against utils/auth. redirects to from_page or to "/" after successfull login
      """
      if username is None or password is None:
          return self.get_loginform("", from_page=from_page)

      error_msg = check_credentials(username, password)
      if error_msg:
          return self.get_loginform(username, error_msg, from_page)
      else:
          cherrypy.session[CURRENT_USER_NAME] = cherrypy.request.login = username
          raise cherrypy.HTTPRedirect(from_page or "/")


  @cherrypy.expose
  def logout(from_page="/"):
      """
      Destroys complete Session and redirects to about page or from_page, if given
      """
      sess = cherrypy.session
      username = sess.get(CURRENT_USER_NAME, None)
      sess[CURRENT_USER_NAME] = None
      if username:
          cherrypy.request.login = None
      raise cherrypy.HTTPRedirect(from_page or "/about")
