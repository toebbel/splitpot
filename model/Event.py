import json

class Event:
    def __init__(self, id=None, owner=None, date=None, amount=None, participants=None, comment=None):
        self.id = id
        self.owner = owner
        self.date = date
        self.amount = amount
        self.participants = participants
        self.comment = comment

    def __str__(self):
     return "Event " + str(self.id) + ", owned by " + self.owner + "(" + self.date + ") over " + str(self.amount) + " with " + json.dumps(self.participants) + " | " + self.comment
