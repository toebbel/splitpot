import cherrypy
import cherrypy
from mako.template import Template
from mako.lookup import TemplateLookup
lookup = TemplateLookup(directories=['template/', 'template/splitpot/'])

class splitpot_controller(object):

  @cherrypy.expose
  def index(self):
    tmpl = lookup.get_template("index.html")
    return tmpl.render(debts=12.2, others_debts=0.2, entries = [])

  @cherrypy.expose
  def add(self): #gives the form for entering a new event
    tmpl = lookup.get_template("add.html")
    return tmpl.render()

  """
  Adds an event with the current user as owner and users with emails in 'others' as participants

  If one of the given emails in other is not a known user, an invitation email will be sent.
  """
  @cherrypy.expose
  def doAdd(self, comment, amount, others):
    print "do Add" + comment + ", " + amount + "euro" + others
    return "danke"

