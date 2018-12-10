SLDR = "../sldr/sldr"
RESULTS = results

.PHONY : all

all : ${RESULTS}/alltags.json ${RESULTS}/alltags.txt ${RESULTS}/alltags_inherited.txt

${RESULTS}/alltags.json : source/langtags.csv
	-bin/ltdb2alltags -i $(SLDR) $< $@

${RESULTS}/alltags.txt : source/langtags.csv
	-bin/ltdb2alltags -i ${SLDR} -t $< $@

${RESULTS}/alltags_inherited.txt : source/langtags.csv
	-bin/ltdb2alltags -i ${SLDR} -t -p $< $@
