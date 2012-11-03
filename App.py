import cherrypy
import logging
from utils import Logger
from controller.Splitpot import *
from controller.Login import *
from controller.Email import *

#def main():
log = logging.getLogger("appLog")
log.info("Splitpot started")
cherrypy.log.access_file = None

root = splitpot_controller()
root.user = login_controller()

cherrypy.quickstart(root)
log.info("Splitpot stopped")

#if __name__ == '__main__':
#    main()
