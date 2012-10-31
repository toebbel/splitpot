import cherrypy
from mako.template import Template
from mako.lookup import TemplateLookup
lookup = TemplateLookup(directories=['template/email', 'template'])

import string
import smtplib
from email.mime.text import MIMEText

import DatabaseParser
db = DatabaseParser

import Splitpot

def sendMail(host, sender, to, subject, body):
  msg = MIMEText(body)
  msg['From'] = sender
  msg['To'] = to
  msg['Subject'] = subject
  server = smtplib.SMTP(host)
  server.sendmail(sender, [to], msg.as_string())
  server.quit()

class MailHelper(object):
  runningUrl = "http://0xabc.de/splitpot/"

  def SettingsWrapper(to, subject, body):
    #TODO read from config file and provide login data
    sendMail("localhost", "splitpot@0xabc.de", sender, to, subject, body)

  def signupConfirm(email, key):
    tmpl = lookup.get_template("signup_confirmation.email")
    SettingsWrapper(email, "Signup Confirmation", tmpl.render(url = runningUrl + "/user/confirm?key=" + key))

  def forgotConfirmation(email, key):
    tmpl = lookup.get_template("forgot_confirmation.email")
    SettingsWrapper(email, "Password Reset", tmpl.render(url = runningUrl + "/user/forgot_form?key=" + key))

  def forgotNewPwd(email, pwd):
    tmpl = lookup.get_template("forgot_success.email")
    SettingsWrapper(email, "Info: Password reset successfully", tmpl.render(pwd = pwd))

  def payday(email, payments):
    tmpl = lookup.get_template("payday.email")
    SettingsWrapper(email, "Payday!", tmpl.render(payments)) #TODO enough data or more?
