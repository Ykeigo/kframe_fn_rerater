import csv
import sys

args = sys.argv

indexFile = open(args[2], "r")
indexReader = csv.reader(indexFile)

for row in indexReader:
    if row[0].startswith(args[1]):
        print(row[1].zfill(6))