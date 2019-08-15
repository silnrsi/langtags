#!/usr/bin/python
'''Langtags processing module

SYNOPSIS:

from palaso.langtag import LangTags, langtag
lts = LangTags()
l = LangTags['en-Latn']
otherl = langtag('en-Latn')
'''

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of the University nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

import json, os
from six import with_metaclass
from collections import namedtuple
try:
    from cachingurl import CachedFile
except ModuleNotFoundError:
    from .cachingurl import CachedFile

class _Singleton(type):
    '''Manage singletons by fname parameter'''
    _instances = {}
    def __call__(cls, *args, **kwargs):
        fname = kwargs.get('fname', None)
        if fname not in cls._instances:
            cls._instances[fname] = super(_Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[fname]

class LangTag(namedtuple('LangTag', ['lang', 'script', 'region', 'variants', 'ns'])):
    def __str__(self):
        '''Returns a parsable (by langtag) representation of the language tag.'''
        res = [self.lang or ""]
        if self.script:
            res.append(self.script)
        if self.region:
            res.append(self.region)
        if self.variants:
            res.extend(self.variants)
        if self.ns:
            for k in sorted(self.ns.keys()):
                res.extend([k] + self.ns[k])
        return "-".join(res)

    def __hash__(self):
        return hash(str(self))

    def matched(self, l):
        '''Is this langtag matched by l in that l may be less specified than this?'''
        for i in range(len(self)):
            if l[i] is None:
                continue
            if self[i] != l[i]:
                return False
        return True


def langtag(s):
    '''Parses string to make a LangTag named tuple with properties: lang, script,
       region, variants, ns. Extlangs result in ext-lang in lang property.'''
    params = {}
    bits = str(s).replace('_', '-').split('-')
    curr = 0

    # lang component
    lang = None
    if 1 < len(bits[curr]) < 4 :
        lang = bits[curr].lower()
        curr += 1
    elif bits[curr] == "x" and curr < len(bits) - 1:
        # private use, try to parse as extlang
        lang = "x-"
        curr += 1
        while curr < len(bits) and 1 < len(bits[curr]) < 4:
            lang += bits[curr] + "-"
            curr += 1
        lang = lang[:-1]
    if curr >= len(bits) : return LangTag(lang, None, None, None, None)

    # script component
    script = None
    if len(bits[curr]) == 4 :
        script = bits[curr].title()
        curr += 1
    if curr >= len(bits) : return LangTag(lang, script, None, None, None)

    # region component
    region = None
    if 1 < len(bits[curr]) < 4 :
        region = bits[curr].upper()
        curr += 1
    if curr >= len(bits): return LangTag(lang, script, region, None, None)

    # extlang spotting
    if len(bits[curr]) == 4 and script is None:
        lang += "-"+region
        script = bits[curr]
        region = None
        curr += 1
        if curr >= len(bits): return LangTag(lang, script, region, None, None)
        if 1 < len(bits[curr]) < 4:
            region = bits[curr]
            curr += 1

    # variants and extensions
    ns = ''
    extensions = {}
    variants = []
    while curr < len(bits) :
        if len(bits[curr]) == 1 :
            ns = bits[curr].lower()
            extensions[ns] = []
        elif ns == '' :
            variants.append(bits[curr].lower())
        else :
            extensions[ns].append(bits[curr].lower())
        curr += 1
    return LangTag(lang, script, region, (variants if len(variants) else None),
                    (extensions if len(extensions) else None))


class LangTags(with_metaclass(_Singleton)):
    '''Collection of TagSets'''

    matchRegions = False

    def __init__(self, fname=None, useurl=None, cachedprefix=""):
        '''fname is an optional langtags.json file'''
        self._tags = {}
        self._info = {}
        if fname is None:
            for srcdir in [os.path.join(os.path.dirname(__file__)),
                            os.path.join(os.path.dirname(__file__), '..', '..', 'pub')]:
                if os.path.exists(os.path.join(srcdir, 'langtags.json')):
                    break
            else:
                raise IOError("Cannot find langtags.json")
            self._cachedltags = CachedFile('langtags.json', url=useurl, 
                    srcdir = srcdir, prefix=cachedprefix or "langtag-LangTags")
            fname = self._cachedltags.get_latest()
        with open(fname, "r") as inf:
            data = json.load(inf, object_hook=self.addSet)
            for d in data:
                if not hasattr(d, 'tag'):
                    continue

    def addSet(self, d):
        '''Adds a TagSet to this collection'''
        t = d.get('tag', '')
        if t.startswith("_"):
            self._info[t[1:]] = d
        elif t != "":
            s = TagSet(**d)
            for l in s.allTags():
                self._tags[str(l)] = s

    def values(self):
        '''Return a list of all the tagsets in this LangTags'''
        return self._tags.values()

    def _getwithvars(self, l, vs):
        '''Given a langtag and list of variants, create a new tagset corresponding
            to the variant list if not already covered by this tagset'''
        t = [v for v in l.variants if v not in vs]
        if len(t) != len(vs):
            lv = l._replace(variants=t)
            res = self._tags.get(str(lv), None)
            if res is not None:
                tsv = res._make_variant([v for v in l.variants if v in vs])
                for l in tsv.allTags():
                    self._tags[l] = tsv
                return tsv
        return None

    def __getitem__(self, s):
        '''Looks up a langtag string returning a TagSet or raising KeyError. As in
            aLangTags[s]. Handle .variants and if self.matchResults, .regions.'''
        if s in self._tags:
            return self._tags[s]
        l = langtag(s)
        if l.variants is not None:
            gvar = self._info.get('globalvar', {}).get('variants', [])
            res = self._getwithvars(l, gvar)
            if res is not None:
                return res
            if l.script is None or l.script == "Latn":
                pvar = self._info.get('phonvar', {}).get('variants', [])
                res = self._getwithvars(l, pvar)
                if res is not None:
                    return res
                if pvar and gvar:
                    res = self._getwithvars(l, pvar + gvar)
                    if res is not None:
                        return res
        if self.matchRegions and l.region is not None:
            lr = l._replace(region = None)
            res = self[str(lr)]
            if res is not None:
                if l.region in res.regions:
                    return res
        raise KeyError(s)

class TagSet:
    '''Represents tag set from the json file with same attributes as fields
       .tag = shortest/preferred tag, .full = maximal tag.'''

    def __init__(self, **kw):
        '''Create a TagSet and fill in its data properties'''
        self.tags = []
        self.regions = []
        self._allkeys = kw.keys()
        for k, v in kw.items():
            setattr(self, k, v)
        for k in ('tag', 'full'):
            v = getattr(self, k, "")
            l = langtag(v)
            setattr(self, k, l)
        self.tags = [langtag(s) for s in self.tags]

    def __str__(self):
        '''Returns tag as a str'''
        return str(self.tag or self.full)

    def __hash__(self):
        return hash(self.tag) + hash(self.full)

    def __cmp__(self, other):
        return cmp(str(self), str(other))

    def asdict(self, format=None, **kw):
        '''Returns all data properties as a dict. Set format to process each element.
            Other kw values are used to initialise the dictionary with default values
            for missing properties.'''
        for k in self._allkeys:
            v = getattr(self, k)
            if format is not None:
                if isinstance(v, list):
                    v = list(map(format, v))
                else:
                    v = format(v)
            kw[k] = v
        return kw

    def _isin(self, l):
        '''Is the given langtag specified as one of the tags in this set'''
        s = str(l)
        return s == str(self.tag) or s == str(self.full) or s in map(str, self.tags)

    def contains(self, l):
        '''Is LangTag l one that this tagset contains? This includes the extra
            regions supported.'''
        if self._isin(l):
            return True
        if l.region and l.region in self.regions:
            nr = l._replace(region=None)
            if self._isin(nr):
                return True
        return False

    def matched(self, l):
        '''Returns whether this tagset is matched by l, given l may be less
            specified than this tagset.'''
        if self.full.matched(l):
            return True
        for s in getattr(self, 'tags', []):
            t = langtag(s)
            if t.matched(l):
                return True
        return False

    def match639(self, l):
        '''Test this langtag against the iso639_3 field for language'''
        if l.lang == getattr(self, 'iso639_3', ""):
            t = l._replace(lang=self.tag.lang)
            return self.matched(t)

    def allTags(self):
        '''Returns a list of all the LangTags in this set. Not necessarily every
            tag that matches. But all the tags excluding those with regions in
            the .regions list of extra regions matched by this TagSet.'''
        res = [self.tag, self.full]
        res.extend(self.tags)
        return res

    def _make_variant(self, vs):
        '''Return a copy tagset changing all tags to add the variants vs.'''
        d = dict([(k, getattr(self, k, None)) for k in self._allkeys])
        for k in ('tag', 'full'):
            if k in d:
                l = d[k]._replace(variants=sorted((d[k].variants or []) + vs))
                d[k] = l
        d['tags'] = [t._replace(variants=sorted((t.variants or []) + vs)) for t in d['tags']]
        return TagSet(**d)


if __name__ == "__main__":
    lts = LangTags()
    for t in ('en-Latn-fonipa-simple', 'aal-NG'):
        lts.matchRegions = False
        try:
            print("Simply, {} = {}".format(t, lts[t]))
        except KeyError:
            lts.matchRegions = True
            print("With regions, {} = {}".format(t, lts[t]))
