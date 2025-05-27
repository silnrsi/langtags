# langtag module

Langtag is a module for working with language tag sets. A tag set is a set of
orthographically equivalent tags along with various information. The core data
for the database may be found here: [https://ldml.api.sil.org/langtags.json].

## Installatino

- pip install langtag

langtag is only dependent on python3 and its core libraries (including json).

## Example

```
from langtag import lookup, langtag
t = lookup('en-Latn')       # find a tagset returning a TagSet object
l = langtag('en-Latn')      # create an underling LangTag object
simple = str(t.tag)         # t.tag is a LangTag
full = str(t.full)
info = t.asdict()           # all the fields as a dictionary of strings
```

See pydoc for details

The first run of an application using this module can take a few seconds as the
module downloads langtags.json from the internet. You can override that and use
a local copy:

```
from langtag import LangTags

langtags = LangTags(fname="local/langtags.json")
t = langtags.get("en-US")
```

The tag sets used here are a formal superset of both those in the IETF registry and in CLDR likelysubtags.xml.
