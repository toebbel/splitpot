#!/usr/bin/python
# -*- coding: utf-8 -*-

import cherrypy
import logging
from utils import Logger
from controller.Splitpot import *
from controller.User import *
from controller.Email import *
from controller.Autocomplete import *
from utils.Auth import check_auth

import utils.Auth

# def main():

log = logging.getLogger('appLog')
cherrypy.log.access_log.propagate = False
log.info('Splitpot started')
cherrypy.log.access_file = None

root = splitpot_controller()
root.user = User
root.autocomplete = autocomplete 

cherrypy.quickstart(root, '/splitpot', config='resource/app.cfg')
log.info('Splitpot stopped')
