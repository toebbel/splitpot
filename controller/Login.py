import cherrypy
from mako.template import Template
from mako.lookup import TemplateLookup
lookup = TemplateLookup(directories=['template/login', 'template'])
import re #gex
import string

import Email

sys.path.append('../utils/')
import Encryption

import DatabaseParser
db = DatabaseParser
import Splitpot

class login_controller(object):

  mail_regex = """^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$"""

  @cherrypy.expose
  def index(self):
    print "provide login form"
    tmpl = lookup.get_template("index.html")
    return tmpl.render()

  @cherrypy.expose
  def register(self):
    print "provide register form"
    tmpl = lookup.get_template("register.html")
    return tmpl.render()

  @cherrypy.expose
  def forgot(self):
    print "provide forgot form"
    tmpl = lookup.get_template("forgot_pwd.html")
    return tmpl.render()

  @cherrypy.expose
  def doLogin(self, email = None, pwd = None):
    print "login " + email + " with pwd " + pwd #TODO remove!
    tmpl = lookup.get_template("register.html")
    if (not db.login(email, pwd)):
      return tmpl.render(feedback="User or password incorrect")
    else:
      return Splitpot.index()

  @cherrypy.expose
  def doRegister(self, email = None, pwd1 = None, pwd2 = None):
    print "register " + email + ":" + pwd1 + " == " + pwd2 #TODO remove!
    tmpl = lookup.get_template("register.html")
    if(email is None):
      tmpl.render(feedback="Du musst eine Email angeben")
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
        return login(email, pwd1)
      else:
        return tmpl.render(feedback="Something went wrong. Please try again later")

  @cherrypy.expose
  def requestForgot(self, email = None):
    print "request forgot for " + email
    tmpl = lookup.get_template("forgot.html")
    if(not db.userExists(email)):
      return tmpl.render(feedback="Email not found")
    else:
      MailHelper.forgotConfirmation(email, "")#TODO get forgot-key from db
      return tmpl.render(feedback="We sent you further instructions via email")

  @cherrypy.expose
  def doForgot(self, email = None, resetKey = None):
    print "forgot " + email + ", key " + resetKey
    tmpl = lookup.get_template("forgot.html")
    if(db.isValidResetUrl(email, resetKey)):
      new_pwd = Encryption.generateSalt(8)
      MailHelper.forgotNewPwd(email, new_pwd)
      return tmpl.render(feedback="You'r password has been reset and in on it's way to your mailbox")
    else:
      return tmpl.render(feedback="You'r reset key is invalid")
