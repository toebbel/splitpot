import logging
log = logging.getLogger("appLog")
log.setLevel(logging.DEBUG)
formatter = logging.Formatter(
            "[%(asctime)-11s] %(module)-20s %(levelname)-10s %(message)s", datefmt="%d/%m/%Y %H:%M:%S")

# Log to file
filehandler = logging.FileHandler("log/app.log", "a")
filehandler.setLevel(logging.DEBUG)
filehandler.setFormatter(formatter)
log.addHandler(filehandler)

'''
    # Log to stdout too
    streamhandler = logging.StreamHandler()
    streamhandler.setLevel(logging.DEBUG)
    streamhandler.setFormatter(formatter)
    log.addHandler(streamhandler)
'''
