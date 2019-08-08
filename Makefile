SLDR = "../sldr/sldr"
FLATDIR = "../sldr/flat"
RESULTS = pub
LTDB = bin/ltdb2alltags
NAME = langtags

.PHONY : all build test

all : test

build : ${RESULTS}/${NAME}.json ${RESULTS}/${NAME}.txt # ${RESULTS}/${NAME}_inherited.txt

${RESULTS}/${NAME}.json : source/langtags.csv ${LTDB}
	-${LTDB} -i $(SLDR) -f $(FLATDIR) $< $@

${RESULTS}/${NAME}.txt : ${RESULTS}/${NAME}.json
	-bin/jsonlangtagstotxt -r -s ${SLDR} $< $@

#${RESULTS}/${NAME}_inherited.txt : source/langtags.csv ${LTDB}
#	-${LTDB} -i ${SLDR} -t -p $< $@

test : build
	python -m unittest discover -s tests
