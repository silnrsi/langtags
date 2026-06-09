#!/usr/bin/python3
import os
import csv
import unittest
from langtag import langtag
from sldr.iana import Iana

langtagjson = os.path.join(os.path.dirname(__file__), '..', 'pub', 'langtags.json')

class DeveloperOnly(unittest.TestCase):

    extraScripts = ["Berf", "Hntl", "Seal"]
    extraLangs = ("000", "oak", "vsn") 

    def setUp(self):
        self.fname = os.path.join(os.path.dirname(__file__), '../source/langtags.csv')
        with open(self.fname) as csvfile:
            reader = csv.DictReader(csvfile, restkey="_")
            self.rows = list(reader)
            self.fieldnames = reader.fieldnames
            self.numlines = reader.line_num
        self.iana = Iana()

    def _allRows(self):
        for r in self.rows:
            t = langtag(r['likely_subtag'])
            if t.lang.startswith("x-"):
                continue
            yield (r, t)

    def test_lang(self):
        ''' Tests that all lang subtags are in iana '''
        fails = []
        for r, t in self._allRows():
            l = langtag(r['Lang_Id'])
            if l.lang != t.lang and "-" not in l.lang and "-" not in t.lang:
                self.fail("{Lang_Id} has different lang to {likely_subtag} ({0} != {1})".format(l.lang, t.lang, **r))
            if t.lang not in self.iana.language and "-" not in t.lang and t.lang not in self.extraLangs:
                fails.append(r['Lang_Id'])
            if not l.test(fname=langtagjson) and t.lang not in self.extraLangs:
                self.fail("{Lang_Id} failed conformance check".format(**r))
        if len(fails):
            self.fail(f"{fails} langs not in IANA")

if __name__ == "__main__":
    unittest.main()
