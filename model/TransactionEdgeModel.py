#!/usr/bin/python
# -*- coding: utf-8 -*-


class TransactionEdge:

    def __init__(
        self,
        fromUserId,
        toUserId,
        amount,
        ):

        self.fromUser = fromUserId
        self.toUser = toUserId
        self.amount = amount

    def keyify(self):
        return str(self.fromUser) + '|' + str(self.toUser)

    def __eq__(self, other):
        if isinstance(other, TransactionEdge):
            return self.fromUser == other.fromUser and self.toUser \
                == other.toUser and self.amount - other.amount < 0.01
        return TypeError("can't compare Transaction edge to "
                         + str(other))

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return 'from ' + self.fromUser + ', ' + self.toUser \
            + ', amount ' + str(self.amount)


