SLDR = "../sldr/sldr"
FLATDIR = "../sldr/flat"
RESULTS = pub
SOURCE = source
LTDB = bin/ltdb2alltags
LTROLV = bin/addrolv
LTRFBACK = bin/addfallbacks
NAME = langtags
LTDBOPTS = -H 1

.PHONY : all build test history

all : test

build : ${SOURCE}/${NAME}.json ${RESULTS}/${NAME}.txt # ${RESULTS}/${NAME}_inherited.txt

${RESULTS}/${NAME}.json : ${SOURCE}/${NAME}.json | ${RESULTS}
	cp -a ${SOURCE}/${NAME}.json ${RESULTS}/${NAME}.json

${RESULTS}/${NAME}.txt : ${SOURCE}/${NAME}.json | ${RESULTS}
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

