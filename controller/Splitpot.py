import cherrypy
from mako.template import Template
from mako.lookup import TemplateLookup
lookup = TemplateLookup(directories=['template/', 'template/splitpot/'])

from DatabaseParser import *
import User
import sys
from Auth import *
from datetime import date
from Regex import *
sys.path.append('controller')
from Email import * 

import logging
log = logging.getLogger("appLog")

class splitpot_controller(object):

  #TODO make admin-only
  @cherrypy.expose
  def inspectSession(self):
    """
    Pulls all information from utils/session and pushes them naked into the response
    """
    log.info("Session:" + cherrypy.session.get('currentUser')) #TODO use session helper
    return self.index()

  @cherrypy.expose
  @require()
  def index(self):
    activateUser("awesome@0xabc.de", "Mr. Awesome", "awesome", True)
    """
    [users] Returns the overview of the accounting of the current user. Contains debts and link to overview as well as creation of new events.
    """
    log.info("deliver index")
    tmpl = lookup.get_template("index.html")
    return tmpl.render(debts=12.2, others_debts=0.2, entries = [])

  @cherrypy.expose
  @require()
  def event(self, id): #TODO ensure that users can only see events, they are participating/hosting
    tmpl = lookup.get_template("event.html")
    if not eventIdRegex.match(id):
      return self.index()
    return tmpl.render(event=getEvent(id))


  @cherrypy.expose
  @require()
  def add(self): #gives the form for entering a new event
    """
    [users] Delivers the "Add-Event form"
    """
    log.info("deliver add form")
    return lookup.get_template("add.html").render()

  @cherrypy.expose
  def about(self):
    """
    [users] Delivers a static page, which is the welcome screen for users, that are not logged in
    """
    log.info("deliver about page")
    return lookup.get_template("about.html").render()

  @cherrypy.expose
  @require()
  # signature of insertEvent: insertEvent(owner, date, amount, participants, comment)
  def doAdd(self, amount, others, comment):
    """
    Adds an event with the current user as owner and users with emails in 'others' as participants
    If one of the given emails in other is not a known user, an invitation email will be sent.
    """
    othersList = [x.strip() for x in str(others).split(',')]

    log.info("removing duplicates from others list, if there are any.")
    duplicates = set()
    duplicates_add = duplicates.add
    othersList = [ x for x in othersList if x not in duplicates and not duplicates_add(x)]

    for other in othersList:
        if not emailRegex.match(others):
            log.info("Email: " + str(others) + " is malformed.")
            #TODO: template.render error for wrong emails

    if not entryCommentRegex.match(comment):
        log.info("Comment is malformed.")
        #TODO: template.render error for malformed comments

    for curParticipant in othersList:
            if not userExists(curParticipant, True):
                log.info('participant: ' + curParticipant + ' is not registered yet, registering now.')
                registerUser(curParticipant)
		sendInvitation(curParticipant, getResetUrlKey(email))

    log.info("Add " + amount + " Euro to " + str(othersList) + ", comment: " + comment)
    insertEvent(getCurrentUserName(), date.today(), amount, othersList, comment)
    return self.index()

  @cherrypy.expose
  @require()
  def list(self):
      """
      Lists all events of a user, which he is participating/is owner
      """
      tmpl = lookup.get_template("list.html")
      log.info("Get all events for " + getCurrentUserName())

      totalDebts = 0
      totalEarnings = 0
      events = listAllEventsFor(getCurrentUserName())
      for event in events:
          if (event.amount < 0):
              totalDebts += event.amount
          else:
              totalEarnings += event.amount
      return tmpl.render(debts=totalDebts, others_debts=totalEarnings, entries=events)
