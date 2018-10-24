# Language Tagging

The short URL for this document is:
[*https://goo.gl/LgQfGb*](https://goo.gl/LgQfGb). This document is aimed at
those asked to help maintain the [*SIL Language Tags
list*](https://docs.google.com/spreadsheets/d/121lH-li0w2gOMSaZ2Ac9vZ9TnFPJtldbtCvNvUrkZ0o/edit#gid=738998013).

## Overview

A language tag may be as simple as the three-letter code for the language, or
it may additionally include subtags to indicate the script used to write the
language (if more than one script is used) or the region of the world (country)
where the language is used (if the orthography is different). In the vast
majority of cases, the three letter code is sufficient (for example, "aak" for
Ankave, a language of Papua New Guinea, rather than "aak-Latn-PG" indicating
the Latin script and the country of PNG). Some languages, however, can be
written with multiple scripts (for example, "ahk" for Akha, which can be
written in Latin, Thai or Myanmar scripts) and need multiple language tags
("ahk" for the Latin case, but also "ahk-Thai" and "ahk-Mymr").

A "likely subtags" list serves to "fill in the blanks", having entries that
supply script and region information for each language tag, for example:

|          |             |
|----------|-------------|
| aak      | aak-Latn-PG |
| ahk      | ahk-Latn-MM |
| ahk-Mymr | ahk-Mymr-MM |
| ahk-Thai | ahk-Thai-TH |
| ahk-TH   | ahk-Latn-TH |

As a language tag reviewer, you will be looking at language entries in your
region in order to:

-   make the language tag as short as possible without losing information
-   add entries if additional script or region subtags are needed
-   verify that the "likely subtag" contains the correct script and region
    information for the language tag
-   add your initials in the confirmation column

More details about these tasks are explained in the rest of this document. If
at the end, you still have questions or things are unclear, please add a
comment and the authors will do their best to address it, either directly or by
improving the text.

## Introduction

A language tag is a string made up of subtags separated by -. The string can be
used as an identifier to tag text in a language, or more precisely, a writing
system.

### Structure of a Language Tag

Here we describe the basic structure of a typical language tag. For the full
details and the exceptions see [*BCP47*](https://tools.ietf.org/html/bcp47).
The structure of a language tag is a sequence of subtags (or components) in
order, separated by -. Only the first, language subtag, is required. All other
subtags are optional and are only required if they add distinguishing
information that is needed to clarify the tag sufficiently to make it useful
for what the user is tagging. Yes, this is an ambiguous statement and most of
the rest of the document will address that ambiguity. The order and structure
of each of the subtags is carefully controlled. Here is a tag showing the
various subtags, even if none of them are right, it shows the structure:

```
lng-Scrp-RE-variant-n-ext
```

While language tags are interpreted caseless, there is a convention regarding
casing. Taking each subtag in turn:

-   **Language**. This is an ISO639 code. If a 2-letter code exists from
    ISO639-1 or ISO639-2, then use that, else use the 3 letter code from
    ISO639-3. The subtag is typically lowercase.
-   **Script**. This subtag identifies which script is being used. It is a 4
    letter code and comes from ISO15924. The subtag is typically title case
    with the first letter upper case and the rest lowercase.
-   **Region**. This subtag is used to indicate a writing system or language
    variation based on the region. The region code is 2 letters and comes from
    ISO3166-1 and is typically uppercase.
-   **Variant**. Variants are used to distinguish between dialects that share
    the same language subtag, or orthography variants due to revisions, or
    anything else. The important thing about the variant (which is 5-11 chars and
    typically lowercase) is that it has been registered with the language subtag
    registrar. Private use variants can exist, but they are represented using an
    extension.
-   **Extension**. An extension is prefixed by a single letter namespace code
    followed by whatever subtags make sense within that namespace. There are a
    few namespaces of interest:

    -   -u- is used by CLDR and ICU to identify processing parameters like
        which sort order to use or how linebreaking is done. See UTS\#35 for
        details.

    -   -x- is the private use namespace. Anything after this namespace is
        treated as private use and has no externally defined meaning. This is
        useful for doing initial tagging before variants get registered.

There is one other basic language tag structure and that is the private use
tag. It simply starts with an x- and all subsequent subtags are private use.

### Language Tag Examples

Here we look at some examples:

```
ahk
```

This is a typical tag. It simply consists of a single ISO639-3 code. There is
no need to provide any distinguishing information because there is no
ambiguity. Except in this case there is. So we may want to identify the script
being used:

```
ahk-Latn
```

This tells us the text is in the Akha language using the Latin script. This is
in contrast to the Thai or Burmese script orthographies.

```
ahk-fonipa
```

This tag is common in analysis data. It says that the text is Akha and
represented in the IPA. The fonipa variant implicitly implies that the script
has to be Latn and so no script subtag is required. Such analysis language tags
are not represented in the language tag list because they are not used for
orthographies, only for analysis. This does not reduce their validity, just the
need for any likely subtags associated with them.

While the structure of a language tag is clearly defined, which subtags should
be present in any given situation is not. There is only one piece of community
advice regarding language tagging and that is *tag wisely*. What does this
mean? While there are many cases where things can get complicated, there are a
few basic principles:

### No Redundant Elements

The basic principle is:

Do not add elements to a tag that do not add distinguishing information

This is not saying to minimise the tag, since we also need enough information
in the tag to distinguish it from other tags of data in a different
orthography. But it does mean that for 90% of tags, the tag can consist of just
a single ISO 639 initial element.

But if a tag consists of just the language element, how is an application to
know what the script or region is for text tagged with just the language? A
default region is important to provide good regional locale information. While
a default script may be analysable from the text, it is often preferable to
have knowledge of the intended script before processing the text.

Therefore, it would be helpful if there were some list that specified the
default script and region for any given tag. The CLDR is managing one and calls
the default information the likely subtags for a given tag. SIL is keeping such
a list for the many language tags that it interacts with,
[*here*](https://goo.gl/tI4waT).

## Managing the Language Tags list

The purpose of the SIL Language Tags list is to come up with helpful likely
subtags for any given tag and to know who can act as a point of reference
regarding a tag in the list. The data originates from the Ethnologue and
periodically some resolution will take place, but the list is not master of the
Ethnologue, while it does provide some information the Ethnologue may not have.

### Easy Case

The easy case is where a language group has no dialects, is found in one
primary region and uses only one script and orthography. This is most cases.
Consider aak, Ankave, a language of Papua New Guinea. Given its location, it is
highly unlikely that the likely subtags for the orthography for this language
will be anything other than aak-Latn-PG. And the basic tag need be nothing
other than aak. In checking this, someone would ensure that the Lang\_id field
is simply aak and the likely\_subtag is aak-Latn-PG. Once that is done, the
person would add their registered initials in the confirmed column. More than
one person can confirm the same row and thus if anyone wants to change
information on that row, they should build consensus with anyone else in the
confirmed cell.

It may be that the Lang\_id field has a script subtag in it which is entirely
redundant. This is to be expected. When the data was exported from the
Ethnologue, script subtags were left in, even though they could have been
reasonably removed. The decision was to act conservatively and encourage
confirmers to check their data and remove redundant subtags rather than needing
to add them back in.

#### What about other scripts?

The aim here is to tag orthographies. Thus while linguists may use other
scripts to represent text in the language (for example, Latin romanisations for
non-Roman based orthographies), there is not expected to be any community
standardisation of these romanisations. Therefore there is no need to add an
entry for them. This is particularly true for the -fonipa variant which may be
used on any language and implies Latn script. On the other hand, if there is a
large community and a standardised romanisation for a writing system, then it
may be worth listing the other script, even if it is only used for analysis.
For example, polytonic Greek or Hebrew. The issue of languages with multiple
established orthographies in multiple scripts is covered later.

The Zyyy script is inserted into tags for which there is no known script. If
you know better, please replace Zyyy with the known script, even if it is Qaax
(the script tag for “unwritten”).

It is possible to tag audio, although we use a private use variant for this:
-x-audio. This allows audio text to be treated as just another representation
of a language.

#### Multiple Regions

What if a language is used in multiple countries? The key question is whether
the orthography changes in the other country? If it does, then there should be
another full entry for the other orthography. The question then remains as to
which country is the default region for the basic tag. For the most part, this
is clear. But where it is not, then there may need to be no simple tag and
there needs to be one or more tags each with a region subtag.

What about the list of regions associated with a tag? This list is intended to
give the possible range of values that the region subtag for a given tag, can
take. A country should only be listed if there is an established community of
users of the orthography settled there (or regularly passing through for
nomadic groups). This does not include expatriate or diaspora groups. For
example, there are speakers of many languages in the world living in London,
but that does not mean that there needs to be a -GB type tag for every
language.

#### Unwritten Languages

It is possible, often, to predict what the language tag will be for an
unwritten language. If a confirmer is confident of their prediction, then
please feel free to add the tag entry preemptively. But it helps if the fact
that the language is currently unwritten can be recorded (in the "unwritten"
column). If there is any ambiguity, for example, there is any probability that
a language in a Latin script area may end up being written in Arabic script,
then do not add a script preemptively. Instead use the Qaax script tag to
indicate that the language is as yet unwritten.

### Multiple Scripts

The next most complex situation is where a language is written using different
scripts. In most cases, there is still a primary default script used for a
language and so an entry can be made for the language and the likely\_subtag
can be set to the default script and region. Then for the other scripts, new
rows can be added, one per script.

In the past, it was felt that region drove script: one used Thai script in
Thailand and Khmer script in Cambodia, and therefore the disambiguating
information was the region. The problem is that it doesn't tell you what script
someone in London will use. For this reason, we record script as taking
priority over region. Enough information is recorded that either approach can
be taken, so there is no danger.

For a complex example, consider ahk, Akha. Here is how it is listed in the
language tag list:

|          |             |          |
|----------|-------------|----------|
| ahk      | ahk-Latn-MM | CN MM TH |
| ahk-Mymr | ahk-Mymr-MM | MM       |
| ahk-Thai | ahk-Thai-TH | TH       |
| ahk-TH   | ahk-Latn-TH | TH       |

It can be written in Latn, Thai and Mymr scripts. For the most part it is
written in Latn script and that is what is the default script for ahk. But
there are also entries for the other scripts. The default region is listed for
each script along with all the regions in which there is an established user
group.

Whether there should be an extra entry for ahk-TH depends on what the default
script is in Thailand. If the default script is Thai, then there is no need for
an extra entry since the default region for ahk-Thai is TH and therefore, the
default script for ahk-TH is ahk-Thai-TH. But the default script is Latn, and
we need an entry to resolve the ambiguity and we add ahk-TH as ahk-Latn-TH. For
ahk-MM there are two likely subtags with a region of MM and the default will be
taken as the shorter, i.e. ahk-Latn-MM.

There is one more region of note for ahk and that is CN. CN only occurs in the
list of regions for ahk and therefore ahk-CN is equivalent to ahk-Latn-CN.
There is no need for an extra entry.

Deciding what the default script for a language is, is probably more political
than linguistic. This isn't a question of whether one script is used by 51% of
the population and another by 49%, so picking the winner. The aim is to answer
the question: if I just see the language code as the tag, which script should I
assume is being used? In some cases (for example where there are 2 large
communities using different scripts), it may not be possible to come up with a
default. In which case, don't set one. Just list an entry for each of the
scripts and not one for the language without a script.

### Multiple Orthographies

In addition to the multi-script situation, there are a number of reasons why a
language can end up with multiple orthographies and we discuss some of them
here.

#### Regional Variation

Sometimes a different country uses a different orthography, even though it is
the same script as another country. For example, Zaiwa (atb) is written in
Latin script. The orthography used in Burma is different to that in China. In
this case, we simply acknowledge the fact that atb-MM is different from atb-CN.
We would have two entries in the database for the two regions, whether or not
one of them is the default.

#### Competing Variations

In situations where no orthography has become dominant, for a relatively large
or disparate language group, different orthographies can emerge and become
popular in different regions. Those regions may overlap and not be identifiable
using a region tag. In this case, or for whatever reason there are multiple
established orthographies for a language, we can use a variant to mark the
different orthographies. That still leaves the question of whether one is
considered the default, and that can be a highly political question. It may be
wisest not to specify a default variant for a language in that case and just to
list them all as being equal and required. In politically charged situations
like this, the variant tags need to be carefully chosen as needed by the
situation. There are no a priori limitations or requirements on private use
tags. For standardised tags, there are structural limits as specified in BCP
47.

#### Time Variation

This is probably the most complex tagging issue to address. As an example,
consider the case of German. It underwent an orthography change in 1996. So now
there is the pre-1996 orthography, or traditional German, and the post 1996
orthography. To indicate these two orthographies, there are two variants: -1901
(for traditional German) and -1996 for modern German. This allows someone to
specify precisely which orthography they are talking about, either de-1901 or
de-1996. But what about simple de? Users want de to refer to the default
standard orthography, which is the modern post 1996 one. At some point,
therefore, de needs to switch its default mapping from de-1901 (which didn't
actually exist when de was created) to de-1996.

Moving forward to the present day. If a language is undergoing an orthography
change, then you will want the default orthography for the tag to refer to the
new standard orthography. The question is whether you want to have a tag for
the old orthography. For orthographies in development, the answer is probably
no. Just move on and drop the past, either by updating the data to the new
orthography or acknowledge that the data is now defunct. In the case where the
old orthography was established enough that data in it needs to be kept, then
there is a problem. We can create a variant for it, but the old data needs to
be retagged at some point if it is not to be confused with the modern
orthography. Of course we can also keep it with its old tag and just
acknowledge the ambiguity. In such a case, it is probable that a variant will
be needed for the new orthography, just so that a very clear contrast can be
made. See the Example for Tai Dam later in this document for a worked example.

##### Stable Tagging

For those wanting stable tags, how can they deal with orthography changes?
Let's consider the example of de. The year is 1990 and there is only one tag
for German: de. All data is tagged de. There are no variants and life is
simple. Time passes and it is now 1997. The government has passed the new
orthography and as a result two new tags have been created to indicate the two
orthographies: de-1901 and de-1996. From now on, the simple de tag is
equivalent to de-1996. But all the data we have tagged as de is referring to
de-1901. If, in our data repository, we follow a policy of stable language
tagging, then whenever there is an orthography variant that can be used, it is
used. This means that in 1997 any new data will be tagged de-1996 and never as
de. This means that we can interpret de as de-1901 and probably retag it at the
first opportunity. But at least we know what things mean. What is needed for
this is a mapping from stable ambiguous tags to stable tags. I.e. when we know
that the old orthography is de-1901, we record that and now know what de means,
because using a stable tagging policy we will never tag data in the new
orthography as de.

A stable tagging policy is very attractive, but doesn't fit with the rest of
the industry that says that de means de-1996. Therefore, stable tagging is best
used temporarily. While the stable and unstable tags are the same, there is no
problem. But when an orthography revision occurs, it is best for data held
within a stable tagging environment to be retagged with an unambiguous tag as
soon as possible. Then there is no problem and the data can be tagged unstably
from then on.

A classic example of wanting stable tagging is archiving. Here, only stable
tags should be used and if an orthography revision occurs, ambiguously tagged
data should be retagged and the ambiguous tag never used from then on.
Thankfully, retagging can be an automated process. The key is knowing when
something was tagged. If we know that something was tagged before the tag was
split (or changed), then we know what it means in the new tagging regime for
the orthography. One problem an archive can face is that for emerging
orthographies, there can be many changes made to an orthography before it
stabilises. Again, the date of entry into the archive is key. It is unlikely
that anyone will want to come up with variants for all the provisional
orthographies. It might be worth introducing a variant that says that a
particular data set isn't precisely in the orthography as specified by the non
variant tag. But greater precision than that is probably unwarranted. This just
goes to show that language tagging isn't perfect.

The moral of the story: don't change your orthography! Well don't change it
once it's become well established. But if you have to, there are ways it can be
done, but they are not cost free.

### Confirmation

The next most important column is the confirmed field which contains a list of
initials of people who have expressed an interest in a row. If you have edited
or reviewed a row (would have edited it, but it was correct already) then you
should add your initials there. For those in sensitive areas, the initials do
not actually have to be yours and you can put someone else's email address in
the list of contacts (with their permission) and they can act as the contact
for you. Thus many initials can refer to the same email.

An important set of initials are those of the CLDR. Any row with CLDR in the
confirmed field is highlighted in red and italicised to warn people not to just
edit it. Any changes to the lang\_id and likely\_subtag fields must be agreed
with the CLDR technical committee first. Notice that other columns, including
the regions list, may be edited and your initials added.

### Regions

The regions list, as has been mentioned before, contains a list of all the
countries in which there is an established user community of the orthography.
The list does not need to include expatriate communities, for example in the UK
or USA, although if those communities are big or established enough and are
recognised as such, by the host country, then it is worth adding them. The
regions list is used to resolve the question what script is used for a
language-REGION pair. If there is any ambiguity, then it may be necessary to
add an explicit language-REGION row to resolve the script question. But where a
region is the default region for the correct script of that region, and is not
the default region for any other script, then there is no need for an explicit
entry.

### Dialects

In many cases whether a language variety is a dialect of another language or a
separate language, is clear. In language tagging terms, a dialect is considered
a variant of a language and the tag receives a variant to account for that. But
variants may be used for other things including different orthographies of a
language or dialect. In fact, there is nothing that says a language variant has
to be mutually comprehensible with the non-variant language. As such, language
tags allow for non mutually intelligible dialects. While this does not make
linguistic sense, it can make very good socio-political sense. If a language
group considers itself part of another language group, it may be more
appropriate to treat as a language variant of the main group rather than give
it its own iso639 code, despite what the linguistics might say.

BCP 47 describes how language variants are tagged. There are a number of ways
pertinent to a dialect:

-   A registered variant subtag (5-11 chars long), registered under the
    language with the IETF.
-   A regional variant, identified through the regional subtag.
-   A private use variant under the x- namespace.

Regional variation is exactly the same issue as for regional orthographic
differences. If a dialect is identified with and primarily bound by a country,
then the best way to mark the dialect is through the region subtag. For
example, Singlish is a dialect of English spoken in Singapore and it might be
tagged en-SG. (Although due to its low prestige, people may not want to
identify Singlish as the local form of English). There are lexical and
grammatical differences. Contrast this with en-CA, Canadian English, whose only
difference from British English (or strictly, International English - en-001)
is some calendar differences. A language tag is not constrained by the amount
of difference between variants. The only thing that is important is whether you
can fall back by trimming subtags. Is it acceptable to fall back from en-SG or
en-CA? See BCP 47 for more details on this.

One problem with dialects is akin to that of identifying languages. How does
one know how the dialects are to be grouped or separated? Do we mark each
village as being its own dialect? This cuts to the heart of what a language tag
is. It is a way of identifying two sets of data as being of the same language
variety. Therefore a language tag is only of value to a user community. If
there is no user community for the tag, then there is little point in having
the tag. Further, if a tag is only used by a very small community, who are all
in contact with each other, then there is no real need for a standardised tag.
It is only as the user community grows that standardisation is needed. So while
a tag is only used by a small number of users, it is perfectly adequate to use
private use subtags. While data is being analysed, then tagging to the village
level is fine. It is only once a dialect needs to be tagged more widely that it
needs to be standardised.

A further problem is that while every effort may be made to keep language
tagging from being political, it is often interpreted that way. How dialect
groups consider themselves or other groups can get complicated quickly. As
stated above, the primary subcategorising of language tags is the ability to
fall back to a simpler tag (the tag with the rightmost subtag removed). But
there also needs to be a consensus among the users of a language tag of what
the tag should be. This agreement includes appropriateness. One of the
difficulties is that there needs to be a language variety that is the
non-variant language. But it may not be possible to choose one. One approach is
to, in effect, invent a dialect that is the most accessible given all the
dialects will fall back to it. But this is far from ideal. Another option is to
make the unmarked language empty. This makes more sense in theory, but may be
pragmatically more frustrating. But at that point, agreed common elements can
be transferred from all the dialects into the language.

But it may be that all this discussion of variants does not help a particular
language. It really is a different language and it really needs an ISO-639 code
so that it can be tagged. In that case, an important part of developing a tag
is deciding on the language part of the tag. Information on how to apply for a
iso 639-3 code can be found
[*here*](http://www-01.sil.org/iso639-3/submit_changes.asp#Submitting). The
process can be quite slow and so those thinking whether they need to apply are
encouraged to do so earlier rather than later.

### Audio/Video

Language tags were originally envisaged for marking text. The need to mark
non-textual media has grown, and thankfully there is a script tag for such
data: Zxxx. One convention has grown up for marking audio data using
-Zxxx-x-audio. But strictly speaking the -x-audio is unnecessary since for
written text, the assumption is that the unwritten form will be audio. The key
exception to this is sign languages, where the default clearly needs to be
video (-Zxxx-x-video). But a simple tag involving Zxxx is insufficient to tell
an application what the tagged data actually is. There is the whole encoding
question (including container formats and codecs) which calls for extra
information somewhere. While this could be encoded in the language tag, it is
more easily handled as extra meta-data. It is unhelpful to encumber a language
tag with encoding information since the tag may be used to tag different sets
of data, differently encoded and then tag matching will fail.

On this basis, any information in the -x- such as -x-audio can only be
considered advisory and should not be keyed off to define whether an element is
audio or video. The data encoding information tells whether it is audio or
video. If there is a context where both audio and video data sets are present
for the same language, an -x- subtag can be used to add some differentiation,
just to make the two tags different in some way.

### Timing

The good news in all this complexity is that time is on our side. It is
possible to wait and to see how things will work out. Standardisation struggles
with change and it can be costly. It is often better to wait until things
stabilize so that the resulting tags will last. We do not want to have the
meaning of a tag to change, otherwise previously tagged data needs to be
retagged.

### Procedure

Having walked through all the issues involved in tagging, this section gives an
overview procedure for reviewing a row in the spreadsheet.

-   Is this the default script for the language? Then remove the script element
    from the Lang\_id. For example, in single script regions, it is very
    unlikely a language will have an orthography in another script.
-   Make sure the appropriate region and script are used in the likely\_subtag.
-   Check the langname and check the script corresponds to the likely\_subtag.
-   Ensure the regions list reflects the particular tag rather than the whole
    language. Is the script used in that region. A language script may not be
    used in all regions.
-   The default region reflects the likely\_subtag.
-   Indicate whether the language is unwritten or unused now
-   Areas is helpful for filtering. Iso639 corresponds to the main language
    part of the lang\_id
-   Add your initials to the confirmed, so that you will be included in any
    future changes
-   Date the change, please.

## Extra Information

The SLDR, in addition to keeping the language tags database (eventually), also
has other files that help with language tag processing.

### Alltags.txt

This file consists of a set of language tags equivalence sets, one per line. A
language tag equivalence set consists of all the tags that are considered
equivalent. Thus, due to the likely subtags list, en = en-Latn = en-US =
en-Latn-US. There are a few key characteristics of the way an equivalence set
is listed. The first element in the list is considered the preferred short tag.
The last element in the list is considered the preferred long tag. Everything
in between is considered simply equivalent. In addition, all tags for which
there is a directly referenced file in the SLDR are listed with a \* prefix. If
a set has more than one tag marked in this way, then the files are considered
equivalent by inheritance, differing only in their identity block, and you can
use any of them. The earliest starred tag in the list points to the most
generic (and most inherited from) file and the last, the most specific.

## Examples or FAQ

### Tai Dam

Here's a hypothetical issue. Start with the current state of Tai Dam. The
language code is blt. It uses three scripts, so that gives us blt-Tavt,
blt-Laoo, and blt-Latn. It would be reasonable to make blt-Tavt the default, so
for it we just use blt. Now for blt-Laoo, we actually have two orthographies,
the original dating from 1977, and a revised orthography dating from 2013. We
have data in print and electronic form in both versions. I'm not sure how that
is added to a tag, but it might give you something like blt-Laoo-1977 vs
blt-Laoo-2013. The 2013 version would be the default, since it's the current
version. So that gives us:

```
blt = blt-Tavt
blt-Laoo = blt-Laoo-x-2013
blt-Laoo-x-1977 = blt-Laoo-x-1977
blt-Latn = blt-Latn
```

So we adopt those. Then suppose that in 2020 someone comes up with a really
great solution for how to handle the ambiguities that exist in the Lao
orthography (I'd really love to see this happen), and we revise it again. Now
we have blt-Laoo-x-2020.

Does the default for blt-Laoo now change to blt-Laoo-x-2020? And if so, what
happens to older data that used the blt-Laoo tag?

Yes, this is a nasty situation and the current understanding (this answer may
change) is that at some point, once blt-Laoo-x-2020 has become established and
people want the default orthography to be the new orthography, the default
mapping gets changed. But how dare they? Doesn't that invalidate all the old
data? Actually no. While the likely subtags for a given tag specifies a
particular orthography, that is not the same as saying that someone who tags
using blt-Laoo is effectively tagging as blt-Laoo-x-2013 (or whatever the
current mapping is). They are actually tagging saying: this text is in blt-Laoo
and I am not specifying which particular orthography is in use. That
information is ambiguous at that point. It is only the application of other
processes that try to resolve that ambiguity. That they might resolve it wrong,
is not really their fault. If you want precise tagging, then use a precise tag
and always tag with the variant.

This does raise the question that if you tag something blt-Laoo-x-2013, is a
process that rewrites the data, at liberty to simplify the tag back to
blt-Laoo? The above answer implies that that should not happen. **Applications
should endeavour to rewrite data with the same tag with which it was originally
tagged.**

### Registry of Dialects

The Registry of Dialects (ROD), managed by Global Recordings is a valuable
resource. It provides a central registry of dialects for a language so that
users can refer to the same thing. It does much of what language tags aim to do
in providing a common identifier. But the relationship between a dialect
identifier in the ROD is not obvious. Some dialects are regional variants. Some
are actually the same dialect (due to early registration before the dialect map
is complete). This is not a problem for what the ROD was developed to do. But
it does seem to preclude the ROD from being turned into a simple namespace for
dialect variants. It would probably be unhelpful to allocate a namespace to it,
as in -r-rod1347. Instead the most helpful approach would be to provide a map
from the ROD to language tags. Since there is no hurry to provide this map, the
ROD provides an excellent first step towards a more stable set of language tags
for the dialects of a language.

### When to add a script

A small language, Qabiao \[laq\] in Vietnam has no record of being written, but
a contact has just informed me of two resources in the language using the
Vietnamese script. When is it appropriate to add a script to a language?

The ideal criteria for adding a script to a language are:

-   The script is available and the orthography supported by Unicode
-   The orthography is established and there is a user community using it such
    that it isn't going to disappear soon and probably not change that much.

The problem is that while the first criterion is easy to meet, the second is
trickier to decide when an orthography is mature. Having said that, there is
nothing to stop us saying that say: laq-Latn is the whole range of
orthographies that are currently being used in the Latin script for the
language. This would apply up until the point that after being established with
significant long lasting literature, the orthography then changes. At this
point we would need to add a variant for the old established orthography and a
variant for the new orthography. But that is waaay down the road. It may also
be that with a dying language, no orthography ever gets established. But then
it's probably a case of last orthography standing.

One advantage of a small language group is that it is much easier for an
orthography to become established. Mind you it only takes 2 people to have an
argument! I would be surprised if this language were written in anything other
than Latin script, being in Vietnam. So adding a Latn script to the language
isn't a long stretch. And we can assume it will be the default. But these
assumptions, are risky. The only reason for proceeding is that we consider the
risk to be low due to the language group being in a single script region.

So we could add an entry laq = laq-Latn-VN with a high degree of confidence. If
the situation does change, then, again the size of the group and the fluid
sociolinguistic situation means that there is unlikely to be a lot of wrongly
tagged data should the mapping change and they suddenly switch to using Khmer
script or somesuch.

### Macro Languages

or: Why does the CLDR insist on treating cmn as zh?

ISO 639-3 was developed to address the many languages that are in the world.
Previously, there was ISO 639-2 which allowed for new languages only if there
was a corpus of 50 publications in the language. In addition, language codes
were not allocated very precisely. So there was a language code (qu) for
'quechua', even though there are some 34 individual languages that call
themself a quechua language. In order to not break existing tags, ISO 639-3
took in the existing ISO 639-2 codes and created a category: macro language for
them. The result has been a cause of confusion ever since.

One approach to resolving the mess is taken by the CLDR. They establish an
equivalence between the macro language and one of the languages within the
cluster. So for qu they chose quz (Cusco Quechua). They then convert any
occurrence of the lead language into the macro language. Thus quz gets
converted to qu. They do this for backward compatibility, rather than the other
way around. Likewise cmn gets converted to zh. More information on how CLDR
normalizes its tags can be found in
[*UTS\#35*](https://unicode.org/reports/tr35/tr35.html#BCP_47_Language_Tag_Conversion)
and
[*here*](http://cldr.unicode.org/index/cldr-spec/picking-the-right-language-code).

Question: Do we extend alltags to include the macro language equivalents? Thus:

```
*zh = zh-CN = *zh-Hans = cmn = cmn-Hans = cmn-Hans-CN = *zh-Hans-CN

zh-TW = *zh-Hant = cmn-Hant = cmn-TW = cmn-Hant-TW = *zh-Hant-TW
```

