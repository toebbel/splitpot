import cherrypy
import logging
from controller.Splitpot import *
from controller.Login import *
from controller.Email import *

def main():
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S',filename='log/app.log', level=logging.DEBUG)
    logging.info('Splitpot started')
                    
    cherrypy.log.access_file = None

    root = splitpot_controller()
    root.user = login_controller()

    cherrypy.quickstart(root)
    logging.info('Stopped Splitpot')

if __name__ == '__main__':
    main()
