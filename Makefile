SLDR = "../sldr/sldr"
RESULTS = results
LTDB = bin/ltdb2alltags
NAME = langtags

.PHONY : all build test

all : test

build : ${RESULTS}/${NAME}.json ${RESULTS}/${NAME}.txt # ${RESULTS}/${NAME}_inherited.txt

${RESULTS}/${NAME}.json : source/langtags.csv ${LTDB}
	-${LTDB} -i $(SLDR) $< $@

${RESULTS}/${NAME}.txt : source/langtags.csv ${LTDB}
	-${LTDB} -i ${SLDR} -t $< $@

#${RESULTS}/${NAME}_inherited.txt : source/langtags.csv ${LTDB}
#	-${LTDB} -i ${SLDR} -t -p $< $@

test : build
	pytest
