SLDR = "../sldr/sldr"
FLATDIR = "../sldr/flat"
RESULTS = pub
LTDB = bin/ltdb2alltags
LTROLV = bin/addrolv
LTRFBACK = bin/addfallbacks
NAME = langtags
LTDBOPTS = -H 1

.PHONY : all build test history

all : test

build : ${RESULTS}/${NAME}.json ${RESULTS}/${NAME}.txt # ${RESULTS}/${NAME}_inherited.txt

${RESULTS}/${NAME}.json : source/langtags.csv source/autonyms.csv source/langindex.tab source/rolv.json source/fallbacks.json ${LTDB} ${LTROLV} ${LTRFBACK} | ${RESULTS}
	${LTDB} -i $(SLDR) -f $(FLATDIR) $(LTDBOPTS) -L source/langindex.tab -a source/autonyms.csv $< $@
	${LTROLV} -o temp.json $@ source/rolv.json
	${LTRFBACK} -o $@ temp.json source/fallbacks.json
	@- rm temp.json

${RESULTS}/${NAME}.txt : ${RESULTS}/${NAME}.json | ${RESULTS}
	bin/jsonlangtagstotxt -r -s ${SLDR} $< $@

${RESULTS}:
	mkdir pub

#${RESULTS}/${NAME}_inherited.txt : source/langtags.csv ${LTDB} | ${RESULTS}
#	-${LTDB} -i ${SLDR} -t -p $< $@

test : build
	cd tests ; python3 -m unittest discover 

history : ${RESULTS}/langtag_history.json

${RESULTS}/langtag_history.json : ${RESULTS}/${NAME}.json | ${RESULTS}
	bin/ltdbhistory -a -o $@

