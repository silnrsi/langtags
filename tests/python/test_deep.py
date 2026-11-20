#!/usr/bin/python3
''' Deep tests of the langtag module as a reference implementation.

    Most tests run over the whole of source/langtags.json and check that lookup
    rules hold for every tagset, not just a few examples. Each failure lists
    every offending tag. The rules tested are those agreed in
    dev/discuss_matching.md and dev/impl_issues.md:

    - every tag in a returned set looks up to that same set
    - a partial tag that can only mean one tagset resolves to it
    - region resolution: L-R and L-S-R via regions lists
    - variants: at most one from variants+_globalvar, at most one from svariants,
      at most one phonetic variant, no svariant with a phonetic variant; any
      order; written canonically; synthesised sets are new sets
    - private use: unknown x- and extensions are ignored unless strict;
      x-HIS<n> selects a ROLV dialect
    - lookup never raises, and answers do not depend on query order or caching
'''

from langtag import langtag, LangTags, LangTag
from pathlib import Path
from itertools import permutations
import unittest, json

langtagjson = Path(__file__).parent.parent.parent / 'source' / 'langtags.json'


def fresh():
    ''' A new LangTags with empty caches (LangTags is a singleton per file) '''
    res = LangTags.__new__(LangTags)
    res.__init__(fname=langtagjson)
    return res


def full(ts):
    return None if ts is None else str(ts.full)


def fail_list(test, title, items, limit=200):
    if items:
        extra = "" if len(items) <= limit else "\n    ... and {} more".format(len(items) - limit)
        test.fail("\n{} ({} item(s)):\n    ".format(title, len(items))
                  + "\n    ".join(str(i) for i in items[:limit]) + extra)


class DB(unittest.TestCase):
    ''' Shared data: one LangTags and the stored tagsets '''

    @classmethod
    def setUpClass(cls):
        cls.lt = LangTags(fname=langtagjson)
        with open(langtagjson, encoding="utf-8") as inf:
            cls.data = [d for d in json.load(inf) if not d['tag'].startswith('_')]
        cls.sets = [cls.lt.get(d['full']) for d in cls.data]
        cls.stored = set(map(id, cls.sets))
        cls.gvar = cls.lt._info['globalvar']['variants']
        cls.pvar = cls.lt._info['phonvar']['variants']
        cls.groups = {}     # (lang, vars, x) -> tagsets: a language or dialect
        for t in cls.sets:
            cls.groups.setdefault(cls.key(t.full), []).append(t)

    @staticmethod
    def key(l):
        return (l.lang, tuple(l.vars or ()), tuple((l.ns or {}).get('x', ())))

    def get(self, t, **kw):
        return self.lt.get(t, **kw)

    def roundtrip(self, ts):
        ''' Tags of ts that do not look up to ts '''
        return ["{} -> {} (in {})".format(t, full(self.get(str(t))), ts.full)
                    for t in ts.allTags(use639=False) if self.get(str(t)) is not ts]


class Robustness(DB):
    ''' Lookup never raises, whatever it is given '''

    junk = [None, 123, 1.5, b'en', ['en'], ('en',), {}, object(), '', ' ', 'en ', ' en',
            'en\n', 'en\x00', '-', '--', 'en-', '-en', 'en--US', 'en_', 'ен', 'en-١٢٣',
            'x', 'x-', 'i', 'a-b', 'en-a', 'en-x', 'en-a-x-b', 'en-x-' + 'a' * 9,
            'abcdefghi', 'en-' + 'abcdefgh' * 2, '-'.join(['en', 'x'] + ['abcdefgh'] * 500),
            'en-US-US', 'en-Latn-Latn', 'en-u-nu-u-nu', 'en-fonipa-fonipa', 'x-foo', 'qaa',
            'und', 'root', 'en-x-his', 'en-x-his0', 'en-x-his123456', 'en-x-his-06861',
            'en-x-HIS99999', 'aae-x-his06861-x-his06861', '*', 'en-*', 'en-%', 'EN-us']

    def test_get_never_raises(self):
        bad = []
        for t in self.junk:
            for f in (lambda: self.lt.get(t), lambda: t in self.lt,
                      lambda: self.lt.get(t, use639=True), lambda: self.lt.get(t, strict=True),
                      lambda: self.lt.get(t, matchRegions=False)):
                try:
                    f()
                except Exception as e:
                    bad.append("{!r}: {}: {}".format(t, type(e).__name__, e))
        fail_list(self, "Lookup raised an exception", bad)

    def test_default(self):
        marker = object()
        for t in ('', 'en-Arab-TH', 'xyz-x-foo', None):
            self.assertIs(self.lt.get(t, marker), marker, t)
        with self.assertRaises(KeyError):
            self.lt['en-Arab-TH']

    def test_parser_only_syntaxerror(self):
        ''' langtag() raises SyntaxError and nothing else for bad strings '''
        bad = []
        for t in self.junk:
            if not isinstance(t, str):
                continue
            try:
                langtag(t)
            except SyntaxError:
                pass
            except Exception as e:
                bad.append("{!r}: {}".format(t, type(e).__name__))
        fail_list(self, "langtag() raised something other than SyntaxError", bad)

    def test_objects(self):
        ''' A LangTag or TagSet may be looked up in place of a string '''
        en = self.get('en')
        self.assertIs(self.get(langtag('en-GB')), self.get('en-GB'))
        self.assertIs(self.get(en), en)


