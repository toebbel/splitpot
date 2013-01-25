#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from utils import Logger
import os
import datetime
now = datetime.datetime.now()

# backup the database

bashCmd = \
    'echo ".dump" | sqlite3 -batch -echo resource/splitpotDB_DEV.sqlite > ' \
    + now.strftime('%Y-%m-%d-%H-%M-%S') + '.backup'
os.system(bashCmd)

# run payday

from controller.Splitpot import *
log = logging.getLogger('appLog')
log.info("it's payday!")
controller = splitpot_controller()
controller.payday()
