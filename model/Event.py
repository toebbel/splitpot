#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
from datetime import datetime
DATEFORMAT = '%d-%m-%Y'

class Event:

    def __init__(
        self,
        id=None,
        owner=None,
        date=None,
        amount=None,
        participants=None,
        comment=None,
        status=None
        ):
        self.id = id
        self.owner = owner
        self.date = date
        self.amount = amount
        self.participants = participants
        self.comment = comment
        self.status = status

    def __str__(self):
        date_str = self.date
        if type(date_str) is datetime:
            date_str = date_str.strftime(DATEFORMAT)
        return 'Event ' + str(self.id) + ', owned by ' + self.owner \
            + '(' + date_str + ') over ' + str(self.amount) + ' with ' \
            + json.dumps(self.participants) + ' | ' + self.comment + ' | ' + self.status


