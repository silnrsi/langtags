#!/usr/bin/python

import unittest, os
from xml.etree import ElementTree as et
from palaso.langtags import LangTags, LangTag

def isnotint(s):
    try:
        x = int(s)
        return False
    except ValueError:
        return True

class LikelySubtags(unittest.TestCase):
    ''' Tests alltags.txt for discrepencies against likelySubtags.xml '''
    def setUp(self):
        self.likelymap = {}
        thisdir = os.path.dirname(__file__)
        self.ltags = LangTags(alltags=os.path.join(thisdir, '..', 'alltags.txt'))
        doc = et.parse(os.path.join(thisdir, "likelySubtags.xml"))
        for e in doc.findall("./likelySubtags/likelySubtag"):
            tolt = LangTag(e.get('to').replace("_", "-"))
            if tolt.region == "ZZ":
                tolt.hideregion = True
            if tolt.script == "Zyyy":
                tolt.hidescript = True
            self.likelymap[e.get('from').replace("_", "-")] = tolt

    def test_noBadMappings(self):
        for k, v in self.likelymap.items():
            t = LangTag(k)
            if t.lang=="und" or t.region=="ZZ" or t.script=="Zyyy":
                continue
            if k in self.ltags:
                r = str(v)
                if r not in self.ltags:
                    self.fail(r + " is missing from langtags")
                self.assertIs(self.ltags[k], self.ltags[r])

    def test_noBadComponents(self):
        for v in self.ltags.values():
            if len(v.lang) > 3 and "-" not in v.lang:
                self.fail(repr(v) + " has odd lang length")
            if v.region is not None and len(v.region) > 2 and isnotint(v.region):
                self.fail(repr(v) + " has bad region")
            

if __name__ == '__main__':
    unittest.main()
