#!/usr/bin/env python3

import argparse, csv

parser = argparse.ArgumentParser()
parser.add_argument("infile")
parser.add_argument("outfile")
parser.add_argument("-d","--delete",action="append",help="Delete this column, after appends")
parser.add_argument("-a","--append",action="append",help="Append index=name column")
args = parser.parse_args()

appends = [x.split("=") for x in args.append]
with open(args.infile) as csvfile, open(args.outfile, "w") as outfile:
    reader = csv.DictReader(csvfile)
    fnames = reader.fieldnames[:]
    for i, n in sorted(appends, key=lambda x:(-int(x[0]), x[1])):
        fnames.insert(int(i), n)
    for d in args.delete:
        del fnames[fnames.index(d)]
    writer = csv.DictWriter(outfile, fnames)
    writer.writeheader()
    for row in reader:
        for i, n in appends:
            row[n] = ""
        for d in args.delete:
            del row[d]
        writer.writerow(row)

