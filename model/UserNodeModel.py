from TransactionEdgeModel import TransactionEdge

class UserNode:
    def __init__(self, userId):
        self.userId = userId
        self.outgoing = {}
        self.incoming = {}
    
    def addOutEdge(self, edge):
        if not isinstance(edge, TransactionEdge):
            raise TypeError("parameter is not a transaction edge")
        if not edge.keyify() in self.outgoing:
            self.outgoing[edge.toUser] = edge
        else:
            self.outgoing[edge.toUser].amount += edge.amount

    def addInEdge(self, edge):
        if not isinstance(edge, TransactionEdge):
            raise TypeError("parameter is not an transaction edge")
        if not edge.keyify() in self.incoming:
            self.incoming[edge.fromUser] = edge
        else:
            self.incoming[edge.fromUser].amount += edge.amount

    def __eq__(self, other):
        if isinstance(other, UserNode):
            return self.userId == other.userId
        return TypeError("can't compare UserNode to " + str(other))

    def __ne__(self, other):
        return not self. __eq__(other)

    def __str__(self):
        return str(self.userId)

    def __repr__(self):
        return self.__str__()
