#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import sys
from datetime import datetime

sys.path.append('controller/')

from DatabaseParser import *
import json


class TestDatabaseParser(unittest.TestCase):

    def setUp(self):
        """
        Called before *each* testcase. We want to operate on a fresh database.
        """

        clear()

    def testResolveNick(self):
        self.assertEqual(resolveNick('awesome@0xabc.de'), 'unknown user'
                         )
        registerUser('awesome@0xabc.de')
        self.assertEqual(resolveNick('awesome@0xabc.de'),
                         'awesome@0xabc.de')
        activateUser('awesome@0xabc.de', 'nick', '123456')
        self.assertEqual(resolveNick('awesome@0xabc.de'), 'nick')

    def testVerifyLoginOnEmptyDb(self):
        self.assertFalse(verifyLogin('test@0xabc.de', 'asfelkj'))

    def testRegister(self):
        self.assertTrue(registerUser('benjamin@flowerpower.org'))
        self.assertFalse(registerUser('benJamin@flowerpower.org'))
        self.assertTrue(registerUser('karlaColumna@bild.de'))
        self.assertTrue(userExists('benjamin@flowerpower.org',
                        includeGhosts=True))
        self.assertTrue(userExists('karlaColumna@bild.de',
                        includeGhosts=True))
        self.assertFalse(userExists('benjamin@flowerpower.org'))
        self.assertFalse(userExists('karlaColumna@bild.de'))

    def testActivate(self):
        activateUser('test@0xabc.de', 'test', '123456', True)  # force = register if not present and activate
        self.assertTrue(userExists('test@0xabc.de'))

        self.assertFalse(activateUser('test@0xabc.de', 'test2', '765432'
                         ))

                             # an activated user can't be activated a second time

        registerUser('ghost@test.de')
        self.assertTrue(activateUser('ghost@test.de', 'ghosty', '123456'
                        ))

                            # activate a ghost user

        self.assertTrue(userExists('ghost@test.de'))  # User should be found in "normal" users

    def testListEvents(self):
        activateUser('a', 'alpha', '1', True)
        activateUser('b', 'beta', '2', True)
        activateUser('c', 'charlie', '3', True)
        date_a = datetime.datetime.now
        id_a = insertEvent('a', '1.4.2013', 10, ['b'], 'Event1')
        print listEvents()
        self.assertEqual(listEvents(), [(
            id_a,
            u'a',
            '1.4.2013',
            10,
            u'["b"]',
            u'Event1',
            )])

    def testListEvents_emptyDB(self):
        listEvents()

    def testGetPassword_NonexistentUser(self):
        getPassword('martin@0xabc.de')

    def testGetPassword(self):
        activateUser('awesome@0xabc.de', 'Bluemchen', 'blume', True)
        getPassword('awesome@0xabc.de')

    def testInsertEvent(self):
        activateUser('awesome@0xabc.de', 'Bluemchen', 'blume', True)
        insertEvent('awesome@0xabc.de', '4.1.2010', 12.1,
                    ['tobstu@0xabc.de'], 'An Event')

    def testSetEventStatus(self):
        setEventStatus('tobstu@gmail.com', 2, 'paid')

    def testResetUrl(self):
        activateUser('dummy@0xabc.de', 'dummy', 'thisIsMyPwd', True)
        reset = getResetUrlKey('dummy@0xabc.de')
        self.assertTrue(str(reset).__len__() == 8)
        self.assertTrue(isValidResetUrlKey('dummy@0xabc.de', reset))

    def testResetLogin(self):
        activateUser('userA@0xabc.de', 'A', '123456', True)
        activateUser('userB@0xabc.de', 'B', '654321', True)
        self.assertFalse(updateLogin('userC@0xabc.de', 'ffffff'))
        self.assertTrue(updateLogin('userb@0xabc.de', 'abcdef'))
        self.assertFalse(verifyLogin('userB@0xabc.de', '654321'))
        self.assertTrue(verifyLogin('userB@0xabc.de', 'abcdef'))
        self.assertTrue(verifyLogin('userA@0xabc.de', '123456'))

    def testGetEvent(self):
        activateUser('userA@0xabc.de', 'A', '123456', True)
        id = insertEvent('userA@0xabc.de', '10.4.2013', 101.12,
                         ['tobstu@gmail.com'], 'comment')
        self.assertEqual(getEvent(id + 1), None)
        print str(getEvent(id))
        self.assertEqual(str(getEvent(id)), str(Event(
            id=id,
            owner='userA@0xabc.de',
            date='10.4.2013',
            amount=101.12,
            participants=['tobstu@gmail.com'],
            comment='comment',
            )))

    def testBuildTransactionTree(self):
        registerUser('userA@0xabc.de')
        registerUser('userB@0xabc.de')
        registerUser('userC@0xabc.de')
        insertEvent('userA@0xabc.de', '1.1.2010', 12, ['userB@0xabc.de'
                    , 'userC@0xabc.de'], 'event1')
        insertEvent('userA@0xabc.de', '1.1.2010', 2, ['userC@0xabc.de'
                    ], 'event2')
        insertEvent('userB@0xabc.de', '1.1.2010', 3.3, ['userA@0xabc.de'
                    , 'userC@0xabc.de'], 'event3')
        buildTransactionTree()
        self.assertIn('userA@0xabc.de', graphNodes)  # node for every user?
        self.assertIn('userB@0xabc.de', graphNodes)
        self.assertIn('userC@0xabc.de', graphNodes)

        # entries from B to A and C (event3)

        self.assertIn('userA@0xabc.de', graphNodes['userB@0xabc.de'
                      ].incoming.keys())
        self.assertIn('userC@0xabc.de', graphNodes['userB@0xabc.de'
                      ].incoming.keys())
        self.assertEqual(graphNodes['userB@0xabc.de'
                         ].incoming['userA@0xabc.de'],
                         TransactionEdge('userA@0xabc.de',
                         'userB@0xabc.de', 1.1))
        self.assertEqual(graphNodes['userB@0xabc.de'
                         ].incoming['userC@0xabc.de'],
                         TransactionEdge('userC@0xabc.de',
                         'userB@0xabc.de', 1.1))
        self.assertIn('userB@0xabc.de', graphNodes['userA@0xabc.de'
                      ].outgoing.keys())
        self.assertIn('userB@0xabc.de', graphNodes['userC@0xabc.de'
                      ].outgoing.keys())

        # entries hosted by A for C

        self.assertIn('userC@0xabc.de', graphNodes['userA@0xabc.de'
                      ].incoming.keys())
        self.assertEqual(graphNodes['userA@0xabc.de'
                         ].incoming['userC@0xabc.de'],
                         TransactionEdge('userC@0xabc.de',
                         'userA@0xabc.de', 5))  # (12/4 + 2/2)
        self.assertEqual(graphNodes['userC@0xabc.de'
                         ].outgoing['userA@0xabc.de'],
                         TransactionEdge('userC@0xabc.de',
                         'userA@0xabc.de', 5))

        # entries hosted by A for B

        self.assertIn('userB@0xabc.de', graphNodes['userA@0xabc.de'
                      ].incoming.keys())
        self.assertEqual(graphNodes['userA@0xabc.de'
                         ].incoming['userB@0xabc.de'],
                         TransactionEdge('userB@0xabc.de',
                         'userA@0xabc.de', 4))
        self.assertEqual(graphNodes['userB@0xabc.de'
                         ].outgoing['userA@0xabc.de'],
                         TransactionEdge('userB@0xabc.de',
                         'userA@0xabc.de', 4))

    def testGetEvent(self):
        activateUser('userA@0xabc.de', 'A', '123456', True)
        id = insertEvent('userA@0xabc.de', '10-04-2013', 101.12,
                         ['tobstu@gmail.com'], 'comment')
        self.assertEqual(getEvent(id + 1), None)
        print str(getEvent(id))
        self.assertEqual(str(getEvent(id)), str(Event(
            id=id,
            owner='userA@0xabc.de',
            date='10-04-2013',
            amount=101.12,
            participants=['tobstu@gmail.com'],
            comment='comment',
            )))

    def testMergeUser(self):
        activateUser('jobs@0xabc.de', 'Steve Jobs', 'apple', True)
        activateUser('gates@0xabc.de', 'Bill Gates', 'microsoft', True)
        activateUser('buffet@0xabc.de', 'Warren Buffet', 'billion',
                     True)
        id = insertEvent('jobs@0xabc.de', '20-12-2012', 21.22,
                         ['gates@0xabc.de', 'buffet@0xabc.de'],
                         'Dinner with my besties')
        insertEvent('gates@0xabc.de', '20-12-2012', 1.22,
                    ['buffet@0xabc.de'], 'Dinner with my besties')

        self.assertFalse(mergeUser('sinofsky@0xabc.de', 'jobs@0xabc.de'
                         ))

                             # sinofski doesn't exist

        self.assertTrue(mergeUser('gates@0xabc.de', 'jobs@0xabc.de'))

        self.assertNotEqual(str(getEvent(id)), str(Event(
            id=id,
            owner='jobs@0xabc.de',
            date='20-12-2012',
            amount=21.22,
            participants=['gates@0xabc.de', 'buffet@0xabc.de'],
            comment='Dinner with my besties',
            )))

        self.assertEqual(str(getEvent(id)), str(Event(
            id=id,
            owner='gates@0xabc.de',
            date='20-12-2012',
            amount=21.22,
            participants=['gates@0xabc.de', 'buffet@0xabc.de'],
            comment='Dinner with my besties',
            )))

        self.assertEqual(str(getEvent(id + 1)), str(Event(
            id=id + 1,
            owner='gates@0xabc.de',
            date='20-12-2012',
            amount=1.22,
            participants=['buffet@0xabc.de'],
            comment='Dinner with my besties',
            )))

    def testMergeUrlKey(self):
        activateUser('jobs@0xabc.de', 'Steve Jobs', 'apple', True)
        activateUser('gates@0xabc.de', 'Bill Gates', 'microsoft', True)
        merge = getMergeUrlKey('jobs@0xabc.de', 'gates@0xabc.de')
        self.assertTrue(len(merge) == 16)
        self.assertTrue(isValidMergeUrlKey(merge))

    def testGetUserFromPassword(self):
        activateUser('jobs@0xabc.de', 'Steve Jobs', 'apple', True)
        pwd = getPassword('jobs@0xabc.de')
        self.assertIsNone(getUserFromPassword('aerafe'))
        self.assertEqual('jobs@0xabc.de', getUserFromPassword(pwd[:3]))

    def testIsUserInEvent(self):
        activateUser('jobs@0xabc.de', 'Steve Jobs', 'apple', True)
        activateUser('buffet@0xabc.de', 'Warren Buffet', 'billion',
                     True)
        activateUser('gates@0xabc.de', 'Bill Gates', 'microsoft', True)
        id = insertEvent('jobs@0xabc.de', '12-12-2012', 1.00,
                         ['gates@0xabc.de'], 'BFFs')
        self.assertFalse(isUserInEvent('buffet@0xabc.de', id))
        self.assertTrue(isUserInEvent('jobs@0xabc.de', id))
        self.assertTrue(isUserInEvent('gates@0xabc.de', id))

    def testAutocomplete(self):

        # on empty DB

        self.assertEqual(getAutocompleteUser('cookiemonster@sesamstreet.xxx'
                         , 'a'), json.dumps([]))

        # multiple users but no visibility

        registerUser('cookiemonster@sesamstreet.xxx')
        activateUser('awesome@0xabc.de', 'awesome', 'awesome', True)
        activateUser('martin@0xabc.de', 'martin', 'martin', True)

        # add single visibility

        self.assertEqual(getAutocompleteUser('cookiemonster@sesamstreet.xxx'
                         , 'awe'), json.dumps([]))
        self.assertTrue(addAutocompleteEntry('cookiemonster@sesamstreet.xxx'
                        , 'awesome@0xabc.de'))
        self.assertEqual(getAutocompleteUser('cookiemonster@sesamstreet.xxx'
                         , 'awe'),
                         json.dumps([{'value': 'awesome@0xabc.de',
                         'name': 'awesome (awesome@0xabc.de)'}]))
        self.assertEqual(getAutocompleteUser('awesome@0xabc.de', 'coo'
                         ), json.dumps([]))
        self.assertEqual(getAutocompleteUser('martin@0xabc.de', 'aw'),
                         json.dumps([]))

        # add duble visibility

        self.assertFalse(addAutocompleteEntry('cookiemonster@sesamstreet.xxx'
                         , 'awesome@0xabc.de'))

        # two different visibility connections

        self.assertTrue(addAutocompleteEntry('cookiemonster@sesamstreet.xxx'
                        , 'martin@0xabc.de'))

        self.assertEqual(getAutocompleteUser('cookiemonster@sesamstreet.xxx'
                         , 'awe'),
                         json.dumps([{'value': 'awesome@0xabc.de',
                         'name': 'awesome (awesome@0xabc.de)'}]))
        self.assertEqual(getAutocompleteUser('cookiemonster@sesamstreet.xxx'
                         , 'm'), json.dumps([{'value': 'martin@0xabc.de'
                         , 'name': 'martin (martin@0xabc.de)'}]))


if __name__ == '__main__':
    unittest.main()
