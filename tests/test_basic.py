#!/usr/bin/python

import os, re
import csv, unittest
import palaso.langtags as lt
from palaso.sldr.iana import Iana

class Basic(unittest.TestCase):

    extraScripts = []
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
            t = lt.LangTag(r['likely_subtag'])
            if t.lang.startswith("x-"):
                continue
            yield (r, t)

    def test_lang(self):
        ''' Tests that all lang subtags are in iana '''
        for r, t in self._allRows():
            l = lt.LangTag(r['Lang_Id'])
            if l.lang != t.lang and "-" not in l.lang and "-" not in t.lang:
                self.fail("{Lang_Id} has different lang to {likely_subtag} ({0} != {1})".format(l.lang, t.lang, **r))
            if t.lang not in self.iana.language and "-" not in t.lang and t.lang not in self.extraLangs:
                self.fail("{Lang_Id} lang not in IANA".format(**r))

    def test_region(self):
        ''' Test that region values are sensible and that they equal the default region.
            Unknown regions do not have to be specified. '''
        for r,t in self._allRows():
            reg = r['default region']
            if len(reg) < 2 or len(reg) > 3:
                self.fail("{Lang_Id} has bad default region: {default region}".format(**r))
            if t.region is not None or (reg != '001' and reg != 'XX'):
                self.assertEqual(reg, t.region, msg="{likely_subtag} region is not {default region}".format(**r))
            if not self._region_test(reg):
                self.fail("{Lang_Id} has irregular default region: {default region}".format(**r))
            if not self._region_test(t.region):
                self.fail("{likely_subtag} has irregular region".format(**r))
            for s in r['regions'].split():
                if not self._region_test(s.strip()):
                    self.fail("{Lang_Id} has irregular region: {0} in regions".format(s, **r))

    def test_script(self):
        ''' Qaa? type scripts must have an -x- for the script name '''
        for r, t in self._allRows():
            scr = r['script']
            if scr.startswith("Qaa") or scr.startswith("Qab"):
                if scr not in ("Qaax", "Qaby", "Qabz") and (t.extensions is None or 'x' not in t.extensions):
                    self.fail("{Lang_Id} has no extension for script name".format(**r))
            elif scr not in self.iana.script and scr not in self.extraScripts:
                self.fail("{Lang_Id} has irregular script {script}".format(**r))
            elif t.script not in self.iana.script and t.script not in self.extraScripts:
                self.fail("{likely_subtag} has irregular script".format(**r))
            self.assertEqual(scr, t.script, msg="{likely_subtag} script is not {script}".format(**r))

    def test_variants(self):
        ''' Test that all variants are in IANA '''
        for r, t in self._allRows():
            l = lt.LangTag(r['Lang_Id'])
            if t.variants is None and l.variants is None:
                continue
            if sorted(t.variants) != sorted(l.variants):
                self.fail("{Lang_Id} and {likely_subtag} have different variants".format(**r))
            for v in t.variants:
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
            l = lt.LangTag(r['Lang_Id'])
            if t.extensions is None and l.extensions is None:
                continue
            if len(t.extensions) == 1 and 'x' in t.extensions and len(t.extensions['x']) == 1:
                continue        # allow a private script extension
            if sorted(t.extensions.keys()) != sorted(l.extensions.keys()):
                self.fail("{Lang_Id} and {likely_subtag} have different extension namespaces".format(**r))
            for k, v in t.extensions.items():
                if sorted(v) != sorted(l.extensions[k]):
                    self.fail("{Lang_Id} and {likely_subtag} have different extensions in the {0} namespace".format(k, **r))

if __name__ == "__main__":
    unittest.main()
