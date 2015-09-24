#!/usr/bin/python
"""
This tool can be used to inspect the datafiles.
(cc) 2015 Luis Rodil-Fernandez
"""
import sys, os
import json
import datetime
from pprint import pprint

if len(sys.argv) > 1:
    fname = sys.argv[1]
else:
    fname = 'KRX_009540.json'

last_close = 0
aggregate_close = 0

with open(fname) as fin:
    data = json.loads(fin.read())

    records = len(data['dataset']['data'])

    # print header information
    print '*'*78
    print "CODE: ", data['dataset']['dataset_code']
    print "NAME: ", data['dataset']['name']
    print "DESC: ", data['dataset']['description']
    print "START: ", data['dataset']['start_date']
    print "END: ", data['dataset']['end_date']
    print '*'*78

    print "COLS: ", data['dataset']['column_names']

    idx = 0
    doprint = False
    for quote in data['dataset']['data']:
        variation = float(quote[4]) - last_close
        last_close = float(quote[4])
        aggregate_close += variation

        # print only first and last three quotes
        if idx < 4 or ((records-4) < idx):
            pprint(quote)

        if(idx == 5):
            print "[...]"
            print "[...]"
            print "[...]"

        idx += 1

    # print calculated stats
    print "="*78
    print "Number of quotes:", records
    dtlast = datetime.datetime.strptime(data['dataset']['data'][0][0], '%Y-%m-%d')
    dtfirst = datetime.datetime.strptime(data['dataset']['data'][records-1][0], '%Y-%m-%d')
    dt = dtlast - dtfirst
    print "Tstamp of first quote:", dtfirst
    print "Tstamp of last quote:", dtlast
    print "Time difference:", dt
    print "Avg variability:", 1.0 * aggregate_close / records
    print "="*78
