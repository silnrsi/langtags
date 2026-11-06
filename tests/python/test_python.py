#!/usr/bin/python

from langtag import lookup, langtag, LangTags
from pathlib import Path
import unittest, json, os

langtagjson = Path(__file__).parent.parent.parent / 'source' / 'langtags.json'
def report(title, sections):
    ''' Returns a labelled list of what needs fixing, or None if no section
        (heading, list of items) has items. '''
    msg = []
    for heading, items in sections:
        if items:
            msg.append("\n" + heading)
            msg.append("    " + ", ".join(items))
    if msg:
        n = sum(len(i) for h, i in sections)
        return "\n{} {} item(s) to fix.".format(title, n) + "\n".join(msg)


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
        self.assertEqual(str(lt.full), "aa-Latn-ET-fonipa")
        self.assertIn("DJ", lt.regions)

    def test_phonetic(self):
        # one phonetic set per language, from its tagset without nophonvars,
        # in Latin script and covering every region of the language
        lt = self.lt.get("th-fonipa")
        self.assertEqual(str(lt.full), "th-Latn-TH-fonipa")
        for t in ("th-Latn-fonipa", "th-Latn-TH-fonipa", "th-TH-fonipa", "th-US-fonipa"):
            self.assertIs(self.lt.get(t), lt, t)
        self.assertEqual(lt.name, "Thai")
        for t in ("th-Thai-fonipa", "zhk-fonipa", "th-fonipa-fonupa"):
            self.assertIsNone(self.lt.get(t), t)
        lt = self.lt.get("mey-SN-fonipa")
        self.assertEqual(len(lt.tags), len(set(map(str, lt.tags))))
        self.assertIn("SN", [t.region for t in lt.allTags()] + lt.regions)

    def test_variant_cache(self):
        n = len(self.lt._tags)
        first = self.lt.get("th-fonipa")
        self.assertEqual(first.full.script, "Latn")
        self.assertEqual(len(self.lt._tags), n)
        self.assertIs(self.lt.get("th-fonipa"), first)

    def test_bad_tag(self):
        self.assertIsNone(self.lt.get("en-a1-zz"))
        self.assertFalse("" in self.lt)

    def test_local_variants(self):
        # variants and svariants listed on the base tagset
        for t, full in (("be-tarask", "be-Cyrl-BY-tarask"), ("el-polyton", "el-Grek-GR-polyton"),
                        ("ja-Latn-hepburn-heploc", "ja-Latn-JP-hepburn-heploc"),
                        ("be-tarask-simple", "be-Cyrl-BY-tarask-simple"),
                        ("en-scouse-fonipa", "en-Latn-US-scouse-fonipa")):
            lt = self.lt.get(t)
            self.assertIsNotNone(lt, t)
            self.assertEqual(str(lt.full), full, t)
        # every tag of a derived set looks up to the same set
        lt = self.lt.get("be-tarask")
        for t in lt.allTags(use639=False):
            self.assertIs(self.lt.get(str(t)), lt, str(t))

    def test_variant_order(self):
        # variants are found in any order and returned in canonical order:
        # language variant, script or phonetic variant, then global variant
        for t, full in (("ja-Latn-heploc-hepburn", "ja-Latn-JP-hepburn-heploc"),
                        ("ja-Latn-simple-hepburn-heploc", "ja-Latn-JP-hepburn-heploc-simple"),
                        ("en-fonipa-scouse", "en-Latn-US-scouse-fonipa"),
                        ("be-simple-tarask", "be-Cyrl-BY-tarask-simple"),
                        ("ca-simple-valencia", "ca-Latn-ES-valencia-simple")):
            self.assertEqual(str(self.lt.get(t).full), full, t)

    def test_private_use_fallback(self):
        # unrecognised private use and extensions are ignored (RFC 4647 4.1)
        for t, full in (("en-x-foo", "en-Latn-US"), ("en-GB-x-foo", "en-Latn-GB"),
                        ("en-u-nu-thai", "en-Latn-US"), ("vi-x-central-foo", "vi-Latn-VN-x-central"),
                        ("vi-simple-x-central", "vi-Latn-VN-simple-x-central")):
            self.assertEqual(str(self.lt.get(t).full), full, t)

    def test_synthesised_fields(self):
        # windows gains the variants (and Latn for phonetic sets), sldr is
        # unknown, and a used slot no longer offers variants
        lt = self.lt.get("th-fonipa")
        self.assertEqual((lt.windows, lt.sldr, lt.nophonvars), ("th-Latn-fonipa", False, True))
        self.assertFalse(hasattr(lt, "suppress"))
        lt = self.lt.get("en-fonipa")
        self.assertIn("scouse", lt.variants)
        lt = self.lt.get("be-tarask")
        self.assertEqual((lt.windows, lt.nophonvars), ("be-tarask", True))
        self.assertFalse(hasattr(lt, "svariants"))
        lt = self.lt.get("en-scouse")
        self.assertFalse(getattr(lt, "nophonvars", False))
        self.assertFalse(hasattr(lt, "variants"))

    def test_sldrfile(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as sldr:
            os.mkdir(os.path.join(sldr, "b"))
            for f in ("b/be.xml", "b/be_TARASK.xml", "b/be_BY.xml"):
                open(os.path.join(sldr, f), "w").close()
            be = self.lt.get("be-UA")
            self.assertEqual(be.sldrFile("be-UA"), "be.xml")      # no tree: base locale
            self.assertEqual(be.sldrFile("be-UA", sldr), os.path.join(sldr, "b", "be.xml"))
            self.assertEqual(be.sldrFile("be-BY", sldr), os.path.join(sldr, "b", "be_BY.xml"))
            tk = self.lt.get("be-tarask")
            self.assertEqual(tk.sldrFile("be-tarask", sldr), os.path.join(sldr, "b", "be_TARASK.xml"))
            have = {"be.xml", "be_TARASK.xml"}
            self.assertEqual(tk.sldrFile("be-tarask", exists=have.__contains__), "be_TARASK.xml")
            self.assertEqual(be.sldrFile("be-BY", exists=have.__contains__), "be.xml")
            os.remove(os.path.join(sldr, "b", "be_TARASK.xml"))
            from langtag import _dirlists
            _dirlists.clear()
            self.assertEqual(tk.sldrFile("be-tarask", sldr), os.path.join(sldr, "b", "be.xml"))

    def test_his_codes(self):
        # x-HIS<n>: the dialect tagset with that rod, else a dialect synthesised
        # from the tagset listing n in its rolv
        for t, full in (("aae-x-his06861", "aae-Latn-IT-x-sub84"), ("aae-x-HIS6861", "aae-Latn-IT-x-sub84"),
                        ("aae-simple-x-his06861", "aae-Latn-IT-simple-x-sub84"),
                        ("aae-x-his06862", "aae-Latn-IT-x-his06862"),
                        ("ar-x-his04501", "ar-Arab-SA-x-his04501"),
                        ("ar-Brai-x-his04501", "ar-Brai-SA-x-his04501")):
            self.assertEqual(str(self.lt.get(t, strict=True).full), full, t)
        lt = self.lt.get("aae-x-his06862")
        self.assertEqual((lt.rod, lt.sldr), ("06862", False))
        for t in lt.allTags(use639=False):
            self.assertIs(self.lt.get(str(t)), lt, str(t))
        # an unknown code is ignored unless strict; another language's code is an error
        self.assertEqual(str(self.lt.get("aae-x-his99999").full), "aae-Latn-IT")
        self.assertIsNone(self.lt.get("aae-x-his99999", strict=True))
        self.assertIsNone(self.lt.get("en-x-his06861"))

    def test_strict(self):
        self.assertIsNone(self.lt.get("en-x-foo", strict=True))
        self.assertEqual(str(self.lt.get("en-u-nu-thai", strict=True).full), "en-Latn-US")
        self.assertEqual(str(self.lt.get("vi-x-central", strict=True).full), "vi-Latn-VN-x-central")

    def test_variant_lockouts(self):
        # at most one from variants+globalvar, one from svariants+phonvar,
        # and no svariant with a phonetic variant
        for t in ("be-tarask-fonipa", "en-fonipa-fonxsamp", "bg-ivanchov-simple",
                  "be-tarask-1959acad", "th-Thai-fonipa", "en-tarask",
                  "ja-Latn-heploc"):    # heploc requires hepburn
            self.assertIsNone(self.lt.get(t), t)

    def test_matchregions_not_sticky(self):
        lookup("en-GB", fname=langtagjson, matchRegions=False)
        self.assertTrue(self.lt.matchRegions)

    def test_region_resolution(self):
        # base tagset listing the region, else the only tagset listing it
        for t, full in (("en-AS", "en-Latn-US"), ("amw-PS", "amw-Arab-SY"),
                        ("sl-IT-rozaj-solba", "sl-Latn-SI-rozaj-solba")):
            self.assertEqual(str(self.lt.get(t).full), full, t)
        self.assertIsNone(self.lt.get("en-Latn-AQ"))


sldrdir = Path(os.environ.get("SLDR", langtagjson.parent.parent.parent / "sldr" / "sldr"))
SLDR_SPECIAL = {"root", "test"}

class SLDR(unittest.TestCase):
    ''' Consistency between langtags.json and an SLDR checkout (set $SLDR or
        have ../sldr/sldr next to this repository). The sldr entry of a tagset is
        for its base locale, which must exist whenever any locale of it does. '''

    @classmethod
    def setUpClass(cls):
        if not sldrdir.is_dir():
            raise unittest.SkipTest("No SLDR found at {}".format(sldrdir))
        cls.lt = LangTags(fname=langtagjson)
        cls.files = {f.stem.lower(): f.stem for f in sldrdir.glob("*/*.xml")}
        with open(langtagjson, encoding="utf-8") as inf:
            cls.tagsets = [t for t in json.load(inf) if not t["tag"].startswith("_")]

    def _hasbase(self, ts):
        return any(str(t).replace("-", "_").lower() in self.files for t in ts.allTags())

    def test_sldr_flag(self):
        ''' sldr is true exactly when the base locale has an SLDR file '''
        settrue, setfalse = [], []
        for t in self.tagsets:
            forms = [t["tag"], t.get("full", t["tag"])] + t.get("tags", [])
            found = [self.files[f.replace("-", "_").lower()] + ".xml" for f in forms
                        if f.replace("-", "_").lower() in self.files]
            if found and not t.get("sldr", False):
                settrue.append(t.get("full", t["tag"]))
            elif not found and t.get("sldr", False):
                setfalse.append(t.get("full", t["tag"]))
        msg = report("Wrong \"sldr\" flag in source/langtags.json (SLDR at {}).".format(sldrdir), [
            ("Set \"sldr\": true on these tagsets (an SLDR file exists for one of their tags):", settrue),
            ("Set \"sldr\": false on these tagsets (no SLDR file for any of their tags):", setfalse)])
        if msg:
            self.fail(msg)

    def test_sldr_files_have_base(self):
        ''' every SLDR file is a locale of a tagset whose base locale exists. A file
            with variants is ok if its non-variant locale's tagset has a file. '''
        notag, nobase, unparsed = [], [], []
        for low, stem in sorted(self.files.items()):
            if low in SLDR_SPECIAL:
                continue
            try:
                l = langtag(stem.replace("_", "-"))
            except SyntaxError:
                unparsed.append(stem + ".xml")
                continue
            if l.lang is not None and "qaa" <= l.lang <= "qtz":
                continue
            if l.vars:
                l = l._replace(vars=None)
            ts = self.lt.get(str(l), matchRegions=True)
            if ts is None:
                notag.append(stem + ".xml")
            elif not self._hasbase(ts):
                nobase.append("{}.xml ({})".format(stem, ts.full))
        msg = report("SLDR files (at {}) that source/langtags.json does not account for.".format(sldrdir), [
            ("No tagset: add a tagset, or a tag to an existing tagset, for the locale; or rename or remove the SLDR file:", notag),
            ("The tagset has no base locale file: add the tagset's base locale file to the SLDR, or move the locale's region to a tagset that has one:", nobase),
            ("Unparsable file names: rename the SLDR file:", unparsed)])
        if msg:
            self.fail(msg)


class Data(unittest.TestCase):
    ''' Consistency checks on langtags.json '''

    def test_one_phonetic_base(self):
        ''' each language and dialect has at most one tagset without nophonvars,
            which is the base for its phonetic variants '''
        groups = {}
        with open(langtagjson, encoding="utf-8") as inf:
            for t in json.load(inf):
                if t["tag"].startswith("_") or t.get("nophonvars", False):
                    continue
                f = langtag(t.get("full", t["tag"]))
                k = (f.lang, tuple(f.vars or ()), tuple((f.ns or {}).get("x", ())))
                groups.setdefault(k, []).append(t.get("full", t["tag"]))
        bad = [" / ".join(v) for k, v in sorted(groups.items()) if len(v) > 1]
        msg = report("Languages with more than one tagset without \"nophonvars\" in source/langtags.json.", [
            ("Set \"nophonvars\": true on all but the one tagset that phonetic variants (fonipa etc.) should be based on (each group is separated by a comma):", bad)])
        if msg:
            self.fail(msg)


    def test_rolv_codes(self):
        ''' rod is one ROLV code, of five digits, listed in the rolv of a tagset of
            the same language (the dialect's parent); rolv codes are five digits '''
        badrod, orphan, badrolv = [], [], []
        parents = {}
        with open(langtagjson, encoding="utf-8") as inf:
            data = [t for t in json.load(inf) if not t["tag"].startswith("_")]
        for t in data:
            for c in t.get("rolv", []):
                parents.setdefault(c, set()).add(langtag(t["full"]).lang)
                if not (c.isdigit() and len(c) == 5):
                    badrolv.append("{} ({})".format(t["full"], c))
        for t in data:
            if "rod" not in t:
                continue
            c = t["rod"]
            if not (c.isdigit() and len(c) == 5):
                badrod.append("{} ({})".format(t["full"], c))
            elif langtag(t["full"]).lang not in parents.get(c, ()):
                orphan.append("{} ({})".format(t["full"], c))
        msg = report("ROLV codes in source/langtags.json.", [
            ("\"rod\" must be a single five digit code (zero padded): fix these tagsets:", badrod),
            ("\"rolv\" codes must be five digits (zero padded): fix these tagsets:", badrolv),
            ("These tagsets' \"rod\" is not in the \"rolv\" of any tagset of the same language: add it to the parent's \"rolv\" (or correct the \"rod\"):", orphan)])
        if msg:
            self.fail(msg)


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


