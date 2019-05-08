#!/usr/bin/python

import unittest, os, re, json
from xml.etree import ElementTree as et
from palaso.langtags import LangTags, LangTag
from itertools import product

langtagjson = os.path.join(os.path.dirname(__file__), '..', 'results', 'langtags.json')

exceptions = set(["aii-Cyrl"])

class Supplemental(unittest.TestCase):
    ''' Tests alltags.txt for discrepencies against likelySubtags.xml '''
    def setUp(self):
        with open(langtagjson, "r") as inf:
            self.data = json.load(inf)
        self.ltags = {}
        for j in self.data:
            if j['tag'].startswith("_"):
                continue
            self.ltags[j['tag']] = j
            self.ltags[j['full']] = j
            if 'tags' in j:
                for t in j['tags']:
                    self.ltags[t] = j
        thisdir = os.path.dirname(__file__)
        self.doc = et.parse(os.path.join(thisdir, "supplementalData.xml"))

    def test_languageData(self):
        failures = []
        for e in self.doc.findall('./languageData/language'):
            lang = e.get('type')
            if lang == "und":
                continue
            scripts = e.get('scripts', '').split(' ')
            regions = e.get('territories', '').split(' ')
            for s in scripts:
                tag = lang + ("-" + s if len(s) else "")
                if tag not in self.ltags:
                    failures.append(tag)
                    continue
                for r in regions:
                    if not len(r):
                        continue
                    t = tag + "-" + r
                    if t in self.ltags:
                        continue
                    if r not in self.ltags[tag].get('regions', []):
                        failures.append(t)
        if len(failures):
            self.fail("Missing tags from supplemental Data" + str(failures))