class Syntax(DB):
    ''' RFC 5646 grammar corner cases '''

    def test_wellformed(self):
        tests = {
            "EN_latn_us": ("en", "Latn", "US", None, None),
            "zh-yue-HK": ("zh-yue", None, "HK", None, None),
            "zh-abc-def-ghi": ("zh-abc-def-ghi", None, None, None, None),
            "abcdefgh": ("abcdefgh", None, None, None, None),
            "en-419": ("en", None, "419", None, None),
            "de-1996": ("de", None, None, ["1996"], None),
            "en-x-x-x": ("en", None, None, None, {"x": ["x", "x"]}),
            "en-x-a-u-b": ("en", None, None, None, {"x": ["a", "u", "b"]}),
            "en-fonipa-x-central": ("en", None, None, ["fonipa"], {"x": ["central"]}),
            "en-a-bb-b-cc-x-dd": ("en", None, None, None, {"a": ["bb"], "b": ["cc"], "x": ["dd"]}),
        }
        for s, r in tests.items():
            self.assertEqual(tuple(langtag(s)), r, s)

    def test_illformed(self):
        for s in ("en-US-US", "en-Latn-Latn", "en-u", "en-u-x-a", "en-a-b", "en-u-nu-u-ca",
                  "en-abcd-efgh-ijkl-mnop", "en-x", "en-x-abcdefghi", "en-1", "1en", "en-12",
                  "en-fonipa-12345678a", "en--US", "en-", "-en"):
            with self.assertRaises(SyntaxError, msg=s):
                langtag(s)

    def test_no_language(self):
        ''' a tag without a language is a bare script and/or region: parsed as
            such unless strict, when it is an error '''
        for s, r in (("123", (None, None, "123", None, None)), ("419", (None, None, "419", None, None)),
                     ("Latn", (None, "Latn", None, None, None)), ("Latn-GB", (None, "Latn", "GB", None, None))):
            self.assertEqual(tuple(langtag(s)), r, s)
            self.assertEqual(str(langtag(s)), s, s)
            with self.assertRaises(SyntaxError, msg=s):
                langtag(s, strict=True)

    def test_private_use_swallows(self):
        ''' everything after x- is private use: vi-x-central-fonipa has no variant '''
        self.assertEqual(full(self.get('vi-x-central-fonipa')), 'vi-Latn-VN-x-central')
        self.assertEqual(full(self.get('vi-fonipa-x-central')), 'vi-Latn-VN-fonipa-x-central')

    def test_case_and_separator(self):
        ''' case and _ for - make no difference, for every stored tag '''
        bad = []
        for ts in self.sets:
            for t in ts.allTags(use639=False):
                for s in (str(t).upper(), str(t).lower(), str(t).replace('-', '_'), str(t).swapcase()):
                    if self.get(s) is not ts:
                        bad.append("{} -> {} not {}".format(s, full(self.get(s)), ts.full))
        fail_list(self, "Case or separator changed the answer", bad)


class Equivalence(DB):
    ''' The tags of a tagset and the partial tags that can only mean it '''

    def test_roundtrip_stored(self):
        ''' every tag of every stored tagset looks up to that tagset '''
        bad = sum((self.roundtrip(ts) for ts in self.sets), [])
        fail_list(self, "Stored tags that do not look up to their own tagset", bad)

    def test_unique_completion(self):
        ''' A tag of a tagset, with its script and/or region dropped, that only
            one tagset of the language or dialect can complete, resolves to that
            tagset. E.g. lah-x-landa: lah-Zzzz-PK-x-landa is the only landa set;
            scz-Latn: scz-Latn-GB is the only Latin scz set.
            Languages are taken from each tag, so aliases (sch in mrh) count. '''
        bad, seen = [], set()
        for ts in self.sets:
            group = self.groups[self.key(ts.full)]
            for t in ts.allTags(use639=False):
                for l in (t._replace(script=None, region=None), t._replace(region=None),
                          t._replace(script=None)):
                    s = str(l).lower()
                    if s in seen or s in self.lt._tags:
                        continue
                    seen.add(s)
                    cands = [c for c in group if (l.script is None or c.script == l.script)
                                and (l.region is None or c.region == l.region or l.region in c.regions)]
                    if len(cands) == 1 and self.get(s) is not cands[0]:
                        bad.append("{} -> {} not {}".format(l, full(self.get(s)), cands[0].full))
        fail_list(self, "Partial tags with only one possible tagset that do not resolve to it", bad)

    def test_filled_in(self):
        ''' Adding the tagset's own script and/or region to one of its tags
            gives the same tagset, unless that tag belongs to another tagset
            (mey-MR is explicitly the Latin mey tagset). '''
        bad = []
        for ts in self.sets:
            for t in ts.allTags(use639=False):
                for s, r in ((ts.script, None), (None, ts.region), (ts.script, ts.region)):
                    q = t._replace(script=t.script or s, region=t.region or r)
                    if q == t:
                        continue
                    owner = self.lt._tags.get(str(q).lower())
                    if owner is not None and owner is not ts:
                        continue
                    if self.get(str(q)) is not ts:
                        bad.append("{} -> {} not {}".format(q, full(self.get(str(q))), ts.full))
        fail_list(self, "A tag with its own script/region filled in does not resolve to its tagset", bad)

    def test_consistent(self):
        ''' whatever a partial tag resolves to, its full tag matches the request '''
        bad = []
        for ts in self.sets:
            for t in ts.allTags(use639=False):
                for l in (t._replace(script=None, region=None), t._replace(region=None), t._replace(script=None)):
                    r = self.get(str(l))
                    if r is None or r._isin(l):
                        continue
                    if (l.script is not None and l.script != r.script) \
                            or (l.region is not None and l.region != r.region and l.region not in r.regions) \
                            or (l.vars or None) != (r.full.vars or None) \
                            or (l.ns or {}).get('x') != (r.full.ns or {}).get('x'):
                        bad.append("{} -> {}".format(l, r.full))
        fail_list(self, "Results inconsistent with the request", bad)


