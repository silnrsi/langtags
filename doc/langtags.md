# LangTags

Language tags are identifiers used for locales, orthographies and writing systems and in extreme cases, just languages. For more information on what is a language tag and how they are used in this project see [tagging.md].

## langtags.txt

Langtags.txt contains a sequence of equivalence sets. Each set consists of a list of language tags separated by `=`. The first tag on the line is the canonical tag and the last tag on the line is the maximal tag. In addition, a tag is prefixed with `*` if there is an entry in the SLDR for that particular tag.

The preferred download location for the text data file is <https://ldml.api.sil.org/langtags.txt>

## langtags.json

This file brings together information regarding a tag equivalence set. It includes information from the following sources:

- ISO 639 parts 1 and 3 - language codes
- ISO 15924 - script codes
- ISO 3166 part 1 - region codes
- Ethnologue: Language names and autonyms
- IANA tag registry - standard language tag components
- CLDR likely\_subtags.xml,  - agreed defaults and aliases
- SLDR [https://github.com/silnrsi/sldr]

Current API version 1.2.1

Unless otherwise stated all fields were added at v1.0.0. 

The preferred download location for the json data file is <https://ldml.api.sil.org/langtags.json>

Langtags.json consists of an array of objects. Each object corresponds to an equivalence set. The fields in that object are defined as:

- **tag** The canonical tag for this set. This is the normal tag to use for the set. Conforms to BCP 47
- **full** The full tag for this set. Use this if you want to pull out the details. Conforms to BCP 47
- **tags** A list of other tags that are equivalent. Each conforms to BCP 47
- **variants** A list of variant tag components that may occur with tags in this set. A tag with a variant is not equivalent to other tags in this set.
- **iso639_3** The ISO639-3 code for the language of the **tag** in this set.
- **region** Region code, from the full tag, for this set. Conforms to ISO 3166-1.
- **regions** Other regions that may be used with these tags. See the following section on regions list. Each conforms to ISO 3166-1
- **regionname** The English name for this region taken from the IANA registry.
- **iana** The IANA names for the language of the canonical tag. Is an array. \[Array added 1.1.1\] \[Always an array 1.2.0\]
- **name** The name from the Ethnologue names list for the language and region of the full tag. If this does not exist, then any name from the list of names given for this language is used. If this fails to find anything, then the **iana** entry is used. Thus **name** is never empty.
- **names** Other alternative names for this language coming from the Ethnologue names list, including alternate names and names and alternate names from other regions.
- **localname** If present, this gives the name of the language in the orthography specified by this set. Also known as the autonym. This comes from CLDR/SLDR data. \[Deprecated 1.1.0, use localnames instead\]
- **sldr** True if there is a file in the SLDR for at least one of the tags in this set.
- **nophonvars** If present and true indicates that this tag may not take a phonetic alphabet variant. This occurs if the tag has a hidden script which is not Latn.
- **script** Specifies the script component of the full tag, for this set. Conforms to ISO 15924. \[Added 1.0.1\]
- **localnames** Specifies a list of local names (autonyms), coming from the Ethnologue. \[Added 1.1.0\]
- **latnnames** Specifies a list of romanised autonyms in direct correspondance to the localnames list. \[Added 1.1.0\]
- **rod** A Registry of Dialects numeric code \(as a string\) \[Added 1.1.1\]
- **suppress** If present and true indicates that the IANA language tag registry has the suppress script set for this language. \[Added 1.1.1\]
- **windows** Windows requires a strict BCP-47 interpretation and requires a script tag unless the suppress script from the IANA registry is the same as the script. This field is always present and may be the same as the **tag** field or one of the values in the **tags** list. \[Added 1.1.1\]
- **obsolete** If present and true indicates that the language is obsolete \[Added 1.2.1\]
- **unwritten** If present and true indicates that the language is unwritten. It may still have a non Zyyy script due to regional inference. \[Added 1.2.1\]
- **macrolang** If present another language tag which is a macro language containing this language. \[Added 1.3.1\]

### Special tags

There are various specially named (via the **tag** field) objects that occur at the start of the list. All special tags start with `_` and the set may grow:

#### _globalvar

- **variants** Lists variants that may occur with any language tag.

#### _phonvar

- **variants** Lists variants that may occur with any language tag for the **Latn** script, whether implicit or explicitly stated. Notice that for some languages there is no entry for a Latin script form of the language. For example `th-Latn` does not occur in the list of tags anywhere. But `th-fonipa` is a valid tag, whereas `th-Thai-fonipa` is not.

#### _version

- **api** Contains a semantic version string "x.y.z" where x is a major version not backwardly structurally compatible, y is a minor version involving removing fields and z is minimal change that simply adds fields or extra header records (special tags of the form \_tag.)
- **date** Contains the date of the file creation in the form year-month-date with each component a number.

#### _conformance

Holds information to aid in conformance testing for language tags. \[Added 1.2.2\]

- **regions** Combine this with a list of every region referenced in every tagset to come up with a list of possible regions that are conformant.
- **scripts** Combine this with a list of every script field in every tagset to come up with a list of possible script subtags that are conformant.

### File invariants

- A language tag will never occur in more than one place in the fields **tag** **full** or **tags**, except if it occurs in both the **tag** and **full** fields of a record.
- All plural fields store their results as arrays.
- Empty fields are not stored in the record.
- The **tag** and the **full** fields are not stable and may change between versions of the data file. But they will always appear somewhere in the equivalence set. In effect the equivalence set is stable in terms of once something is in it, it is not removed (unless there is an actual fault).
- A tagset may have an empty **localname** while still having a non empty **localnames**. Likewise the same name may occur as both **localname** and in **localnames**.

### Regions list

Language tags have a number of uses. There are two major uses: orthography
identification and locale identification. An orthography may be used in multiple
regions. For example it may be used by a diaspora community. At a locale level,
though, the use of an orthography in a different region may need to be adapted
to incorporate region specific locale variation that is based on a different
regional standard.

For example, consider en-FR. It is considered to have the same orthography as
en-US, but in France, the week is considered to start on a Monday, while in the
US it is considered to start on a Sunday. Thus en-FR is orthographically the
same as en-US, but is different at a locale level.

The tagsets in this database are identifying orthography equivalence. The
regions list within a tagset gives a list of orthographically equivalent
regions. But users should be aware that this does not imply a locale
equivalence. For the purposes of this database, if two tags are from the same
tagset (including the region being in the region list for the tagset) AND they
have the same region subtag, then they are considered to be equivalent at the
locale level.

With regard to the CLDR, the CLDR includes 'empty' LDML files (only consisting
of an identity block) for each territory for a given language. Only if such a
file includes actual content differences is a new tagset created for it. The
mapping between language and territories may be found in supplementalData at
`supplementalData/languageData/language[@type="lang"]`.

### Variants field

The variants field lists different variants that may occur with the tags in the equivalence set. As such, a tag with a variant is in a different equivalence set. Thus bg, bg-BG, bg-Cyrl, bg-Cyrl-BG forms one set and bg-ivanchov, bg-BG-ivanchov, bg-Cyrl-ivanchov, bg-Cyrl-BG-ivanchov forms another. The header record \_globalvar contains a variants field that should be appended to the variants field of every equivalence set. Thankfully this list is short and it may not make semantic sense to use it. Not all languages have a simplified form, but in theory they might. See [IANA simple variant](https://www.iana.org/assignments/lang-subtags-templates/simple.txt) for more details.

The \_phonvar header record contains a variants field list that may be applied to any equivalence set, but it implies Latn script even if used with a non-Latin script language. For examle from our bg-Cyrl-BG example, we also have an equivalence set of bg-fonipa, bg-BG-fonipa, bg-Latn-fonipa, bg-Latn-BG-fonipa. Only one of the list of variants in the \_phonvar variants list may occur in a tag, at most.

The **variants** field itself does not chain. Thus if there is more than one variant in the field then there is not a further variant that is a sequence of them both. For example be-Cyrl-BY has a **variants** field containing 1959acad and tarask. So there could be `be-1959acad` and `be-tarask` but not `be-1959acad-tarask`. If such a thing were allowed, then the variants list would include an entry 1959acad-tarask. For an example see ja-Latn with `hepburn` and `hepburn-heploc`.

Thus a complete list of equivalence sets for bg-Cyrl-GB (with only one of the variants from \_phonvar used) would be:

- bg, bg-BG, bg-Cyrl, bg-Cyrl-BG
- bg-ivanchov, bg-BG-ivanchov, bg-Cyrl-ivanchov, bg-Cyrl-BG-ivanchov
- bg-fonipa, bg-BG-fonipa, bg-Latn-fonipa, bg-Latn-BG-fonipa 
- bg-fonipa-ivanchov, bg-BG-fonipa-ivanchov, bg-Latn-fonipa-ivanchov, bg-Latn-BG-fonipa-ivanchov
- bg-simple, bg-BG-simple, bg-Cyrl-simple, bg-Cyrl-BG-simple
- bg-ivanchov-simple, bg-BG-ivanchov-simple, bg-Cyrl-ivanchov-simple, bg-Cyrl-BG-ivanchov-simple
- bg-fonipa-simple, bg-BG-fonipa-simple, bg-Latn-fonipa-simple, bg-Latn-BG-fonipa-simple
- bg-fonipa-ivanchov-simple, bg-BG-fonipa-ivanchov-simple, bg-Latn-fonipa-ivanchov-simple, bg-Latn-BG-fonipa-ivanchov-simple

### Macro Languages

The language component of a language tag may be from ISO639-1 (when it is a 2
letter code) or ISO639-3 (when a 3 letter code). When ISO639-3 was created, it
was designed to incorporate the existing 3 letter coding scheme of ISO639-2. As
part of the analysis for the creation of ISO639-3, Constable and Simons wrote a
paper: ["An Analysis of ISO 639: Preparing the way for advancements in language
identification
standards"](https://www.ethnologue.com/14/iso639/An_analysis_of_ISO_639.pdf).
Section 3 of this paper examines a number of issues, in particular the concept
of Collection codes. These came to be known as macro languages. In summary a
macro language is a language that is a collection of languages. A language may be
a member of a macro language.

For many macro languages, there is a representative language for that macro
language. In many cases the macro language code is more popular than the
representative langauge code. Thus, for example, in the CLDR, the macro language
code is used instead of the representative language code. For this reason,
langtags.json unifies the representative language tags into the macro language
tag set rather than having a separate tag set for them, and gives the tag for
the tag set in terms of the macro language rather than the representative
language.

Other languages that are part of a macro language are given a macrolang field
identifying the macro language they are part of.

