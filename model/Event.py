class Event:
    def __init__(self, id=None, owner=None, date=None, amount=None, participants=None, comment=None):
        self.id = id
        self.owner = owner
        self.date = date
        self.amount = amount
        self.participants = participants
        self.comment = comment
