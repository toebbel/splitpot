#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import sys

sys.path.append('utils/')
from TransactionGraph import *
from UserNodeModel import UserNode
from TransactionEdgeModel import TransactionEdge


class TestTransactionGraph(unittest.TestCase):

    def setUp(self):
        """
        Called before *each* testcase. We want to operate on a fresh database
        """

        clearTransactionGraph()

    def testInsertNode(self):
        insertNode(UserNode('a'))
        self.assertEqual(1, len(graphNodes))

    def testInsertEdge(self):

        # edge creates nodes

        e = TransactionEdge('a', 'b', 10)
        insertEdge(e)
        self.assertEqual({'a': UserNode('a'), 'b': UserNode('b')},
                         graphNodes)
        self.assertEqual({e.keyify(): e}, graphEdges)
        self.assertEqual({'b': e}, graphNodes['a'].outgoing)
        self.assertEqual({'a': e}, graphNodes['b'].incoming)

        # doesn't create new nodes if not neseccary

        e2 = TransactionEdge('b', 'c', 5)
        insertEdge(e2)
        self.assertEqual({'a': UserNode('a'), 'b': UserNode('b'),
                         'c': UserNode('c')}, graphNodes)
        self.assertEqual({e.keyify(): e, e2.keyify(): e2}, graphEdges)
        self.assertEqual({'b': e}, graphNodes['a'].outgoing)
        self.assertEqual({'a': e}, graphNodes['b'].incoming)
        self.assertEqual({'c': e2}, graphNodes['b'].outgoing)
        self.assertEqual({'b': e2}, graphNodes['c'].incoming)

        # adding of existing edges increases their amount

        e3 = TransactionEdge('b', 'c', 2)
        insertEdge(e3)
        self.assertDictEqual({e.keyify(): e, e2.keyify(): e2},
                             graphEdges)
        self.assertEqual(7, graphEdges[e3.keyify()].amount)
        self.assertEqual(7, e2.amount)
        self.assertEqual({'c': e2}, graphNodes['b'].outgoing)
        self.assertEqual({'b': e2}, graphNodes['c'].incoming)

    def testGetPath_noncyclic(self):
        insertEdge(TransactionEdge('a', 'b', 1))
        insertEdge(TransactionEdge('b', 'c', 2))
        insertEdge(TransactionEdge('b', 'e', 3))
        insertEdge(TransactionEdge('d', 'c', 4))

        p1 = getPaths('a', 'c')
        self.assertEqual(1, len(p1))
        self.assertEqual([graphNodes['a'], graphNodes['b'], graphNodes['c']], p1[0])

        p2 = getPaths('a', 'd')
        self.assertEqual(0, len(p2))
        self.assertEqual([], p2)

        p3 = getPaths('a', 'e')
        self.assertEqual(1, len(p3))
        self.assertEqual([graphNodes['a'], graphNodes['b'], graphNodes['e']], p3[0])

        #a => e = a -> b -> e + a -> f -> e
        insertEdge(TransactionEdge('a', 'f', 5))
        insertEdge(TransactionEdge('f', 'e', 6))

        p4 = getPaths('a', 'e')
        self.assertEqual(2, len(p4))
        self.assertEqual([graphNodes['a'], graphNodes['b'], graphNodes['e']], p4[0])
        self.assertEqual([graphNodes['a'], graphNodes['f'], graphNodes['e']], p4[1])


    def testGetPaths_cyclic(self):
        insertEdge(TransactionEdge('a', 'b', 1))
        insertEdge(TransactionEdge('b', 'c', 1))
        insertEdge(TransactionEdge('a', 'd', 1))
        insertEdge(TransactionEdge('d', 'a', 1))
        insertEdge(TransactionEdge('d', 'c', 1))
        insertEdge(TransactionEdge('c', 'd', 1))
        insertEdge(TransactionEdge('c', 'b', 1))

        p1 = getPaths('a', 'c')
        self.assertEquals(2, len(p1))
        self.assertEquals([graphNodes['a'], graphNodes['b'], graphNodes['c']], p1[0])
        self.assertEquals([graphNodes['a'], graphNodes['d'], graphNodes['c']], p1[1])


    def testAmountOf(self):
        insertEdge(TransactionEdge('a', 'b', 1))
        insertEdge(TransactionEdge('b', 'c', 2))
        insertEdge(TransactionEdge('a', 'f', 3))
        insertEdge(TransactionEdge('a', 'b', 11))

        self.assertEquals(12, amountOf(['a', 'b']))
        self.assertEquals(2, amountOf(['b', 'c']))
        self.assertEquals(2, amountOf(['a', 'b', 'c']))
        self.assertEquals(0, amountOf(['a']))

    def testGetCycle(self):
        insertEdge(TransactionEdge('a', 'b', 1))
        insertEdge(TransactionEdge('b', 'c', 1))
        insertEdge(TransactionEdge('a', 'd', 1))
        insertEdge(TransactionEdge('d', 'a', 1))
        insertEdge(TransactionEdge('d', 'c', 1))
        insertEdge(TransactionEdge('c', 'd', 1))
        insertEdge(TransactionEdge('c', 'b', 1))

        c1 = getCycles('a')
        self.assertEqual(2, len(c1))
        self.assertEqual([graphNodes['a'], graphNodes['b'], graphNodes['c'], graphNodes['d'], graphNodes['a']], c1[0])
        self.assertEqual([graphNodes['a'], graphNodes['d'], graphNodes['a']], c1[1])

        c2 = getCycles('d')
        self.assertEqual(3, len(c2))
        self.assertEqual([graphNodes['d'], graphNodes['a'], graphNodes['b'], graphNodes['c'], graphNodes['d']], c2[0])
        self.assertEqual([graphNodes['d'], graphNodes['a'], graphNodes['d']], c2[1])
        self.assertEqual([graphNodes['d'], graphNodes['c'], graphNodes['d']], c2[2])

    def testNormalizeCycle(self):
        insertNode(UserNode('a'))
        insertNode(UserNode('b'))
        insertNode(UserNode('c'))
        a = graphNodes['a']
        b = graphNodes['b']
        c = graphNodes['c']
        self.assertEqual([a, b, c, a], normalizeCycle([a, b, c, a]))
        self.assertEqual([a, b, c, a], normalizeCycle([b, c, a, b]))
        self.assertEqual([a, b, c, a], normalizeCycle([c, a, b, c]))
    
    
    def testGetAllCycles(self):
        insertEdge(TransactionEdge('a', 'b', 1))
        insertEdge(TransactionEdge('b', 'c', 1))
        insertEdge(TransactionEdge('c', 'a', 1))
        insertEdge(TransactionEdge('c', 'b', 1))
        insertEdge(TransactionEdge('a', 'c', 1))

        c = getAllCycles()
        self.assertEquals(3, len(c))
        self.assertEquals(([graphNodes['a'], graphNodes['c'], graphNodes['a']], 1), c[0])
        self.assertEquals(([graphNodes['a'], graphNodes['b'], graphNodes['c'], graphNodes['a']], 1), c[1])
        self.assertEquals(([graphNodes['b'], graphNodes['c'], graphNodes['b']], 1), c[2])

if __name__ == '__main__':
    unittest.main()
