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
        self.assertRaises(ValueError, amountOf, (['d', 'b'])) #amount of nonexistent path
        self.assertEqual(amountOf(['a', 'b', 'c']), 1)
        self.assertEqual(amountOf(['a', 'b', 'c', 'a']), 1)
        self.assertEqual(amountOf(['a', 'b', 'c', 'b', 'c', 'a', 'd', 'a']), 1)
        self.assertEqual(amountOf(['a', 'd', 'a']), 3)
        self.assertEqual(amountOf(['a']), 0)

    def testPathToEdgeSequence(self):
        self.assertEqual([], pathToEdgeSequence([]))
        self.assertEqual([], pathToEdgeSequence(['a']))
        e1 = TransactionEdge('a', 'b', 0).keyify()
        self.assertEqual([e1], pathToEdgeSequence(['a', 'b']))
        e2 = TransactionEdge('b', 'c', 0).keyify()
        self.assertEqual([e1, e2], pathToEdgeSequence(['a', 'b', 'c']))

    def testMinimize(self):
        e1 = TransactionEdge('a', 'b', 1)
        e2 = TransactionEdge('b', 'c', 2)
        e3 = TransactionEdge('c', 'a', 5)
        e4 = TransactionEdge('a', 'd', 3)
        e5 = TransactionEdge('d', 'a', 4)
        e6 = TransactionEdge('c', 'b', 3)
        insertEdge(e1)
        insertEdge(e2)
        insertEdge(e3)
        insertEdge(e4)
        insertEdge(e5)
        insertEdge(e6)
        minimizePath(['a', 'd', 'a'])
        self.assertEquals(e4.amount, 0)
        self.assertEquals(e5.amount, 1)
        
        minimizePath(['a', 'd', 'a']) # call again: should change nothing
        self.assertEquals(e4.amount, 0)
        self.assertEquals(e5.amount, 1)
        
        self.assertRaises(RuntimeError, minimizePath, (['a', 'b', 'c', 'b', 'c', 'a']))#should change nothing!
        self.assertEquals(e1.amount, 1)
        self.assertEquals(e2.amount, 2)
        self.assertEquals(e3.amount, 5)

        minimizePath(['a', 'b', 'c', 'a'])
        self.assertEquals(e1.amount, 0)
        self.assertEquals(e2.amount, 1)
        self.assertEquals(e3.amount, 4)

        self.assertRaises(RuntimeError, minimizePath, (['a', 'b']))

    def testRemoveUnusedEdges(self):
        e1 = TransactionEdge('a', 'b', 0)
        e2 = TransactionEdge('b', 'c', 2)
        e3 = TransactionEdge('c', 'a', 5)
        e4 = TransactionEdge('a', 'd', 0)
        e5 = TransactionEdge('d', 'a', 4)
        e6 = TransactionEdge('c', 'b', 0)
        insertEdge(e1)
        insertEdge(e2)
        insertEdge(e3)
        insertEdge(e4)
        insertEdge(e5)
        insertEdge(e6)
        self.assertTrue(removeUnusedEdges())
        self.assertNotIn(e1.keyify(), graphEdges.keys())
        self.assertIn(e2.keyify(), graphEdges.keys())
        self.assertIn(e3.keyify(), graphEdges.keys())
        self.assertNotIn(e4.keyify(), graphEdges.keys())
        self.assertIn(e5.keyify(), graphEdges.keys())
        self.assertNotIn(e6.keyify(), graphEdges.keys())
        self.assertFalse(removeUnusedEdges())


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
