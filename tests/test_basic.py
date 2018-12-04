#!/usr/bin/python

import os, re
import csv, unittest
import palaso.langtags as lt

class Basic(unittest.TestCase):
    def setUp(self):
        self.fname = os.path.join(os.path.dirname(__file__), '../source/langtags.csv')
        with open(self.fname) as csvfile:
            reader = csv.DictReader(csvfile)
            self.rows = list(reader)

    def test_region(self):
        for r in self.rows:
            reg = r['default region']
            t = lt.LangTag(r['likely_subtag'])
            if t.lang.startswith("x-"):
                continue
            if len(reg) < 2 or len(reg) > 3:
                self.fail("{Lang_Id} has bad region: {default region}".format(**r))
            if t.region is not None or reg != '001':
                self.assertEqual(reg, t.region, msg="{likely_subtag} region is not {default region}".format(**r))

    def test_script(self):
        for r in self.rows:
            scr = r['script']
            t = lt.LangTag(r['likely_subtag'])
            if t.lang.startswith("x-"):
                continue
            if len(scr) != 4:
                self.fail("{Lang_Id} has bad script: {script}".format(**r))
            self.assertEqual(scr, t.script, msg="{likely_subtag} script is not {script}".format(**r))

if __name__ == "__main__":
    unittest.main()
