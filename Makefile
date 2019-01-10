SLDR = "../sldr/sldr"
RESULTS = results
LTDB = bin/ltdb2alltags

.PHONY : all

all : ${RESULTS}/alltags.json ${RESULTS}/alltags.txt ${RESULTS}/alltags_inherited.txt

${RESULTS}/alltags.json : source/langtags.csv ${LTDB}
	-${LTDB} -i $(SLDR) $< $@

${RESULTS}/alltags.txt : source/langtags.csv ${LTDB}
	-${LTDB} -i ${SLDR} -t $< $@

${RESULTS}/alltags_inherited.txt : source/langtags.csv ${LTDB}
	-${LTDB} -i ${SLDR} -t -p $< $@