class Regions(DB):
    ''' Region resolution (dev/discuss_matching.md):
        L-R: explicit L-R tag; else the default tagset (bare L) if it lists R;
             else the only tagset of L listing R; else None (ambiguous).
        L-S-R: the L-S tagset if it lists R; else the only tagset of L-S
             (same variants and x-) listing R; else None. '''

    def _claimers(self, ts, region):
        g = self.groups[self.key(ts.full)]
        return [c for c in g if c.script == ts.script and (c.region == region or region in c.regions)]

    def test_lsr(self):
        bad = []
        for ts in self.sets:
            for r in ts.regions:
                if len(self._claimers(ts, r)) > 1:
                    continue        # data conflict, see Data.test_one_locale_per_region
                q = str(ts.full._replace(region=r))
                if self.get(q) is not ts:
                    bad.append("{} -> {} not {}".format(q, full(self.get(q)), ts.full))
        fail_list(self, "L-S-R does not resolve to the only L-S tagset listing R", bad)

    def test_lr(self):
        bad = []
        bylang = {}
        for ts in self.sets:
            bylang.setdefault(ts.full.lang, []).append(ts)
        for lang, tss in bylang.items():
            dflt = self.get(lang)
            for r in sorted({x for ts in tss for x in [ts.region] + ts.regions if x}):
                q = "{}-{}".format(lang, r)
                exp = self.lt._tags.get(q.lower())
                if exp is None:
                    if dflt is not None and (dflt.region == r or r in dflt.regions):
                        exp = dflt
                    else:
                        c = [ts for ts in tss if ts.region == r or r in ts.regions]
                        exp = c[0] if len(c) == 1 else None
                if self.get(q) is not exp:
                    bad.append("{} -> {} not {}".format(q, full(self.get(q)), full(exp)))
        fail_list(self, "L-R resolution differs from the agreed order", bad)

    def test_unlisted_regions(self):
        ''' a region no tagset of the language lists does not resolve '''
        for t in ("en-AQ", "en-GL", "fr-150", "en-419", "xib-ES", "en-Latn-AQ", "ku-Arab-FR"):
            self.assertIsNone(self.get(t), t)
        self.assertIsNone(self.get("en-FR", matchRegions=False))
        self.assertIs(self.get("en-FR"), self.get("en"))      # en-US lists FR
        self.assertIsNone(self.get("en-AS", matchRegions=False))
        self.assertIs(self.get("en-AS"), self.get("en"))

    def test_strange_regions(self):
        ''' private use (AA QM-QZ XA-XZ ZZ), exceptionally reserved (UK EU UN),
            numeric (001 150 419) and Kosovo (XK) '''
        for t, f in (("sq-XK", "sq-Latn-XK"), ("en-001", "en-Latn-001"), ("es-419", "es-Latn-419"),
                     ("es-Latn-419", "es-Latn-419"), ("xib-XX", "xib-Zzzz-XX-x-iberian"),
                     ("en-150", "en-Latn-150"), ("en-001-scouse", "en-Latn-001-scouse")):
            self.assertEqual(full(self.get(t)), f, t)
        for t in ("en-UK", "en-EU", "en-UN", "en-AA", "en-QM", "en-XA", "en-XK",
                  "en-000", "en-999", "en-840", "es-013"):
            self.assertIsNone(self.get(t), t)

    def test_unknown_region(self):
        ''' ZZ (unknown region) adds nothing: it resolves as if absent '''
        for t, b in (("en-ZZ", "en"), ("en-Latn-ZZ", "en-Latn"), ("zh-Hant-ZZ", "zh-Hant"),
                     ("en-ZZ-fonipa", "en-fonipa"), ("en-ZZ-scouse", "en-scouse"),
                     ("vi-ZZ-x-central", "vi-x-central"), ("aae-ZZ-x-his06862", "aae-x-his06862")):
            self.assertIsNotNone(self.get(b), b)
            self.assertIs(self.get(t), self.get(b), t)

    def test_region_conformance(self):
        ''' test() only accepts regions that exist: a three digit code must be a
            UN M.49 code in use (000 and 999 are not) '''
        for r in ("000", "999", "840", "UK"):
            self.assertFalse(self.lt.test(langtag("en-" + r)), r)
        for r in ("001", "419", "GB", "XK"):
            self.assertTrue(self.lt.test(langtag("en-" + r)), r)

    def test_region_keeps_variant(self):
        ''' a region on a variant tag resolves through the variant's base '''
        for t, f in (("ca-ES-valencia", "ca-Latn-ES-valencia"), ("en-GB-scouse", "en-Latn-GB-scouse"),
                     ("sl-IT-rozaj-solba", "sl-Latn-SI-rozaj-solba"), ("en-AS-scouse", "en-Latn-US-scouse")):
            self.assertEqual(full(self.get(t)), f, t)


