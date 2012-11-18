import unittest
import sys

sys.path.append('utils/')
from TransactionGraph import *
sys.path.append('model/')
from UserNodeModel import UserNode
from TransactionEdgeModel import TransactionEdge

class TestTransactionGraph(unittest.TestCase):

    def setUp(self):
        graphNodes.clear()
        graphEdges.clear()

    def testInsertNode(self):
        insertNode(UserNode(123))
        self.assertTrue(cmpDicts(graphNodes, {123: UserNode(123)}))
        self.assertTrue(cmpDicts(graphEdges, {}))
    
    def testInsertEdge(self):
        edge = TransactionEdge(123, 321, 22.1)
        insertEdge(edge)
        self.assertTrue(cmpDicts(graphNodes, {123: UserNode(123), 321: UserNode(321)}))
        self.assertTrue(cmpDicts(graphEdges, {edge.keyify(): edge}))

    def testGetPaths(self):
        edgeA = TransactionEdge(0, 1, 1)
        edgeB = TransactionEdge(1, 2, 1)
        edgeC = TransactionEdge(0, 3, 1)
        edgeD = TransactionEdge(2, 4, 1)
        edgeE = TransactionEdge(1, 3, 1)
        insertEdge(edgeA)
        insertEdge(edgeB)
        insertEdge(edgeC)
        insertEdge(edgeD)
        insertEdge(edgeE)
        self.assertEqual([[0]], getPaths(0, 0))
        self.assertEqual([[0, 1, 2, 4]], getPaths(0, 4))
        self.assertEqual([], getPaths(4, 0))
        res = getPaths(0, 3)
        self.assertTrue([[0, 3], [0, 1, 3]] == res or res == [[0, 1, 3], [0, 3]])

    def testGetCycle(self):
        insertEdge(TransactionEdge('a', 'b', 1))
        insertEdge(TransactionEdge('b', 'c', 1))
        insertEdge(TransactionEdge('c', 'a', 1))
        insertEdge(TransactionEdge('c', 'b', 1))
        self.assertEqual([[graphNodes['a'], graphNodes['b'], graphNodes['c'], graphNodes['a']]], getCycles('a'))
        subA = [graphNodes['b'], graphNodes['c'], graphNodes['b']]
        subB = [graphNodes['b'], graphNodes['c'], graphNodes['a'], graphNodes['b']]
        res = getCycles('b')
        self.assertTrue(res == [subA, subB] or res == [subB, subA])

    def testAmountOf(self):
        insertEdge(TransactionEdge('a', 'b', 1))
        insertEdge(TransactionEdge('b', 'c', 2))
        insertEdge(TransactionEdge('c', 'a', 5))
        insertEdge(TransactionEdge('a', 'd', 3))
        insertEdge(TransactionEdge('d', 'a', 4))
        insertEdge(TransactionEdge('c', 'b', 3))
        self.assertEqual(amountOf(getPaths('a', 'c')[0]), 1)


        



def cmpDicts(a, b):
    if a.keys() != b.keys():
        print "a has different keys than B: " + str(a.keys()) + " vs. " + str(b.keys())
        return False
    for k in a.keys():
        if b[k] != a[k]:
            print "element with key " + k + " are different: " + a[k] + " vs. " + b[k]
            return False
    return True
if __name__ == '__main__':
  unittest.main()
