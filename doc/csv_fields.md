# CSV Fields
This document describes each of the fields in the CSV file.

## Lang\_Id
This field is normative and is unique in the file. A record with a Lang\_Id field of _lang_-_RE_ is only necessary if there is a record with Lang\_id of _lang_ which has a likely\_subtag with a different _RE_. In addition if there is a _lang_-_script_ with a likely\_subtag with the same _RE_ then a record of _lang_-_RE_ is not needed. For example:
```
ahk = ahk-Latn-MM
ahk-Thai = ahk-Thai-TH
```
There is no need for a `ahk-MM` and there is only need for `ahk-TH` if the likely subtag is not `ahk-Thai-TH` which in this case is required because:
```
ahk-TH = ahk-Latn-TH
```

## likely\_subtag
This field is required and normative.

## LangName
This field may end up as one of the names in langtags.json. This allows for the contrastive naming of dialects and other different rows.

## regions
This field contains a space separated list of region codes. This field only has meaning if the Lang_\Id has no region component. It says that appending one of the region codes to the Lang\_Id will result in a tag that is equivalent to the tags from this row.
```
aal = aal-Latn-CM, regions=NG
```
This implies that `aal-NG = aal-Latn-CM = aal-Latn-NG` etc.

## variants
This is a space separated list of possible variants applicable to this tag, beyond the global ones.

## ROD
This specifies the ROD code for this language tag.

## RODs
This specifies a space separated list of all the ROD codes that are dialects of this language tag. Ultimately we desire to have entries for each of these ROD codes with a corresponding ROD field to each of the ROD codes in the RODs list.

## Macro
If set this field specifies that this language tag row should be subsumed within another row. That is there is no record for this row, but the information in this row is merged into the row indicated by this macro field. There are a number of ways this field is used. Here are some examples:
```
aam = aam-Latn-TZ, macro=aas, deprecated=aas
aas = aas-Latn-TZ

abq-Cyrl = abq-Cyrl-RU
abq-Latn = abq-Latn-TR
abq = abq-Cyrl-RU, macro=abq-Cyrl

ar = ar-Arab-EG
ar-Brai = ar-Brai-SA
arb = arb-Arab-SA, macro=ar
arb-Brai = arb-Brai-SA, macro=ar
```
The first example is the last one of `ar`. Here `ar` is a macro language, and in the CLDR all macro languages are given a default concrete language to use when referred to. In addition the default concrete language is generally referred to by the macro language. In this case `arb` is generally referred to by `ar`. Thus we specify the macro field for `arb` as `ar`. Notice that because `arb` is `arb-Arab-SA` but `ar` is `ar-Arab-EG`, `arb` is considered equivalent to `ar-SA` which will be used in preference to `arb`. There is no such difficulty with `arb-Brai` which is simply resolved to `ar-Brai-SA`. Notice that the processing works out the script and regions appropriately.

The second example of `abq` is the odd case where we want the default tag for `abq` to be `abg-Cyrl`. The problem here is that while CLDR requires a default script in all cases for its data, and uses Cyrl in this case, it is not politically appropriate to specify a default. So `abq` should be interpretted as `abq-Cyrl` and also `abq-Cyrl` should be used in preference.

The final example of `aam` is a common case of deprecation. The macro field instructs that `aam` be replaced by `aas`, and the deprecated field simply records that the reason for this association is deprecation. See the deprecated field for more information.

## unwritten

Indicates with a value of 1, that the language is unwritten even if there is a script specified for the language. The reason that it may have a script is that the script is inferred from the socio-linguistic context indicating what the script would be if it were to have a script. For truly unknown scripts, use the Zyyy code.

The field may be used to limit information to written languages.

## obsolete

This is 1 for dead languages. The field may be used to limit information to interesting languages.

## deprecated

This field specifies that this row has been deprecated. It can simply include a 1 to indicate that the row is deprecated. But it should really specify which row this row has been deprecated to. If the tag for this row is encountered, how should it be treated. If the macro field is empty, it inherits the value of the deprecated field (if a language tag rather than just 1).

## areas

The ethnologue has area codes for languages that group languages into wide areas. This is useful for working on a subset of the languages pertinent to a particular area. The information is not required and is informative.

## ISO 639-3

This is the ISO639-3 3 letter code regardless of what the Lang\_Id value is. The value is informative although is propagated to langtags.json.

## confirmed

This field lists user ids of people who wish to register an interest in the particular record. Those wishing to change normative information (Lang\_Id, likely\_subtag) are requested to build consensus with all the users on the confirmation list. It also indicates that this user affirms the data.

User ids are an informal identifier to map to email addresses. Not sure how to maintain that list at the moment, but SIL does have the list.

## Date modified

This is a redundant tracking field and should be removed since version control does a better job.

## comments

Free form comments on the record.