class Variants(DB):
    ''' Variants of every tagset, alone and in every legal and illegal
        combination. Canonical order: variant, svariant or phonetic, global. '''

    def _entries(self, ts):
        ''' (slot, subtags) for each variant entry ts can take.
            slots: 0 variants, 1 svariants, 2 phonetic, 3 global '''
        res = [(0, v.split('-')) for v in getattr(ts, 'variants', None) or []]
        res += [(1, v.split('-')) for v in getattr(ts, 'svariants', None) or []]
        if not getattr(ts, 'nophonvars', False):
            res += [(2, [v]) for v in self.pvar]
        res += [(3, [v]) for v in self.gvar]
        return res

    @staticmethod
    def legal(slots):
        ''' at most one of variants+global, one of svariants, one phonetic,
            and no svariant with a phonetic variant '''
        a = sum(1 for s in slots if s in (0, 3))
        return a <= 1 and slots.count(1) <= 1 and slots.count(2) <= 1 and not (1 in slots and 2 in slots)

    def _query(self, ts, combo):
        vs = [v for s, e in sorted(combo, key=lambda x: x[0]) for v in e]
        base = ts.full
        script = base.script
        if any(s == 2 for s, e in combo):
            script = "Latn"
        q = base._replace(script=script, vars=(base.vars or []) + vs)
        return q

    def _check(self, ts, combo, bad):
        q = self._query(ts, combo)
        r = self.get(str(q))
        if r is None:
            bad.append("{} -> None".format(q))
            return None
        if not any(str(t) == str(q) for t in r.allTags(use639=False)):
            bad.append("{} -> {} which does not contain it".format(q, r.full))
        if str(r.full.vars) != str(q.vars):
            bad.append("{} -> {}: variants not in canonical order".format(q, r.full))
        if id(r) in self.stored and not ts.full.vars and not str(q) in map(str, ts.allTags()):
            bad.append("{} -> stored tagset {}".format(q, r.full))
        if r is ts:
            bad.append("{} -> its base tagset".format(q))
        bad.extend(self.roundtrip(r))
        if r.sldr:
            bad.append("{} -> sldr is true for a synthesised set".format(q))
        if not all(v in str(r.windows).lower().split('-') for v in q.vars):
            bad.append("{} -> windows {} lacks a variant".format(q, r.windows))
        return r

    def test_single(self):
        bad = []
        for ts in self.sets:
            for e in self._entries(ts):
                self._check(ts, [e], bad)
        fail_list(self, "Single variants", bad)

    def test_combinations(self):
        ''' every legal pair resolves; every illegal pair fails '''
        bad, wrong = [], []
        for ts in self.sets:
            es = self._entries(ts)
            for i, a in enumerate(es):
                for b in es[i + 1:]:
                    if set(a[1]) & set(b[1]):
                        continue
                    if self.legal([a[0], b[0]]):
                        self._check(ts, [a, b], bad)
                    else:
                        q = self._query(ts, [a, b])
                        if self.get(str(q)) is not None:
                            wrong.append("{} -> {}".format(q, full(self.get(str(q)))))
        fail_list(self, "Illegal variant combinations that resolve", wrong)
        fail_list(self, "Legal variant combinations", bad)

    def test_triples(self):
        ''' variant + svariant + global is always illegal (two from variants+global);
            the only legal triple shape is impossible, so all triples fail '''
        wrong = []
        for ts in self.sets:
            es = self._entries(ts)
            if len(es) > 12:
                es = [e for e in es if e[0] != 2][:6] + [e for e in es if e[0] == 2][:2]
            for c in ((a, b, d) for i, a in enumerate(es) for j, b in enumerate(es[i + 1:], i + 1)
                                for d in es[j + 1:]):
                if self.legal([e[0] for e in c]):
                    continue
                q = self._query(ts, list(c))
                if self.get(str(q)) is not None:
                    wrong.append("{} -> {}".format(q, full(self.get(str(q)))))
        fail_list(self, "Illegal variant triples that resolve", wrong)

    def test_order(self):
        ''' all orders of the variants give the same object '''
        bad = []
        for t in ("ja-Latn-hepburn-heploc-simple", "en-scouse-fonipa", "be-tarask-simple",
                  "ca-valencia-simple", "sl-rozaj-solba-fonipa", "en-GB-scouse-fonipa",
                  "aae-fonipa-x-his06862", "en-001-scouse-fonupa"):
            l = langtag(t)
            res = self.get(t)
            if res is None:
                bad.append("{} -> None".format(t))
                continue
            for p in permutations(l.vars):
                q = str(l._replace(vars=list(p)))
                if self.get(q) is not res:
                    bad.append("{} -> {} not {}".format(q, full(self.get(q)), res.full))
        fail_list(self, "Variant order changed the answer", bad)

    def test_new_tagset(self):
        ''' a synthesised variant set is a new set; one object per set '''
        base = self.get("be")
        v = self.get("be-tarask")
        self.assertIsNot(v, base)
        self.assertIs(self.get("be-Cyrl-BY-tarask"), v)
        self.assertNotIn(id(v), self.stored)
        self.assertEqual(base.full.vars, None)          # base is unchanged
        self.assertIn("tarask", [x for x in base.svariants])
        self.assertIs(self.get("ca-valencia"), self.lt._tags["ca-valencia"])   # stored variant set

    def test_variant_implies_script(self):
        ''' a variant offered only by one tagset of the language (not by the
            default) implies that tagset: hepburn is on ja-Latn, so ja-hepburn is
            ja-Latn-JP-hepburn '''
        for t, f in (("ja-hepburn", "ja-Latn-JP-hepburn"), ("ja-JP-hepburn", "ja-Latn-JP-hepburn"),
                     ("ja-hepburn-heploc", "ja-Latn-JP-hepburn-heploc"),
                     ("ja-hepburn-simple", "ja-Latn-JP-hepburn-simple")):
            self.assertEqual(full(self.get(t)), f, t)
        self.assertIs(self.get("ja-hepburn"), self.get("ja-Latn-hepburn"))
        self.assertIsNone(self.get("ja-Jpan-hepburn"))
        bad = []
        for k, group in self.groups.items():
            dflt = self.get(str(group[0].full._replace(script=None, region=None)))
            offers = {}
            for ts in group:
                for a in ('variants', 'svariants'):
                    for v in getattr(ts, a, None) or []:
                        offers.setdefault(v, []).append(ts)
            for v, tss in offers.items():
                if dflt is not None and dflt in tss:
                    continue
                scripts = {ts.script for ts in tss}
                if len(scripts) != 1:
                    continue
                ts = self.get(str(group[0].full._replace(script=scripts.pop(), region=None)))
                if ts not in tss:
                    continue
                q = str(group[0].full._replace(script=None, region=None,
                                vars=list(group[0].full.vars or []) + v.split('-')))
                r = self.get(q)
                if r is None or r.script != ts.script or r.full.region != ts.full.region:
                    bad.append("{} -> {} not {}-{}".format(q, full(r), ts.full, v))
        fail_list(self, "Variants that imply the script of the only tagset offering them", bad)

    def test_unknown_variants(self):
        ''' variants not offered by the tagset (or with the wrong prefix) fail '''
        for t in ("en-tarask", "en-GB-oxendict", "sl-biske", "ja-Latn-heploc", "en-Cyrl-fonipa",
                  "th-Thai-fonipa", "zhk-fonipa", "en-fonipa-fonipa", "en-simple-simple",
                  "en-abcde", "en-1234"):
            self.assertIsNone(self.get(t), t)

    def test_phonetic(self):
        ''' every language or dialect with a phonetic base has one phonetic set,
            reachable from every tagset and region of the group, in Latin script '''
        bad = []
        for k, group in self.groups.items():
            free = [t for t in group if not getattr(t, 'nophonvars', False)]
            if len(free) != 1:
                continue
            p = self.get(str(free[0].full._replace(script=None, vars=list(free[0].full.vars or []) + ["fonipa"])))
            if p is None or p.script != "Latn":
                bad.append("{}-fonipa -> {}".format(free[0].full, full(p)))
                continue
            for ts in group:
                for r in [ts.region] + ts.regions:
                    q = str(ts.full._replace(script=None, region=r, vars=list(ts.full.vars or []) + ["fonipa"]))
                    if self.get(q) is not p:
                        bad.append("{} -> {} not {}".format(q, full(self.get(q)), p.full))
        fail_list(self, "Phonetic sets", bad)


