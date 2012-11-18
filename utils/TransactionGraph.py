import sys
sys.path.append('model/')
from TransactionEdgeModel import TransactionEdge
from UserNodeModel import UserNode
from copy import copy

graphNodes = {}
graphEdges = {}

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
    Adds an edge to the graph structure. Adds nodes, if they are not existent.
    """
    if not isinstance(edge, TransactionEdge):
        raise TypeError("parameter is not a transaction edge")
    if not edge.keyify() in graphEdges.keys():
        insertNode(UserNode(edge.fromUser))
        insertNode(UserNode(edge.toUser))
        graphNodes[edge.fromUser].addOutEdge(edge)
        graphNodes[edge.toUser].addInEdge(edge)
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
            del graphEdge[e]
            mod = True
    return mod

def minimizePath(path):
    amount = amountOf(path)
    for e in path:
        graphEdges[e.keyify()].amount -= amount

def amountOf(path):
    amount = float("inf")
    for p in path:
        if p.amount < amount:
            amount = p.amount
    return amount
