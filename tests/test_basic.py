#!/usr/bin/python3

import os, re
import csv, unittest, json
from langtag import langtag
from sldr.iana import Iana
import pytest

langtagjson = os.path.join(os.path.dirname(__file__), '..', 'source', 'langtags.json')
bannedchars = list(range(33, 45)) + [47] + list(range(58, 63)) + [94, 96]
def nonascii(s):
    cs = [ord(x) for x in s]
    if any(not (32 <= x < 123) or x in bannedchars for x in cs):
        return True

class Basic(unittest.TestCase):

    extraScripts = ["Berf", "Hntl", "Seal"]
    extraLangs = ("000", "oak", "vsn") 

    def setUp(self):
        with open(langtagjson, encoding="utf-8") as inf:
            self.json = json.load(inf)
        self.iana = Iana()

    def _region_test(self, x):
        if x in self.iana.region:
            return True
        elif x in ("XX", "XK"):
            return True
        return False

    def _allRows(self):
        for r in self.json:
            if 'full' not in r:
                continue
            t = langtag(r['full'])
            if t.lang.startswith("x-"):
                continue
            yield (r, t)

    def test_lang(self):
        ''' Tests that all lang subtags are in iana '''
        fails = []
        for r, t in self._allRows():
            lid = r['full'][:r['full'].index("-")]
            if 'tag' not in r:
                continue
            l = langtag(r['tag'])
            if l.lang != t.lang and "-" not in l.lang and "-" not in t.lang:
                self.fail("{2} has different lang to {full} ({0} != {1})".format(l.lang, t.lang, l, **r))
            if t.lang not in self.iana.language and "-" not in t.lang and t.lang not in self.extraLangs:
                fails.append(l)
            if not l.test(fname=langtagjson) and t.lang not in self.extraLangs:
                self.fail("{0} failed conformance check".format(l))
        if len(fails):
            self.fail(f"{fails} langs not in IANA")


    def test_region(self):
        ''' Test that region values are sensible and that they equal the default region.
            Unknown regions do not have to be specified. '''
        for r, t in self._allRows():
            reg = t.region
            if not self._region_test(t.region):
                self.fail("{full} has irregular region".format(**r))
            if 'regions' not in r:
                continue
            l = r['full'][:r['full'].index("-")]
            for s in r['regions']:
                if not self._region_test(s.strip()):
                    self.fail("{1} has irregular region: {0} in regions".format(s, l))

    def test_script(self):
        ''' Qaa? type scripts must have an -x- for the script name '''
        for r, t in self._allRows():
            l = r['full'][:r['full'].index("-")]
            scr = t.script
            if scr is not None and (scr.startswith("Qaa") or scr.startswith("Qab")):
                if scr not in ("Qaax", "Qaby", "Qabz") and (t.extensions is None or 'x' not in t.extensions):
                    self.fail("{} has no extension for script name".format(l))
            elif scr not in self.iana.script and scr not in self.extraScripts:
                self.fail("{1} has irregular script {0}".format(scr, l))
            elif t.script not in self.iana.script and t.script not in self.extraScripts:
                self.fail("{full} has irregular script".format(**r))

    @pytest.mark.skip
    def test_variants(self):
        ''' Test that all variants are in IANA '''
        for r, t in self._allRows():
            l = r['full'][:r['full'].index("-")]
            if t.vars is None and l.vars is None:
                continue
            if sorted(t.vars) != sorted(l.vars):
                self.fail("{0} and {full} have different variants".format(l, **r))
            for v in t.vars:
                if v not in self.iana.variant:
                    self.fail("{full} has bad variant {0}".format(v, **r))

    @pytest.mark.skip
    def test_csv_columns(self):
        ''' Test that everyone has the right number of columns '''
        lc = self.fieldnames[-1]
        for r in self._allRows():
            l = r['full'][:r['full'].index("-")]
            if len(r.get("_", [])):
                self.fail("{} has too many columns".format(l))
            elif r[lc] is None:
                self.fail("{} has too few columns".format(l))

    @pytest.mark.skip
    def test_pua(self):
        ''' Test that anything with -x- in Lang_Id has it in likely_subtag too '''
        for r, t in self._allRows():
            l = r['full'][:r['full'].index("-")]
            if t.ns is None and l.ns is None:
                continue
            if len(t.ns) == 1 and 'x' in t.ns and len(t.ns['x']) == 1:
                continue        # allow a private script extension
            if sorted(t.ns.keys()) != sorted(l.ns.keys()):
                self.fail("{} and {full} have different extension namespaces".format(l, **r))
            for k, v in t.ns.items():
                if sorted(v) != sorted(l.ns[k]):
                    self.fail("{1} and {full} have different extensions in the {0} namespace".format(k, l, **r))

    @pytest.mark.skip
    def test_iso639(self):
        ''' Test that the iso639 column is either empty or 3 lower ascii chars. '''
        k = 'ISO 639-3'
        for r, t in self._allRows():
            if r[k] == '':
                continue
            if len(r[k]) != 3 or r[k].lower() != r[k] or any(not (96 < ord(x) < 123) for x in r[k]):
                self.fail("{Lang_Id} has faulty ISO639 code of {ISO 639-3}".format(**r))

    @pytest.mark.skip
    def test_deprecated(self):
        for r, t in self._allRows():
            l = langtag(r['Lang_Id'])
            inf = self.iana.language.get(l.lang, {})
            if 'Deprecated' in inf:
                if r['deprecated'] == '':
                    self.fail("{Lang_Id} was deprecated: {} in IANA but not in the database".format(inf['Deprecated'], **r))

if __name__ == "__main__":
    unittest.main()
