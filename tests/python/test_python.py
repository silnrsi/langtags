#!/usr/bin/python

from langtag import lookup, langtag, LangTags
from pathlib import Path
import unittest

langtagjson = Path(__file__).parent.parent.parent / 'source' / 'langtags.json'
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

    def test_variant_no_tags(self):
        # tagsets without a tags list used to raise KeyError
        lt = self.lt.get("aa-Latn-DJ-fonipa")
        self.assertEqual(str(lt.full), "aa-Latn-DJ-fonipa")

    def test_variant_cache(self):
        n = len(self.lt._tags)
        first = self.lt.get("th-fonipa")
        self.assertEqual(first.full.script, "Latn")
        self.assertEqual(len(self.lt._tags), n)
        self.assertIs(self.lt.get("th-fonipa"), first)

    def test_bad_tag(self):
        self.assertIsNone(self.lt.get("en-a1-zz"))
        self.assertFalse("" in self.lt)

    def test_matchregions_not_sticky(self):
        lookup("en-GB", fname=langtagjson, matchRegions=True)
        self.assertFalse(self.lt.matchRegions)


class Parse(unittest.TestCase):

    def test_good(self):
        tests = {
            "sl-rozaj-1994": ("sl", None, None, ["rozaj", "1994"], None),
            "en-1994": ("en", None, None, ["1994"], None),
            "zh-Yue-HK": ("zh-yue", None, "HK", None, None),
            "x-foo-bar": (None, None, None, None, {"x": ["foo", "bar"]}),
            "en-x-a-b": ("en", None, None, None, {"x": ["a", "b"]}),
            "en-Latn-US-fonipa-u-nu-thai-x-a": ("en", "Latn", "US", ["fonipa"], {"u": ["nu", "thai"], "x": ["a"]}),
        }
        for s, r in tests.items():
            self.assertEqual(tuple(langtag(s)), r, s)
            self.assertEqual(str(langtag(s)).lower(), s.lower())

    def test_bad(self):
        for s in ("", "-Latn", "en-a1-fonipa", "en-1abcdefghi", "en-abc-def-ghi-jkl", "en-a", "en-a-bb-a-cc"):
            with self.assertRaises(SyntaxError, msg=s):
                langtag(s)

    def test_str_order(self):
        self.assertEqual(str(langtag("en-z-abc-b-def-x-foo")), "en-b-def-z-abc-x-foo")
        self.assertEqual(str(langtag("x-foo")), "x-foo")

    def test_matched(self):
        full = langtag("en-Latn-US-fonipa-simple-u-nu-thai")
        for p in ("en", "en-simple-fonipa", "en-u-nu-thai", "en-Latn"):
            self.assertTrue(full.matched(langtag(p)), p)
        for p in ("en-GB", "en-fonupa", "en-u-nu-arab", "en-x-foo"):
            self.assertFalse(full.matched(langtag(p)), p)


if __name__ == "__main__":
    unittest.main()


