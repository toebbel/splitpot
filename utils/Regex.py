import re #gex

entryCommentRegex = re.compile("\A([\w|\d\|\s|\.|-|\20AC|,|:|/|\(|\)])*\Z",re.MULTILINE|re.UNICODE)
emailRegex = re.compile(r"(?:^|\s)[-a-z0-9_.]+@(?:[-a-z0-9]+\.)+[a-z]{2,6}(?:\s|$)",re.IGNORECASE)
