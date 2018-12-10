#!/usr/bin/python

import os, re
import csv, unittest
import palaso.langtags as lt
from palaso.sldr.iana import Iana

class Basic(unittest.TestCase):
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
        elif x in ("XX",):
            return True
        return False

    def _allRows(self):
        for r in self.rows:
            t = lt.LangTag(r['likely_subtag'])
            if t.lang.startswith("x-"):
                continue
            yield (r, t)

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
        ''' Test script tag is appropriate and the same as the script column '''
        for r,t in self._allRows():
            scr = r['script']
            if len(scr) != 4:
                self.fail("{Lang_Id} has bad script: {script}".format(**r))
            self.assertEqual(scr, t.script, msg="{likely_subtag} script is not {script}".format(**r))

    def test_unknown_script(self):
        ''' Qaa? type scripts must have an -x- for the script name '''
        for r, t in self._allRows():
            scr = r['script']
            if scr.startswith("Qaa") and scr != "Qaax":
                if t is None or 'x' not in t.extensions:
                    self.fail("{Lang_Id} has no extension for script name".format(**r))

    def test_csv_columns(self):
        ''' Test that everyone has the right number of columns '''
        lc = self.fieldnames[-1]
        for r in self.rows:
            if len(r.get("_", [])):
                self.fail("{Lang_Id} has too many columns".format(**r))
            elif r[lc] is None:
                self.fail("{Lang_Id} has too few columns".format(**r))

if __name__ == "__main__":
    unittest.main()
