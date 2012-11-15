class User:
    def __init__(self, email=None, name=None, events=None, salt=None, password=None):
        self.email = email
        self.name = name
        self.events = events
        self.salt = salt
        self.password = password
