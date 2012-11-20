import sys
sys.path.append('model/')
from TransactionEdgeModel import TransactionEdge
from UserNodeModel import UserNode
from copy import copy

graphNodes = {}
graphEdges = {}

def clearTransactionGraph():
    graphNodes.clear()
    graphEdges.clear()

def insertNode(node):
    """
    Adds a node to the graph, only if is not already in the grahp
    """
    if not isinstance(node, UserNode):
        raise TypeError("parameter is not a user node")
    if not node.userId in graphNodes:
        graphNodes[node.userId] = node

def insertEdge(edge):
    """
    Adds an edge to the graph structure. Adds nodes, if they are not existent. If the edge exists already, we sum up the amount
    """
    if not isinstance(edge, TransactionEdge):
        raise TypeError("parameter is not a transaction edge")
    if not edge.keyify() in graphEdges.keys():
        insertNode(UserNode(edge.fromUser))
        insertNode(UserNode(edge.toUser))
        graphNodes[edge.fromUser].addOutEdge(edge)
        graphNodes[edge.toUser].addInEdge(edge)
        if edge.keyify() in graphEdges:
            graphEdges[edge.keyify()].amount += edge.amount
        else:
            graphEdges[edge.keyify()] = edge

def getCycles(node):
    """
    Returns a list of paths that are cycles from the given node.

    All paths will start end end with the given node.
    No path? -> []
    """
    assert node in graphNodes, "node %r is not in graph" % node
    result = []
    for n in graphNodes[node].outgoing.keys():
        paths = getPaths(n, node)
        for p in paths:
            p.insert(0, graphNodes[node])
            result.append(p)
    return result

def getAllCycles():
    """
    Returns all cycles in the graph and their amount as tuple <cycle, amount>
    """
    result = []
    for n in graphNodes.keys():
        tmp = getCycles(n)
        for c in tmp:
            if not c in result:
                result.append((c, amount(c)))
    return result
def getPaths(fromId, toId):
    """
    Returns all paths from one node to another, if the path exists. Returns empty otherwise. Won't work for cycles!
    """
    if not fromId in graphNodes.keys() or not toId in graphNodes.keys():
        return []
    result = []
    _getPaths(graphNodes[fromId], graphNodes[toId], [], [], result)
    return result

def _getPaths(fro, to, visited, path, result):
    if fro.userId in visited:
        return 
    subPath = copy(path)
    subPath.append(fro)
    subVisited = copy(visited)
    subVisited.append(fro.userId)
    if fro == to:
        result.append(subPath)
        return
    for e in fro.outgoing.keys():
        if not e in visited:
            assert e in graphNodes
            _getPaths(graphNodes[e], to, subVisited, subPath, result)

def removeUnusedEdges():
    """
    Removes edges that don't hav a positive amount. Returns True, if any edge was removed.
    """
    mod = False
    for e in graphEdges.keys(): #use key as iterator so we can modify the dict
        if graphEdges[e].amount <= 0:
            del graphEdges[e]
            mod = True
    return mod

def minimizePath(path):
    """
    Runs through a cycle and lowers the amount by the min. amount in the cycle.

    Path HAS to be a cycle. if not -> RuntimeError
    No edge can be twice in the path, othweise -> Runtime Error
    """
    if path[0] != path[len(path) - 1]:
        raise RuntimeError("the given path is not a cycle and can't be minimized")
    
    unchecked = pathToEdgeSequence(path)
    accepted = []
    while(len(unchecked) > 0):
        head = unchecked.pop(0)
        if head in accepted:
            raise RuntimeError("minimized edge " + head + " in the same path already before! Possible loss of money")
        accepted.insert(0, head)

    amount = amountOf(path)
    if amount == 0:
        return 
    for e in accepted:
        if not e in graphEdges:
            raise ValueError("edge " + e + " is not in graph")
        graphEdges[e].amount -= amount

def pathToEdgeSequence(path):
    result = []
    for i in range(0, len(path) - 1):
        result.append(TransactionEdge(path[i], path[i+1], 0).keyify())
    return result


def amountOf(path):
    if len(path) < 2:
        return 0 
    amount = float("inf")
    for edgeId in pathToEdgeSequence(path):
        if not edgeId in graphEdges:#path not in graph? Amount of 0
           raise ValueError("edge " + edgeId + " not in graph") 
        curAmount = graphEdges[edgeId].amount
        if curAmount < amount:
            amount = curAmount
    if amount == float("inf"):
        amount = 0
    return amount
