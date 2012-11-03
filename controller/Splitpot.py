import cherrypy
import cherrypy
from mako.template import Template
from mako.lookup import TemplateLookup
lookup = TemplateLookup(directories=['template/', 'template/splitpot/'])

import logging
log = logging.getLogger("appLog")

class splitpot_controller(object):

  @cherrypy.expose
  def index(self):
    log.info("deliver index")
    tmpl = lookup.get_template("index.html")
    return tmpl.render(debts=12.2, others_debts=0.2, entries = [])

  @cherrypy.expose
  def add(self): #gives the form for entering a new event
    log.info("deliver add form")
    return lookup.get_template("add.html").render()

  @cherrypy.expose
  def about(self):
    log.info("deliver about page")
    return lookup.get_template("about.html").render()

  @cherrypy.expose
  def doAdd(self, comment, amount, others):
    """
    Adds an event with the current user as owner and users with emails in 'others' as participants
    If one of the given emails in other is not a known user, an invitation email will be sent.
    """
    log.info("do Add" + comment + ", " + amount + "euro" + others)
    return index();