class PrivateUse(DB):
    ''' x- dialects, unknown private use and extensions '''

    def test_unknown_ignored(self):
        bad = []
        for ts in self.sets[::7]:
            for ext in ("x-zzzfoo", "u-nu-thai", "t-hi-x-zzzfoo", "a-bc-u-de"):
                x = (ts.tag.ns or {}).get('x')
                q = str(ts.tag._replace(ns=None)) + "-" + ext
                if x:       # keep the tagset's own x- first in the private use
                    q = q.replace("-x-", "-x-" + "-".join(x) + "-") if "-x-" in q \
                            else q + "-x-" + "-".join(x)
                if self.get(q) is not ts:
                    bad.append("{} -> {} not {}".format(q, full(self.get(q)), ts.full))
                if "x-" in ext and self.get(q, strict=True) is not None:
                    bad.append("{} strict -> {}".format(q, full(self.get(q, strict=True))))
        fail_list(self, "Unknown private use or extensions changed the answer", bad)

    def test_extensions_strict(self):
        ''' -t- and -u- are always ignored, even when strict '''
        self.assertIs(self.get("en-u-nu-thai", strict=True), self.get("en"))
        self.assertIs(self.get("en-GB-t-hi-u-ca-buddhist", strict=True), self.get("en-GB"))

    def test_dialect_prefix(self):
        ''' the longest recognised x- prefix is kept '''
        self.assertIs(self.get("vi-x-central-zzz"), self.get("vi-x-central"))
        self.assertIs(self.get("vi-x-zzz-central"), self.get("vi"))
        self.assertIsNone(self.get("vi-x-central-zzz", strict=True))

    def test_dialect_partial(self):
        ''' an x- dialect with a single tagset resolves from its bare form '''
        bad = []
        for k, group in self.groups.items():
            if not k[2] or len(group) != 1:
                continue
            q = "{}-x-{}".format(k[0], "-".join(k[2])) if not k[1] else \
                "{}-{}-x-{}".format(k[0], "-".join(k[1]), "-".join(k[2]))
            if self.get(q) is not group[0]:
                bad.append("{} -> {} not {}".format(q, full(self.get(q)), group[0].full))
        fail_list(self, "x- dialects not found from language + private use", bad)

    def test_cache_isolation(self):
        ''' non-strict lookups do not leak into strict ones, or the other way '''
        lt = fresh()
        self.assertEqual(full(lt.get("en-x-zzz")), "en-Latn-US")
        self.assertIsNone(lt.get("en-x-zzz", strict=True))
        lt = fresh()
        self.assertIsNone(lt.get("aae-x-his06861-zzz", strict=True))
        self.assertEqual(full(lt.get("aae-x-his06861-zzz")), "aae-Latn-IT-x-sub84")
        self.assertIsNone(lt.get("aae-x-his06861-zzz", strict=True))


