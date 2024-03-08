#!/usr/bin/python

import unittest, os, re
from xml.etree import ElementTree as et
from langtag import lookup, langtag, LangTags
import sldr       # just to get the path

def isnotint(s):
    try:
        x = int(s)
        return False
    except ValueError:
        return True

langtagjson = os.path.join(os.path.dirname(__file__), '..', 'pub', 'langtags.json')
langtagtxt = os.path.join(os.path.dirname(__file__), '..', 'pub', 'langtags.txt')
likelysubtags = os.path.join(os.path.dirname(sldr.__file__), 'likelySubtags.xml')

exceptions = ['ji-Hebr-UA', 'kxc-Ethi', 'bji-Ethi', 'drh-Mong-CN']

class LikelySubtags(unittest.TestCase):
    ''' Tests alltags.txt for discrepencies against likelySubtags.xml '''
    def setUp(self):
        self.likelymap = {}
        thisdir = os.path.dirname(__file__)
        self.ltags = LangTags(langtagjson)
        doc = et.parse(likelysubtags)
        for e in doc.findall("./likelySubtags/likelySubtag"):
            if e.get('origin', '') == 'sil1':
                continue
            tolt = langtag(e.get('to').replace("_", "-").replace("-ZZ", "").replace("-Zyyy", ""))
            self.likelymap[e.get('from').replace("_", "-")] = tolt
        self.ltags.matchRegions = True

    def test_noBadMappings(self):
        fails = []
        failequalities = []
        error = ""
        for k, v in self.likelymap.items():
            t = langtag(k)
            r = str(v)
            if r in exceptions:
                continue
            if t.lang=="und" or t.region=="ZZ" or t.script=="Zyyy":
                continue
            if k in self.ltags:
                if r not in self.ltags:
                    fails.append(r)
                elif str(self.ltags[k]) != str(self.ltags[r]):
                    failequalities.append((k, self.ltags[k], self.ltags[r]))
        if len(fails):
            error += ", ".join(fails) + " are missing from langtags\n"
        if len(failequalities):
            error += ", ".join("{}[{}] != {}".format(*x) for x in failequalities)
        if len(error):
            self.fail(error)

    def test_noBadComponents(self):
        for v in self.ltags.values():
            if v.lang is None:
                self.fail(repr(v) + " has no language")
            if len(v.lang) > 3 and "-" not in v.lang:
                self.fail(repr(v) + " has odd lang length")
            if v.region is not None and len(v.region) > 2 and isnotint(v.region):
                self.fail(repr(v) + " has bad region")

    def test_zh_CN(self):
        lt = self.ltags['zh']
        self.assertEqual(str(lt.tag), 'zh-CN')

    def test_noDuplicates(self):
        found = {}
        with open(langtagtxt) as inf:
            for i, l in enumerate(inf.readlines()):
                for t in (x.replace("*", "") for x in re.split(r'\s*=\s*', l.strip())):
                    if t in found and found[t] != i + 1:
                        self.fail("Duplicate of {} found at lines {} and {}".format(t, found[t], i+1))
                    found[t] = i + 1
            

if __name__ == '__main__':
    unittest.main()
