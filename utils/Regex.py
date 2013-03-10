#!/usr/bin/python
# -*- coding: utf-8 -*-

import re  # gex

entryCommentRegex = \
    re.compile("\A([\w|ü|Ü|ä|Ä|ö|Ö|ß|\d\|\s|\.|-|\u20AC|,|:|!|/|\(|\)|\-|\+|\*])*\Z"
               , re.MULTILINE | re.UNICODE)
emailRegex = \
    re.compile(r"(?:^|\s)[-a-z0-9_.+]+@(?:[-a-z0-9]+\.)+[a-z]{2,6}(?:\s|$)"
               , re.IGNORECASE)
emailAutocompleteRegex = re.compile("\A[a-zA-Z0-9_.+@]*\Z")
eventIdRegex = re.compile("\A[0-9]*\Z")
activatenCode = re.compile("\A[0-9a-zA-Z]*\Z")
amountRegex = re.compile("\A[1-9]+(\.[0-9][0-9]?)?\Z")
dateRegex = re.compile("^(((0[1-9]|[1-2][0-9]|3[0-1])-(0[13578]|(10|12)))|((0[1-9]|[1-2][0-9])-(02))|((0[1-9]|[1-2][0-9]|30)-(0[469]|11)))-[0-9]{4}$")
