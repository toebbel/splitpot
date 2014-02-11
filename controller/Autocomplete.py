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


@cherrypy.expose
@require()
def autocomplete(q=''):
    """
    Returns all visible users, that start with the given term (email or nick).
    """
    if emailAutocompleteRegex.match(q):
        return getAutocompleteUser(getCurrentUserName(), q)
    else:
        log.info("caugth illegal search term " + q)
        return json.dumps([])
