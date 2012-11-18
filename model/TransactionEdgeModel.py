class TransactionEdge:
    def __init__(self, fromUserId, toUserId, amount, inheritsFromEventId):
        self.fromUser = fromUserId
        self.toUser = toUserId
        self.amount = amount
        self.inheritsFromEvent = inheritsFromEventId

    def keyify(self):
        return str(self.fromUser) + "." + str(self.toUser) + "." + str(self.inheritsFromEvent)

    def __eq__(self, other):
        if isinstance(other, TransactionEdge):
            return self.fromUser == other.fromUser and self.toUser == other.toUser and self.amount == other.amount and self.inheritsFromEvent == other.inheritsFromEvent
        return TypeError("can't compare Transaction edge to " + str(other))

    def __ne__(self, other):
        return not self.__eq__(other)
