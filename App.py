import cherrypy
import logging
from utils import Logger
from controller.Splitpot import *
from controller.User import *
from controller.Email import *
from utils.Auth import check_auth

import utils.Auth

#def main():
log = logging.getLogger("appLog")
log.info("Splitpot started")
cherrypy.log.access_file = None

root = splitpot_controller()
root.user = User

cherrypy.quickstart(root, config="resource/app.cfg")
log.info("Splitpot stopped")
