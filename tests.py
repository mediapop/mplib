from django.test import TestCase

from helpers import friendly_num

class SimpleTest(TestCase):
    def test_friendly_num(self):

        self.failUnlessEqual('2', friendly_num(2))
        self.failUnlessEqual('102', friendly_num(102))
        self.failUnlessEqual('1k', friendly_num(1000))
        self.failUnlessEqual('1k', friendly_num(1010))
        self.failUnlessEqual('10k', friendly_num(10000))
        self.failUnlessEqual('10.2k', friendly_num(10200))
