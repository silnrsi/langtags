#!/usr/bin/python

import os, re
import csv, unittest

class Basic(unittest.TestCase):
    def setUp(self):
        self.fname = os.path.join(os.path.dirname(__file__), '../source/langtags.csv')
        with open(self.fname) as csvfile:
            reader = csv.DictReader(csvfile)
            self.rows = list(reader)

    def test_region(self):
        for r in self.rows:
            reg = r['default region']
            if len(reg) < 2 or len(reg) > 3:
                self.fail("{Lang_Id} has bad region: {default region}".format(**r))
