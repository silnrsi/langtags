# Alltags

## langtags.txt

Langtags.txt contains a sequence of equivalence sets. Each set consists of a list of language tags separated by `=`. The first tag on the line is the canonical tag and the last tag on the line is the maximal tag. In addition, a tag is prefixed with `*` if there is an entry in the SLDR for that particular tag.

## langtags.json

Langtags.json consists of an array of objects. Each object corresponds to an equivalence set. The fields in that object are defined as:

- **tag** The canonical tag for this set.
- **full** The full tag for this set
- **tags** A list of other tags that are equivalent
- **variants** A list of variant tag components that may occur with tags in this set. A tag with a variant is not equivalent to other tags in this set. But a tag in this set with a variant is considered equivalent to another tag in this set with the same variant.
- **iso639_3** The ISO639-3 code for the language of the tags in this set.
- **region** Region code, from the full tag, for this set.
- **regions** Other regions that may be used with these tags. A tag from this set with one of the extra regions is not equivalent to other tags in this set, unless they have the same region component.
- **regionname** The English name for this region taken from the IANA registry.
- **iana** The IANA name for the language of the canonical tag.
- **name** The name from the Ethnologue names list for the language and region of the full tag. If this does not exist, then any name from the list of names given for this language is used. If this fails to find anything, then the **iana** entry is used. Thus **name** is never empty.
- **names** Other alternative names for this language coming from the Ethnologue names list, including alternate names and names and alternate names from other regions.
- **localname** If present, this gives the name of the language in the orthography specified by this set.
- **sldr** True if there is a file in the SLDR for at least one of the tags in this set.
- **nophonvars** If present and true indicates that this tag may not take a phonetic alphabet variant. This occurs if the tag has a hidden script which is not Latn.

There are two specially named (via the **tag** field) objects that occur at the start of the list:

- **_globalvar** The **variants** field lists variants that may occur with any language tag.
- **_phonvar** The **variants** field lists variants that may occur with any language tag for the **Latn** script, whether implicit or explicitly stated. Notice that for some languages there is no entry for a Latin script form of the language. For example `th-Latn` does not occur in the list of tags anywhere. But `th-fonipa` is a valid tag, whereas `th-Thai-fonipa` is not.

Some invariants:

- A language tag will never occur in more than one place in the fields **tag** **full** or **tags**, except if it occurs in both the **tag** and **full** fields of a record. It will never occur in more than one field.
- All plural fields store their results as arrays.
- Empty fields may not be stored in the record. Exceptions to this are
