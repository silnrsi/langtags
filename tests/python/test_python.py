#!/usr/bin/python

import os
from langtag import lookup, langtag, LangTags
import unittest

langtagjson = os.path.join(os.path.dirname(__file__), '..', '..', 'pub', 'langtags.json')
class Basic(unittest.TestCase):

    def setUp(self):
        self.lt = LangTags(fname=langtagjson)

    def test_simple(self):
        lt = langtag("en-Brai-CA-x-strange")
        self.assertEqual(lt.lang, "en")
        self.assertEqual(lt.script, "Brai")
        self.assertEqual(lt.region, "CA")
        self.assertEqual(lt.ns['x'][0], 'strange')

    def test_ltsen(self):
        lt = self.lt.get("en")
        self.assertEqual(lt.lang, "en")
        self.assertEqual(lt.script, "Latn")
        self.assertEqual(lt.region, "US")

    def test_ltfail(self):
        lt = self.lt.get("en-Arab-TH")
        if lt is not None:
            self.fail()

if __name__ == "__main__":
    unittest.main()


