# LangTags

## langtags.txt

Langtags.txt contains a sequence of equivalence sets. Each set consists of a list of language tags separated by `=`. The first tag on the line is the canonical tag and the last tag on the line is the maximal tag. In addition, a tag is prefixed with `*` if there is an entry in the SLDR for that particular tag.

The preferred download location for the text data file is <https://ldml.api.sil.org/langtags.txt>

## langtags.json

Current API version 1.1.0 Unless otherwise stated all fields were add at v1.0.0. The preferred download location for the json data file is <https://ldml.api.sil.org/langtags.json>

Langtags.json consists of an array of objects. Each object corresponds to an equivalence set. The fields in that object are defined as:

- **tag** The canonical tag for this set. This is the normal tag to use for the set. Conforms to BCP 47
- **full** The full tag for this set. Use this if you want to pull out the details. Conforms to BCP 47
- **tags** A list of other tags that are equivalent. Each conforms to BCP 47
- **variants** A list of variant tag components that may occur with tags in this set. A tag with a variant is not equivalent to other tags in this set. But a tag in this set with a variant is considered equivalent to another tag in this set with the same variant.
- **iso639_3** The ISO639-3 code for the language of the **tag** in this set.
- **region** Region code, from the full tag, for this set. Conforms to ISO 3166-1.
- **regions** Other regions that may be used with these tags. A tag from this set with one of the extra regions is not equivalent to other tags in this set, unless they have the same region component. Each conforms to ISO 3166-1
- **regionname** The English name for this region taken from the IANA registry.
- **iana** The IANA name for the language of the canonical tag.
- **name** The name from the Ethnologue names list for the language and region of the full tag. If this does not exist, then any name from the list of names given for this language is used. If this fails to find anything, then the **iana** entry is used. Thus **name** is never empty.
- **names** Other alternative names for this language coming from the Ethnologue names list, including alternate names and names and alternate names from other regions.
- **localname** If present, this gives the name of the language in the orthography specified by this set. Also known as the autonym. This comes from CLDR/SLDR data. \[Deprecated 1.1.0, use localnames instead\]
- **sldr** True if there is a file in the SLDR for at least one of the tags in this set.
- **nophonvars** If present and true indicates that this tag may not take a phonetic alphabet variant. This occurs if the tag has a hidden script which is not Latn.
- **script** Specifies the script component of the full tag, for this set. Conforms to ISO 15924. \[Added 1.0.1\]
- **localnames** Specifies a list of local names (autonyms), coming from the Ethnologue. \[Added 1.1.0\]
- **latnnames** Specifies a list of romanised autonyms in direct correspondance to the localnames list. \[Added 1.1.0\]

### Special tags

There are three specially named (via the **tag** field) objects that occur at the start of the list. All special tags start with `_`:

#### _globalvar

- **variants** Lists variants that may occur with any language tag.

#### _phonvar

- **variants** Lists variants that may occur with any language tag for the **Latn** script, whether implicit or explicitly stated. Notice that for some languages there is no entry for a Latin script form of the language. For example `th-Latn` does not occur in the list of tags anywhere. But `th-fonipa` is a valid tag, whereas `th-Thai-fonipa` is not.

#### _version

- **api** Contains a semantic version string "x.y.z" where x is a major version not backwardly structurally compatible, y is a minor version involving removing fields and z is minimal change that simply adds fields or extra header records (special tags of the form \_tag.)
- **date** Contains a date in the form year-month-date with each component a number.

### File invariants

- A language tag will never occur in more than one place in the fields **tag** **full** or **tags**, except if it occurs in both the **tag** and **full** fields of a record.
- All plural fields store their results as arrays.
- Empty fields are not stored in the record.
- The **tag** and the **full** fields are not stable and may change between versions of the data file. But they will always appear somewhere in the equivalence set. In effect the equivalence set is stable in terms of once something is in it, it is not removed (unless there is an actual fault).
- A tagset may have an empy **localname** while still having a non empty **localnames**. Likewise the same name may occur as both **localname** and in **localnames**.

### Variants field

The variants field lists different variants that may occur with the tags in the equivalence set. As such, a tag with a variant is in a different equivalence set. Thus bg, bg-BG, bg-Cyrl, bg-Cyrl-BG forms one set and bg-ivanchov, bg-BG-ivanchov, bg-Cyrl-ivanchov, bg-Cyrl-BG-ivanchov forms another. The header record \_globalvar contains a variants field that should be appended to the variants field of every equivalence set. Thankfully this list is short and it may not make semantic sense to use it. Not all languages have a simplified form, but in theory they might. See [IANA simple variant](https://www.iana.org/assignments/lang-subtags-templates/simple.txt) for more details.

The \_phonvar header record contains a variants field list that may be applied to any equivalence set, but it implies Latn script even if used with a non-Latin script language. For examle from our bg-Cyrl-BG example, we also have an equivalence set of bg-fonipa, bg-BG-fonipa, bg-Latn-fonipa, bg-Latn-BG-fonipa. Only one of the list of variants in the \_phonvar variants list may occur in a tag, at most.

The **variants** field itself does not chain. Thus if there is more than one variant in the field then there is not a further variant that is a sequence of them both. For example be-Cyrl-BY has a **variants** field containing 1959acad and tarask. So there could be `be-1959acad` and `be-tarask` but not `be-1959acad-tarask`. If such a thing were allowed, then the variants list would include an entry 1959acad-tarask. For an example see ja-Latn with `hepburn` and `hepburm-heploc`.

Thus a complete list of equivalence sets for bg-Cyrl-GB (with only one of the variants from \_phonvar used) would be:

- bg, bg-BG, bg-Cyrl, bg-Cyrl-BG
- bg-ivanchov, bg-BG-ivanchov, bg-Cyrl-ivanchov, bg-Cyrl-BG-ivanchov
- bg-fonipa, bg-BG-fonipa, bg-Latn-fonipa, bg-Latn-BG-fonipa 
- bg-fonipa-ivanchov, bg-BG-fonipa-ivanchov, bg-Latn-fonipa-ivanchov, bg-Latn-BG-fonipa-ivanchov
- bg-simple, bg-BG-simple, bg-Cyrl-simple, bg-Cyrl-BG-simple
- bg-ivanchov-simple, bg-BG-ivanchov-simple, bg-Cyrl-ivanchov-simple, bg-Cyrl-BG-ivanchov-simple
- bg-fonipa-simple, bg-BG-fonipa-simple, bg-Latn-fonipa-simple, bg-Latn-BG-fonipa-simple
- bg-fonipa-ivanchov-simple, bg-BG-fonipa-ivanchov-simple, bg-Latn-fonipa-ivanchov-simple, bg-Latn-BG-fonipa-ivanchov-simple
