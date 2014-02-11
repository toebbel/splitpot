#!/usr/bin/python
# -*- coding: utf-8 -*-

import cherrypy
import sys
sys.path.append('utils')

from DatabaseParser import *
import User
from Auth import *
from Regex import *

import logging
log = logging.getLogger('appLog')

import json
import random


@cherrypy.expose
@require()
def autocomplete(q=''):
    """
    Returns all visible users, that start with the given term (email or nick).
    """
    if emailAutocompleteRegex.match(q):
        response = getAutocompleteUser(getCurrentUserName(), q)
        fixed = '[{"id":' + str(random.randint(100000000,10000000000000)) + ', "url":"http://www.gravatar.com/avatar?d=monsterid", "value":"'+q+'"}]' 
        return response if response != '[]' else fixed
    else:
        log.info("caught illegal search term " + q)
        return json.dumps([])
