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
        edge = TransactionEdge(123, 321, 22.1, 1)
        insertEdge(edge)
        self.assertTrue(cmpDicts(graphNodes, {123: UserNode(123), 321: UserNode(321)}))
        self.assertTrue(cmpDicts(graphEdges, {edge.keyify(): edge}))

    def testGetPath1(self):
        edgeA = TransactionEdge(0, 1, 1, 1)
        edgeB = TransactionEdge(1, 2, 1, 2)
        edgeC = TransactionEdge(0, 3, 1, 3)
        edgeD = TransactionEdge(2, 4, 1, 4)
        insertEdge(edgeA)
        insertEdge(edgeB)
        insertEdge(edgeC)
        insertEdge(edgeD)
        self.assertEqual([0], getPath(0, 0))
        self.assertEqual([0, 1, 2, 4], getPath(0, 4))
        self.assertEqual(None, getPath(4, 0))
        self.assertEqual([0, 3], getPath(0, 3))

    def testGetCycle(self):
        insertEdge(TransactionEdge('a', 'b', 1, 0))
        insertEdge(TransactionEdge('b', 'c', 1, 1))
        insertEdge(TransactionEdge('c', 'a', 1, 2))
        insertEdge(TransactionEdge('c', 'b', 1, 3))
        self.assertEqual(['a', 'b', 'c', 'a'], getCycle('a'))
        res2 = getCycle('b')
        self.assertTrue(res2 == ['b', 'c', 'b'] or res2 == ['b', 'c', 'a', 'b'])

    def testMinimizePath(self):
        insertEdge(TransactionEdge('a', 'b', 1, 0))
        insertEdge(TransactionEdge('b', 'c', 2, 1))
        insertEdge(TransactionEdge('c', 'a', 5, 2))
        insertEdge(TransactionEdge('a', 'd', 3, 0))
        insertEdge(TransactionEdge('d', 'a', 4, 3))
        insertEdge(TransactionEdge('c', 'b', 3, 4))
        #assertEqual(amountOf(getPath('a', 'a'

        



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