class His(DB):
    ''' x-HIS<n>: Registry of Language Variants codes '''

    def _parents(self):
        res = {}
        for ts in self.sets:
            for c in getattr(ts, 'rolv', None) or []:
                res.setdefault(c, []).append(ts)
        return res

    def test_every_rolv(self):
        ''' every ROLV code of every tagset gives a dialect of that tagset from
            its full tag, and from its shortest tag when the code is unique '''
        bad = []
        parents = self._parents()
        for c, tss in parents.items():
            for ts in tss:
                # the short form is the stored dialect's, if there is one
                rods = [t for t in self.sets if getattr(t, 'rod', None) == c and t.full.lang == ts.full.lang]
                forms = [ts.full] + ([ts.tag] if len(tss) == 1 and not rods else [])
                for f in forms:
                    x = (f.ns or {}).get('x', [])
                    q = str(f._replace(ns={'x': list(x) + ['his' + c]}))
                    r = self.get(q)
                    if r is None:
                        bad.append("{} -> None".format(q))
                        continue
                    if getattr(r, 'rod', None) != c:
                        bad.append("{} -> {} with rod {}".format(q, r.full, getattr(r, 'rod', None)))
                    if r.full.lang != ts.full.lang or r.script != ts.script:
                        bad.append("{} -> {}: not a dialect of {}".format(q, r.full, ts.full))
                    bad.extend(self.roundtrip(r))
        fail_list(self, "ROLV codes", bad)

    def test_every_rod(self):
        ''' a stored dialect tagset is found from its language and its rod '''
        bad = []
        for ts in self.sets:
            c = getattr(ts, 'rod', None)
            if c is None or not str(c).isdigit():
                continue
            q = "{}-x-his{}".format(ts.full.lang, c)
            if len([t for t in self.sets if getattr(t, 'rod', None) == c and t.full.lang == ts.full.lang]) > 1:
                continue
            if self.get(q) is not ts:
                bad.append("{} -> {} not {}".format(q, full(self.get(q)), ts.full))
        fail_list(self, "Stored dialects by x-HIS<rod>", bad)

    def test_spellings(self):
        ''' codes are matched numerically and case-insensitively '''
        r = self.get("aae-x-his06862")
        for t in ("aae-x-HIS6862", "aae-x-His06862", "aae_x_his6862"):
            self.assertIs(self.get(t), r, t)

    def test_his_with_variants(self):
        for t, f in (("aae-fonipa-x-his06862", "aae-Latn-IT-fonipa-x-his06862"),
                     ("aae-simple-x-his06862", "aae-Latn-IT-simple-x-his06862"),
                     ("ca-valencia-x-his08659", "ca-Latn-ES-valencia-x-his08659")):
            self.assertEqual(full(self.get(t)), f, t)

    def test_his_errors(self):
        ''' another language's code is always an error; extra private use after
            the code is ignored unless strict; HIS not first is just private use '''
        self.assertIsNone(self.get("en-x-his06861"))
        self.assertIsNone(self.get("en-x-his06861", strict=True))
        self.assertIsNone(self.get("aae-x-his06861-zzz", strict=True))
        self.assertIs(self.get("aae-x-zzz-his06861"), self.get("aae"))
        self.assertIsNone(self.get("aae-x-his99999", strict=True))
        self.assertIs(self.get("aae-x-his99999"), self.get("aae"))
        self.assertIsNone(self.get("aae-Arab-x-his06862"))
        # at most one HIS code, wherever it is
        for t in ("aae-x-his06861-his06862", "aae-x-his06862-his06862", "aae-x-zzz-his06861-his06862",
                  "aae-x-his06861-zzz-his06862"):
            self.assertIsNone(self.get(t), t)
            self.assertIsNone(self.get(t, strict=True), t)
        # a dialect variant and a ROLV dialect is two dialects; a HIS code for
        # scouse needs a scouse tagset with that rolv
        self.assertEqual(full(self.get("en-x-his00025")), "en-Latn-US-x-his00025")
        for t in ("en-scouse-x-his00025", "en-GB-scouse-x-his00025", "en-scouse-fonipa-x-his00025"):
            self.assertIsNone(self.get(t), t)
            self.assertIsNone(self.get(t, strict=True), t)


