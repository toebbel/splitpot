import cherrypy
import cherrypy
from mako.template import Template
from mako.lookup import TemplateLookup
lookup = TemplateLookup(directories=['template/', 'template/splitpot/'])

class splitpot_controller(object):

  @cherrypy.expose
  def index(self):
    tmpl = lookup.get_template("index.html")
    return tmpl.render()

  def add(self):
    tmpl = lookup.get_template("add.html")
    return tmpl.render()

#  def doAdd(self, Comment, Amount, Others):
 #TODO continue here

