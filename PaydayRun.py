#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from utils import Logger
import os
import datetime
now = datetime.datetime.now()

# run payday

from controller.Splitpot import *
log = logging.getLogger('appLog')
log.info("it's payday!")
controller = splitpot_controller()
controller.payday()