class Undetermined(DB):
    ''' und, mul and qaa-qtz, and tags with no language (Martin, 2026-11-20).
        und has no defaults: und-<anything> is a tagset of its own, with exactly
        the script and region given, the same object for identical tags. Its
        stored tags (und, und-Zyyy, und-001) keep the stored tagset. A tag with no
        language looks up as und (Latn is und-Latn) unless strict. mul is not und
        but behaves the same way. qaa-qtz always give a new tagset with no script
        or region unless the tag has one. x-foo is neither qaa nor und. '''

    def _synth(self, t, lang, script, region, vars=None, x=None):
        r = self.get(t)
        self.assertIsNotNone(r, t)
        self.assertNotIn(id(r), self.stored, t)
        self.assertEqual((r.full.lang, r.script, r.region, r.full.vars, (r.full.ns or {}).get('x')),
                         (lang, script, region, vars, x), t)
        self.assertEqual(self.roundtrip(r), [], t)
        for s in (t.upper(), t.lower(), t.replace('-', '_')):
            self.assertIs(self.get(s), r, s)
        return r

    def test_stored(self):
        for l in ("und", "mul"):
            st = self.lt._tags[l]
            for t in (l, l + "-Zyyy", l + "-001", l + "-Zyyy-001"):
                self.assertIs(self.get(t), st, t)

    def test_no_defaults(self):
        for l in ("und", "mul"):
            a = self._synth(l + "-Latn", l, "Latn", None)
            b = self._synth(l + "-GB", l, None, "GB")
            c = self._synth(l + "-Latn-GB", l, "Latn", "GB")
            d = self._synth(l + "-419", l, None, "419")
            e = self._synth(l + "-Arab-x-foo", l, "Arab", None, x=["foo"])
            self._synth(l + "-fonipa", l, "Latn", None, vars=["fonipa"])
            self._synth(l + "-GB-simple", l, None, "GB", vars=["simple"])
            for t in (l + "-Xyzw", l + "-AB", l + "-Arab-fonipa", l + "-fonipa-fonupa",
                      l + "-abcde", l + "-x-his06861"):
                self.assertIsNone(self.get(t), t)
            self.assertEqual(len({id(x) for x in (a, b, c, d, e, self.lt._tags[l])}), 6, l)
        self.assertIsNot(self.get("mul-Latn"), self.get("und-Latn"))

    def test_no_language(self):
        ''' a tag without a language looks up as und, unless strict '''
        for s, u in (("Latn", "und-Latn"), ("Latn-GB", "und-Latn-GB"),
                     ("419", "und-419"), ("001", "und"), ("Zyyy", "und")):
            self.assertIsNotNone(self.get(u), u)
            self.assertIs(self.get(s), self.get(u), s)
            self.assertIsNone(self.get(s, strict=True), s)
        # a two letter region alone is a language subtag (gb, us), not und-GB
        for s in ("GB", "US"):
            self.assertEqual(langtag(s).lang, s.lower(), s)
            self.assertIsNot(self.get(s), self.get("und-" + s), s)

    def test_qaa(self):
        for l in ("qaa", "qbz", "qtz"):
            a = self._synth(l, l, None, None)
            b = self._synth(l + "-Latn", l, "Latn", None)
            c = self._synth(l + "-GB", l, None, "GB")
            d = self._synth(l + "-x-foo", l, None, None, x=["foo"])
            self._synth(l + "-fonipa", l, "Latn", None, vars=["fonipa"])
            self.assertEqual(len({id(x) for x in (a, b, c, d)}), 4, l)
        self.assertIsNot(self.get("qaa"), self.get("qab"))
        self.assertIsNot(self.get("qaa-Latn"), self.get("und-Latn"))

    def test_private_use_only(self):
        ''' x-foo is a tagset of its own: not qaa, qaa-x-foo or und-x-foo '''
        r = self._synth("x-foo", None, None, None, x=["foo"])
        for t in ("qaa", "qaa-x-foo", "und-x-foo", "x-bar", "x-foo-bar"):
            self.assertIsNot(self.get(t), r, t)


