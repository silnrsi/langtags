#!/usr/bin/python

from langtag import lookup, langtag, LangTags
from pathlib import Path
import unittest

langtagjson = Path(__file__).parent.parent.parent / 'pub' / 'langtags.json'
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

    def test_online_fetch(self):
        import site
        from tempfile import TemporaryDirectory
        with TemporaryDirectory(prefix="langtags_test", suffix=".cache", dir=site.getuserbase()) as prefix:
            lts = LangTags(cachedprefix=prefix)
            lt = lts.get("en")
            self.assertEqual(lt.lang, "en")
            self.assertEqual(lt.script, "Latn")
            self.assertEqual(lt.region, "US")

if __name__ == "__main__":
    unittest.main()


