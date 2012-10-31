import cherrypy
from controller.Splitpot import *
from controller.Login import *
from controller.Email import *

cherrypy.log.access_file = None

root = splitpot_controller()
root.user = login_controller()

cherrypy.quickstart(root)