class Iso639(DB):
    ''' use639: the ISO 639-3 code works in place of the language subtag '''

    def test_every_tagset(self):
        # the language's code is the one on its default tagset (bare language)
        codes = {}
        for ts in self.sets:
            d = self.get(ts.full.lang)
            if d is not None and getattr(d, '_iso639_3', None):
                codes[ts.full.lang] = d._iso639_3
        langs = {}
        for l, c in codes.items():
            langs.setdefault(c, set()).add(l)
        bad = []
        for ts in self.sets:
            c = codes.get(ts.full.lang)
            if c is None or c == ts.full.lang or len(langs[c]) > 1:
                continue        # a code used by two languages (data error) is ambiguous
            q = str(ts.full._replace(lang=c))
            if self.get(q, use639=True) is not ts:
                bad.append("{} -> {} not {}".format(q, full(self.get(q, use639=True)), ts.full))
        fail_list(self, "ISO 639-3 lookups (use639=True)", bad)

    def test_derived(self):
        for t, f in (("eng-fonipa", "en-Latn-US-fonipa"), ("bel-tarask", "be-Cyrl-BY-tarask"),
                     ("eng-AS", "en-Latn-US"), ("eng-GB", "en-Latn-GB"), ("zho-TW", "zh-Hant-TW")):
            self.assertEqual(full(self.get(t, use639=True)), f, t)
            self.assertIsNone(self.get(t), t)
        self.assertIs(self.get("eng-fonipa", use639=True), self.get("en-fonipa"))


class Canonical(DB):
    ''' RFC 5646 canonicalisation: deprecated and grandfathered tags map to
        their Preferred-Value. (Design still open: dev/discuss_matching.md) '''

    def test_extlang(self):
        self.assertIs(self.get("zh-yue"), self.get("yue"))
        self.assertIs(self.get("zh-yue-HK"), self.get("yue-HK"))
        self.assertIs(self.get("zh-cmn"), self.get("cmn"))

    def test_grandfathered(self):
        for t, p in (("i-klingon", "tlh"), ("art-lojban", "jbo"), ("zh-min-nan", "nan"),
                     ("zh-hakka", "hak"), ("en-GB-oed", "en-GB-oxendict"), ("sgn-BR", "bzs"),
                     ("zh-guoyu", "cmn"), ("i-navajo", "nv")):
            self.assertIs(self.get(t), self.get(p), t)

    def test_deprecated_regions(self):
        for t, p in (("my-BU", "my-MM"), ("de-DD", "de-DE"), ("pt-TP", "pt-TL"),
                     ("fr-ZR", "fr-CD"), ("fr-FX", "fr-FR")):
            self.assertIsNotNone(self.get(p), p)
            self.assertIs(self.get(t), self.get(p), t)


class Determinism(DB):
    ''' answers do not depend on query order or on what is cached '''

    def test_query_order(self):
        qs = []
        for ts in self.sets[::5]:
            l = ts.tag
            qs += [str(l), str(l) + "-fonipa", str(l) + "-simple", str(l) + "-x-zzz",
                   str(ts.full._replace(region=(ts.regions or [None])[0]))]
        a, b = fresh(), fresh()
        ra = {q: full(a.get(q)) for q in qs}
        rb = {q: full(b.get(q)) for q in reversed(qs)}
        diff = ["{}: {} / {}".format(q, ra[q], rb[q]) for q in qs if ra[q] != rb[q]]
        fail_list(self, "Answer depends on query order", diff)

    def test_same_object(self):
        ''' the same set comes back as the same object, however it is asked for '''
        lt = fresh()
        p = lt.get("th-TH-fonipa")
        self.assertIs(lt.get("th-fonipa"), p)
        self.assertIs(lt.get("th-Latn-fonipa"), p)
        d = lt.get("aae-x-his06862")
        self.assertIs(lt.get("aae-Latn-IT-x-his06862"), d)


class Data(DB):
    ''' Data rules that the lookup rules rely on '''

    def test_one_locale_per_region(self):
        ''' within a language + script (+ variants and x-) a region belongs to
            one tagset '''
        claims = {}
        for ts in self.sets:
            k = self.key(ts.full) + (ts.script,)
            for r in [ts.region] + ts.regions:
                claims.setdefault(k + (r,), []).append(str(ts.full))
        bad = ["{}-{}-{}: {}".format(k[0], k[3], k[4], " / ".join(v))
                    for k, v in sorted(claims.items(), key=str) if len(v) > 1]
        fail_list(self, "Regions claimed by more than one tagset of the same script", bad)


if __name__ == "__main__":
    unittest.main()
