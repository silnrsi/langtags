#!/usr/bin/env python3
'''Langtags processing module

SYNOPSIS:

from langtag import lookup, langtag
t = lookup('en-Latn')
l = langtag('en-Latn')
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

import json, os, re
from collections import namedtuple

try:
    from cachingurl import CachedFile
except ModuleNotFoundError:
    from .cachingurl import CachedFile

try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError

# 10 means infinity
variantorders = {"1994": 3, "alalc97": 10, "biske": 2, "fonipa": 10, "fonkirsh": 10,
    "fonnapa": 10, "fonupa": 10, "fonxsamp": 10, "grclass": 2, "grital": 2,
    "grmistr": 2, "heploc": 2, "lipaw": 2, "njiva": 2, "osojs": 2, "simple": 10,
    "solba": 2}

class _Singleton(type):
    '''Manage singletons by fname parameter'''
    _instances = {}

    def __call__(cls, *args, **kwargs):
        key = tuple(str(kwargs[k]) if kwargs.get(k, None) is not None else None
                        for k in ('fname', 'useurl', 'cachedprefix'))
        if key not in cls._instances:
            cls._instances[key] = super(_Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[key]

class LangTag(namedtuple('LangTag', ['lang', 'script', 'region', 'vars', 'ns'])):
    def __str__(self):
        '''Returns a parsable (by langtag) representation of the language tag.'''
        res = [self.lang.lower()] if self.lang else []
        if self.script:
            res.append(self.script.title())
        if self.region:
            res.append(self.region.upper())
        if self.vars:
            res.extend([x.lower() for x in self.vars])
        if self.ns:
            for k in sorted(self.ns.keys(), key=lambda x: (x == "x", x)):   # x- is always last
                res.extend([k.lower()] + self.ns[k])
        return "-".join(res)

    def __hash__(self):
        return hash(str(self))

    def matched(self, l):
        '''Is this langtag matched by l in that l may be less specified than this?
            Variants in l must be a subset of ours (in any order). Each extension
            in l must be in ours with the same subtags.'''
        for a in ('lang', 'script', 'region'):
            v = getattr(l, a)
            if v is not None and v != getattr(self, a):
                return False
        if l.vars and not set(l.vars) <= set(self.vars or []):
            return False
        if l.ns and any((self.ns or {}).get(k, None) != v for k, v in l.ns.items()):
            return False
        return True

    def test(self, fname=None, **kw):
        ''' Test for conformance (not existence in the database) of this language tag '''
        lts = LangTags(fname=fname, **kw)
        return lts.test(self)

    def copy(self, **kw):
        ''' Creates a new LangTag with the changed attributes given '''
        parms = [kw.get(a, getattr(self, a, None)) for a in self._fields]
        return self.__class__(*parms)


def langtag(s):
    '''Parses string to make a LangTag named tuple with properties: lang, script,
       region, vars, ns. Extlangs result in the ext-lang being stored in the
       lang property. This may raise a SyntaxError'''
    bits = str(s).replace('_', '-').lower().split('-')
    if any(not re.fullmatch(r"[a-z0-9]{1,8}", b) for b in bits):
        raise SyntaxError(f"Malformed language tag {s}")
    curr = 0

    # lang component. A missing lang is allowed (e.g. a bare script or region)
    lang = None
    if re.fullmatch(r"[a-z]{2,3}|[a-z]{5,8}", bits[0]):
        lang = bits[0]
        curr += 1
        # up to 3 extlangs, only after a 2-3 letter language
        if len(lang) < 4:
            i = 0
            while i < 3 and curr < len(bits) and re.fullmatch(r"[a-z]{3}", bits[curr]):
                lang += "-" + bits[curr]
                curr += 1
                i += 1
    elif bits[0] == "i" and len(bits) > 1:       # grandfathered i- tags
        lang = bits[0]
        curr += 1

    # script component
    script = None
    if curr < len(bits) and re.fullmatch(r"[a-z]{4}", bits[curr]):
        script = bits[curr].title()
        curr += 1

    # region component
    region = None
    if curr < len(bits) and re.fullmatch(r"[a-z]{2}|\d{3}", bits[curr]):
        region = bits[curr].upper()
        curr += 1

    # variants
    variants = []
    while curr < len(bits) and len(bits[curr]) > 1:
        if not re.fullmatch(r"[a-z0-9]{5,8}|\d[a-z0-9]{3}", bits[curr]):
            raise SyntaxError(f"Malformed subtag [{bits[curr]}] in {s}")
        variants.append(bits[curr])
        curr += 1

    # extensions and private use. Everything after x- is private use.
    extensions = {}
    while curr < len(bits):
        ns = bits[curr]
        if ns in extensions:
            raise SyntaxError(f"Repeated extension [{ns}] in {s}")
        curr += 1
        start = curr
        if ns == "x":
            curr = len(bits)
        else:
            while curr < len(bits) and len(bits[curr]) > 1:
                curr += 1
        if curr == start:
            raise SyntaxError(f"Empty extension [{ns}] in {s}")
        extensions[ns] = bits[start:curr]

    if lang is None and script is None and region is None and not variants and 'x' not in extensions:
        raise SyntaxError(f"Malformed language tag {s}")
    return LangTag(lang, script, region, (variants if len(variants) else None),
                    (extensions if len(extensions) else None))


class LangTags(metaclass=_Singleton):
    ''' Collection of TagSets searchable from a language tag string.

        Attributes:
            matchRegions: if True, matches a tag against all the regions
                          in the tagset. Otherwise only match against the
                          explicit tags in the tagset.'''

    matchRegions = False

    def __init__(self, fname=None, useurl=None, cachedprefix=None, **kw):
        '''fname is an optional langtags.json file'''
        self._tags = {}
        self._iso639s = {}
        self._info = {}
        self._regions = {}      # collect region names from json
        self._allscripts = set()
        self._allregions = set()
        self._allvariants = set()
        self._extralangs = set()
        self._varcache = {}     # (tag, use639, matchRegions) -> derived tagset or None
        inf = None

        if fname is None:
            envpath = os.getenv("LANGTAGSPATH", None)
            if envpath is not None:
                fname = envpath
        if fname is not None:
            inf = open(fname)
        else:
            from importlib import resources

            def open_through_cache(srcpath=None):
                cachedltags = CachedFile('langtags.json',
                        url=useurl, 
                        srcpath=srcpath, 
                        prefix=cachedprefix or "langtag-LangTags",
                        stale_period=604800)    # One week
                return cachedltags.open(encoding="utf-8")

            if useurl is None:
                useurl = "https://ldml.api.sil.org/langtags.json"
            try:
                with resources.as_file(resources.files("langtag") / 'langtags.json') as srcpath:
                    inf = open_through_cache(srcpath)
            except FileNotFoundError:
                inf = open_through_cache()
        if inf is not None:
            for d in json.load(inf):
                self.addSet(d)
            inf.close()
            # languages used in tags that have no tagset of their own
            self._extralangs = set(l.lang for ts in self._tags.values()
                                    for l in ts.allTags(use639=False)) - set(self._tags.keys())
        else:
            raise IOError("Unable to load {}".format(fname))
        if 'conformance' in self._info:
            self._allregions.update(self._info['conformance'].get('regions', []))
            self._allscripts.update(self._info['conformance'].get('scripts', []))

    def addSet(self, d):
        '''Adds a TagSet to this collection'''
        t = d.get('tag', '')
        self._allvariants.update(d.get('variants', []))
        if t.startswith("_"):
            self._info[t[1:]] = d
        elif t != "":
            s = TagSet(**d)
            for l in s.allTags(use639=False):
                self._tags[str(l).lower()] = s
                if l.vars:
                    self._allvariants.update(l.vars)
            if 'iso639_3' in d and d['iso639_3'] != s.lang:
                for l in s.allTags():
                    ll = l._replace(lang=d['iso639_3'])
                    self._iso639s[str(ll).lower()] = s
        r = d.get('region', '')
        self._allregions.add(r)
        self._allregions.update(d.get('regions', []))
        self._allscripts.add(d.get('script', ''))
        rn = d.get('regionname', '')
        if r != '' and rn != '':
            self._regions[r] = rn

    def test(self, lt):
        '''Conformance testing for a language tag'''
        if lt.lang not in self._tags and lt.lang not in self._extralangs:
            return False
        if lt.script is not None and lt.script not in self._allscripts:
            return False
        if lt.region is not None and lt.region not in self._allregions and not re.match(r"\d{3}", lt.region):
            return False
        if lt.vars is not None and any(v not in self._allvariants for v in lt.vars):
            return False
        return True

    def values(self):
        '''Return a list of all the tagsets in this LangTags'''
        return self._tags.values()

    def region(self, reg):
        '''Return the name of a region code'''
        return self._regions.get(reg, "")

    def _getwithvars(self, l, vs, use639=False):
        '''Given a langtag and list of variants, create a new tagset corresponding
            to the variant list if not already covered by this tagset'''
        removed = [v for v in l.vars if v in vs]
        if not removed:
            return None
        lv = l._replace(vars=[v for v in l.vars if v not in vs] or None)
        key = str(lv).lower()
        res = self._tags.get(key, None)
        if res is None and use639:
            res = self._iso639s.get(key, None)
        if res is None:
            return None
        return res._make_variant(removed)

    def get(self, ltname, default=None, use639=False, matchRegions=None, **kw):
        '''Looks up a langtag string returning a TagSet or returns default [None].
            matchRegions overrides the matchRegions attribute for this lookup.'''
        if matchRegions is None:
            matchRegions = self.matchRegions
        s = str(ltname).lower()
        if s in self._tags:
            return self._tags[s]
        if use639 and s in self._iso639s:
            return self._iso639s[s]
        ckey = (s, bool(use639), bool(matchRegions))
        res = self._varcache.get(ckey, None)
        if res is None:
            res = self._derive(s, use639, matchRegions)
            if res is None:
                return default
            self._varcache[ckey] = res      # only cache hits, so junk queries don't grow it
        return res

    def _derive(self, s, use639, matchRegions):
        '''Finds a tagset for a tag not directly in the database, by removing
            variants or regions. Returns None if not found.'''
        try:
            l = langtag(s)
        except SyntaxError:
            return None
        if l.lang is None:
            return None
        if l.vars is not None:
            gvar = self._info.get('globalvar', {}).get('variants', [])
            res = self._getwithvars(l, gvar, use639=use639)
            if res is not None:
                return res
            if l.script is None or l.script == "Latn":
                pvar = self._info.get('phonvar', {}).get('variants', [])
                for a in (pvar, pvar + gvar):
                    if l.script != "Latn":
                        res = self._getwithvars(l._replace(script="Latn"), a, use639=use639)
                        if res is not None:
                            return res
                    res = self._getwithvars(l, a, use639=use639)
                    if res is not None:
                        if l.script != "Latn":
                            return res.newFull(res.full._replace(script="Latn"))
                        else:
                            return res
        if matchRegions and l.region is not None:
            lr = l._replace(region = None)
            res = self.get(str(lr), None, use639=use639, matchRegions=False)
            if res is not None:
                if l.region in res.regions or l.region == res.region:
                    return res
        return None

    def __getitem__(self, s):
        '''Implements aTag[s] using get(). Raises KeyError if the tag is missing.'''
        res = self.get(s)
        if res is None:
            raise KeyError(s)
        return res

    def __contains__(self, s):
        res = self.get(s)
        return res is not None

def lookup(lt, default=None, fname=None, matchRegions=True, **kw):
    ''' Looks up a language tag by name in a language tags database. Returns a
        TagSet() containing the given language tag.
        Parameters:
            default         Default value to return, if None raise KeyError on fail
            fname:          A specific language tags json databse to load
            matchRegions:   If True, lookup will match a language tag with a region
                            to a TagSet if the region is in the list of extra
                            regions in the TagSet. Default True. If False only
                            match against the explicit tags in the tagset.
            use639          If True, also match against iso639-3 codes not in BCP47.'''
    lts = LangTags(fname=fname, **kw)
    res = lts.get(str(lt), default=default, matchRegions=matchRegions, **kw)
    if res is None:
        raise KeyError(lt)
    return res

def tagsets(sort='tag', fname=None, **kw):
    ''' Return a list of all the tagsets in the database.
        Parameters:
            sort    Sorts by the given attribute falling back to fulltag.
                    Can be set to False or None or empty to return unsorted.
            fname   A specific language tags json database to load '''
    lts = LangTags(fname=fname, **kw)
    if sort is None or sort is False or sort == '':
        return list(set(lts._tags.values()))
    return list(sorted(set(lts._tags.values()), key=lambda x: str(getattr(x, sort, getattr(x, 'full', '')))))

class TagSet:
    ''' Represents tag set from the json file with same attributes as fields
        .tag = shortest/preferred tag, .full = maximal tag.
        This class has LangTag behaviour in that a tagset has the attributes
        of a LangTag based on the maximal tag (falling back to .tag).
        The .tag, .full and elements of the .tags list are all converted to
        LangTag objects'''

    def __init__(self, **kw):
        '''Create a TagSet and fill in its data properties'''
        self.tags = []
        self.regions = []
        self._allkeys = []
        for k, v in kw.items():
            if k in ("iso639_3", "region", "script"):
                k = "_" + k
            setattr(self, k, v)
            self._allkeys.append(k)
        self.tag = langtag(getattr(self, 'tag', ""))
        full = getattr(self, 'full', None)
        self.full = langtag(full) if full else self.tag
        self.tags = [langtag(s) for s in self.tags]

    def __str__(self):
        '''Returns tag as a str'''
        return str(self._full())

    def __repr__(self):
        return str(self.__class__.__name__)+"(" + ", ".join('{}="{}"'.format(k, " ".join(str(x) for x in v) if isinstance(v, list) else v) for k, v in self.asdict().items()) + ")"

    def __hash__(self):
        '''Hashes the identifying features of this tagset'''
        return hash(self.tag) + hash(self.full)

    def _full(self):
        return self.full

    @property
    def lang(self):
        '''Returns the language component of the full tag. Falling back to the tag'''
        return self._full().lang

    @property
    def script(self):
        '''Returns the script component of the full tag. Falling back to the tag'''
        return self._full().script

    @property
    def region(self):
        '''Returns the region component of the full tag. Falling back to the tag'''
        return self._full().region

    @property
    def vars(self):
        '''Returns the vars component of the full tag. Falling back to the tag'''
        return self._full().vars

    @property
    def ns(self):
        '''Returns the ns component of the full tag. Falling back to the tag'''
        return self._full().ns

    @property
    def iso639_3(self):
        '''Returns the iso639-3 of the language for the tagset, whether or not
            specified in the json file.'''
        return getattr(self, "_iso639_3", self.lang)

    def asSldr(self):
        ''' Returns what an SLDR filename would be for this langtag. Working around
            Microsoft filename problems.'''
        res = str(self.tag).replace("-", "_")
        if res in ('aux', 'con', 'nul', 'prn'):
            res += "_" + self.full.script.title()
        return res + ".xml"

    def __lt__(self, other):
        return str(self) < str(other)

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
            kw[k[1:] if k.startswith("_") else k] = v
        return kw

    def _isin(self, l):
        '''Is the given langtag specified as one of the tags in this set'''
        s = str(l)
        return s == str(self.tag) or s == str(self.full) or s in map(str, self.tags)

    def __contains__(self, l):
        '''Is LangTag l one that this tagset contains? This includes the extra
            regions supported. As in `l in lt`'''
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
        return any(t.matched(l) for t in self.tags)

    def match639(self, l):
        '''Test this langtag against the iso639_3 field for language'''
        if l.lang == getattr(self, '_iso639_3', ""):
            t = l._replace(lang=self.tag.lang)
            return self.matched(t)
        return False

    def allTags(self, use639=True):
        '''Returns a list of all the LangTags in this set, as LangTag objects.
            Not necessarily every tag that matches is included. But all the
            tags excluding those with regions in the .regions list of extra
            regions matched by this TagSet. This includes ISO639-3 equivalents.'''
        res = [self.tag, self.full]
        res.extend(self.tags)
        if use639:
            i639 = getattr(self, '_iso639_3', self.tag.lang)
            if i639 != self.tag.lang:
                res.extend([l._replace(lang=i639) for l in res])
        return res

    def _make_variant(self, vs):
        '''Return a copy tagset changing all tags to add the variants vs.'''
        def varsort(v):
            return variantorders.get(v, 0)
        d = dict([(k, getattr(self, k, None)) for k in self._allkeys])
        for k in ('tag', 'full'):
            if k in d:
                l = d[k]._replace(vars=sorted((d[k].vars or []) + vs, key=varsort))
                d[k] = l
        d['tags'] = [t._replace(vars=sorted((t.vars or []) + vs, key=varsort)) for t in self.tags]
        return TagSet(**d)

    def newFull(self, newfull):
        '''Returns a new tagset but with a different fulltag'''
        d = dict([(k, getattr(self, k, None)) for k in self._allkeys])
        if self.script is not None and newfull.script is not None:
            d['_script'] = newfull.script
        d['full'] = LangTag(lang = newfull.lang or self.full.lang,
                        script = newfull.script or self.full.script,
                        region = newfull.region or self.full.region,
                        vars = newfull.vars,
                        ns = newfull.ns)
        d['tag'] = LangTag(lang = newfull.lang,
                        script = (newfull.script or self.tag.script) if self.tag.script is not None else None,
                        region = (newfull.region or self.tag.region) if self.tag.region is not None else None,
                        vars = newfull.vars,
                        ns = newfull.ns)
        d['tags'] = [LangTag(lang = t.lang,
                            script = (newfull.script or t.script) if t.script is not None else None,
                            region = (newfull.region or t.region) if t.region is not None else None,
                            vars = newfull.vars,
                            ns = newfull.ns) for t in d['tags']]
        if newfull.script is not None and self.script is not None and newfull.script != self.script:
            if newfull.script == "Latn" and 'latnnames' in d:
                d['localnames'] = d.pop('latnnames')
            elif 'localnames' in d:
                del d['localnames']
            for a in ('names', 'name', 'localname'):
                d.pop(a, None)
        return TagSet(**d)
        

if __name__ == "__main__":
    for t in ('en-Latn-fonipa-simple', 'aal-NG', 'bal-fonipa', 'th-fonipa'):
        try:
            print("Simply, {} = {}".format(t, lookup(t)))
        except KeyError:
            print("With regions, {} = {}".format(t, lookup(t, matchRegions=True)))
