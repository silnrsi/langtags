#!/usr/bin/python3

import os, re
import csv, unittest
from langtag import langtag
from sldr.iana import Iana

bannedchars = list(range(33, 45)) + [47] + list(range(58, 63)) + [94, 96]
def nonascii(s):
    cs = [ord(x) for x in s]
    if any(not (32 <= x < 123) or x in bannedchars for x in cs):
        return True

class Basic(unittest.TestCase):

    extraScripts = ["Toto", "Vith"]
    extraLangs = ("000", )

    def setUp(self):
        self.fname = os.path.join(os.path.dirname(__file__), '../source/langtags.csv')
        with open(self.fname) as csvfile:
            reader = csv.DictReader(csvfile, restkey="_")
            self.rows = list(reader)
            self.fieldnames = reader.fieldnames
            self.numlines = reader.line_num
        self.iana = Iana()

    def _region_test(self, x):
        if x in self.iana.region:
            return True
        elif x in ("XX", "XK"):
            return True
        return False

    def _allRows(self):
        for r in self.rows:
            t = langtag(r['likely_subtag'])
            if t.lang.startswith("x-"):
                continue
            yield (r, t)

    def test_lang(self):
        ''' Tests that all lang subtags are in iana '''
        for r, t in self._allRows():
            l = langtag(r['Lang_Id'])
            if l.lang != t.lang and "-" not in l.lang and "-" not in t.lang:
                self.fail("{Lang_Id} has different lang to {likely_subtag} ({0} != {1})".format(l.lang, t.lang, **r))
            if t.lang not in self.iana.language and "-" not in t.lang and t.lang not in self.extraLangs:
                self.fail("{Lang_Id} lang not in IANA".format(**r))

    def test_region(self):
        ''' Test that region values are sensible and that they equal the default region.
            Unknown regions do not have to be specified. '''
        for r,t in self._allRows():
            reg = t.region
            if not self._region_test(t.region):
                self.fail("{likely_subtag} has irregular region".format(**r))
            for s in r['regions'].split():
                if not self._region_test(s.strip()):
                    self.fail("{Lang_Id} has irregular region: {0} in regions".format(s, **r))

    def test_script(self):
        ''' Qaa? type scripts must have an -x- for the script name '''
        for r, t in self._allRows():
            scr = t.script
            if scr.startswith("Qaa") or scr.startswith("Qab"):
                if scr not in ("Qaax", "Qaby", "Qabz") and (t.extensions is None or 'x' not in t.extensions):
                    self.fail("{Lang_Id} has no extension for script name".format(**r))
            elif scr not in self.iana.script and scr not in self.extraScripts:
                self.fail("{Lang_Id} has irregular script {}".format(scr, **r))
            elif t.script not in self.iana.script and t.script not in self.extraScripts:
                self.fail("{likely_subtag} has irregular script".format(**r))

    def test_variants(self):
        ''' Test that all variants are in IANA '''
        for r, t in self._allRows():
            l = langtag(r['Lang_Id'])
            if t.vars is None and l.vars is None:
                continue
            if sorted(t.vars) != sorted(l.vars):
                self.fail("{Lang_Id} and {likely_subtag} have different variants".format(**r))
            for v in t.vars:
                if v not in self.iana.variant:
                    self.fail("{likely_subtag} has bad variant {0}".format(v, **r))

    def test_csv_columns(self):
        ''' Test that everyone has the right number of columns '''
        lc = self.fieldnames[-1]
        for r in self.rows:
            if len(r.get("_", [])):
                self.fail("{Lang_Id} has too many columns".format(**r))
            elif r[lc] is None:
                self.fail("{Lang_Id} has too few columns".format(**r))

    def test_pua(self):
        ''' Test that anything with -x- in Lang_Id has it in likely_subtag too '''
        for r, t in self._allRows():
            l = langtag(r['Lang_Id'])
            if t.ns is None and l.ns is None:
                continue
            if len(t.ns) == 1 and 'x' in t.ns and len(t.ns['x']) == 1:
                continue        # allow a private script extension
            if sorted(t.ns.keys()) != sorted(l.extensions.keys()):
                self.fail("{Lang_Id} and {likely_subtag} have different extension namespaces".format(**r))
            for k, v in t.ns.items():
                if sorted(v) != sorted(l.ns[k]):
                    self.fail("{Lang_Id} and {likely_subtag} have different extensions in the {0} namespace".format(k, **r))

    def test_ascii(self):
        ''' Test that all tags are pure ascii '''
        for r, t in self._allRows():
            for cid in ('Lang_Id', 'likely_subtag', 'regions', 'ISO 639-3', 'Macro', 'variants'):
                if nonascii(r[cid]):
                    self.fail("{Lang_Id} has non ASCII in column {0} value {1}".format(cid, r[cid], **r))

    def test_iso639(self):
        ''' Test that the iso639 column is either empty or 3 lower ascii chars. '''
        k = 'ISO 639-3'
        for r, t in self._allRows():
            if r[k] == '':
                continue
            if len(r[k]) != 3 or r[k].lower() != r[k] or any(not (96 < ord(x) < 123) for x in r[k]):
                self.fail("{Lang_Id} has faulty ISO639 code of {ISO 639-3}".format(**r))

    def test_deprecated(self):
        for r, t in self._allRows():
            l = langtag(r['Lang_Id'])
            inf = self.iana.language.get(l.lang, {})
            if 'Deprecated' in inf:
                if r['deprecated'] == '':
                    self.fail("{Lang_Id} was deprecated: {} in IANA but not in the database".format(inf['Deprecated'], **r))

if __name__ == "__main__":
    unittest.main()
