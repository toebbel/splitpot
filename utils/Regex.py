#!/usr/bin/python
# -*- coding: utf-8 -*-
import re  # gex

entryCommentRegex = \
    re.compile("\A([\w|\d\|\s|\.|-|\20AC|,|:|/|\(|\)])*\Z",
               re.MULTILINE | re.UNICODE)
emailRegex = \
    re.compile(r"(?:^|\s)[-a-z0-9_.+]+@(?:[-a-z0-9]+\.)+[a-z]{2,6}(?:\s|$)"
               , re.IGNORECASE)
eventIdRegex = re.compile("\A[0-9]*\Z")
activatenCode = re.compile("\A[0-9a-zA-Z]*\Z")
