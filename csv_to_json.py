import csv
import json

csvfile = open('ste-hya-other-search-pts.csv', 'r')
jsonfile = open('ste-hya-other-search-pts.json', 'w')

fieldnames = ("latitude","longitude")
reader = csv.DictReader( csvfile, fieldnames)
for row in reader:
    json.dump(row, jsonfile)
    jsonfile.write('\n')