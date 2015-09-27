#!/usr/bin/python
"""
This tool can be used to inspect the datafiles.
(cc) 2015 Luis Rodil-Fernandez
"""
import sys, os
import json
import glob
import datetime, time
from pprint import pprint
import logging
import math
import serial

NODES = []
FRAME_NR = 0
ard = None

def xmap(val, a, b):
    (a1, a2), (b1, b2) = a, b
    return  b1 + ((val - a1) * (b2 - b1) / (a2 - a1))

get_millis = lambda: int(round(time.time() * 1000))

def find_arduinos():
    return glob.glob('/dev/cu.wchusb*') + glob.glob('/dev/tty.usbserial-*') + glob.glob('/dev/ttyUSB*')

def knock(idx, stat):
    """ send actual knock message to node """
    global ard, FRAME_NR
    if ard:
        cmd = "{0} {1} {2};\r\n".format(stat, idx, FRAME_NR)
        logging.debug("{0} {1} {2};\r\n".format(stat, idx, FRAME_NR))
        #logging.debug("sending: {0}".format(cmd))
        # cmd:on/off  node  frame
        ard.write(cmd)
        FRAME_NR += 1

def cb_knock(addr, tags, stuff, source):
    """ handle bell message from osc server """
    #print "params:", stuff
    idx = stuff[0]
    stat = stuff[1]
    knock(idx, stat)

class LeafNode:
    def __init__(self, idx):
        self.node = idx
        self.current_index = 0
        self.last_quote = 0
        self.last = 0
        # hammer attribs
        self.hammer_last_state = 0
        self.hammer_state = 0
        self.hammer_on_since = 0
        self.hammer_timeout = 500
        self.hammer_sent = False

    def print_headers(self):
        # print header information
        print '*'*78
        print 'NODE NUMBER ', self.node
        print "CODE: ", self.ticker
        print "NAME: ", self.name
        print "DESC: ", self.description
        print "START: ", self.tstamp_start
        print "END: ", self.tstamp_end
        print '*'*78
        print "COLS: ", self.columns

    def print_stats(self):
        records = len(self.quotes)
        last_close = 0
        aggregate_close = 0

        idx = 0
        doprint = False
        for quote in self.quotes:
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
        dtlast = datetime.datetime.strptime(self.quotes[0][0], '%Y-%m-%d')
        dtfirst = datetime.datetime.strptime(self.quotes[records-1][0], '%Y-%m-%d')
        dt = dtlast - dtfirst
        print "Tstamp of first quote:", dtfirst
        print "Tstamp of last quote:", dtlast
        mins = dt.days*24*60
        print "Time difference:", dt, "in minutes:", mins
        recs = xmap(records, (0, mins), (0, self.metronome))
        bpms = ((1.0*recs / self.metronome)*60)
        print "Playback {0} quotes in {1}m ==> {2} qph".format(recs, self.metronome, bpms)
        print "Avg variability:", 1.0 * aggregate_close / records
        print "Metronome:", self.metronome
        print "="*78

    def set_metronome(self, tspan):
        self.metronome = tspan
        logging.info("Setting ".format(self.metronome))

    def load_data(self, datafile):
        self.datafile = datafile
        with open(datafile) as fin:
            data = json.loads(fin.read())

            self.ticker = data['dataset']['dataset_code']
            self.name = data['dataset']['name']
            self.description = data['dataset']['description']
            self.tstamp_start = data['dataset']['start_date']
            self.tstamp_end = data['dataset']['end_date']
            self.columns =  data['dataset']['column_names']
            self.quotes = data['dataset']['data']

    def hammer_hit(self):
        if self.hammer_state == 0:
            self.hammer_last_state = self.hammer_state
            self.hammer_state = 1
            self.hammer_on_since = get_millis()

    def update_hammer(self):
        current = get_millis()
        elapsed = current - self.hammer_on_since
        if (self.hammer_state == 1) and ( elapsed > self.hammer_timeout):
            logging.debug("RELEASE {0} (t={1})".format(self.node, elapsed))
            knock(self.node, 0)
            self.hammer_state = 0
            self.hammer_sent = False
        elif (self.hammer_state == 1) and (self.hammer_last_state == 0) and not self.hammer_sent:
            logging.debug("HIT {0}".format(self.node))
            knock(self.node, 1)
            self.hammer_sent = True

    def update(self):
        current = get_millis()
        self.update_hammer()
        #print (current - self.last)
        if ((current - self.last) > self.metronome):
            self.last = current
            self.current_index += 1
            if(self.current_index > len(self.quotes)):
                logging.warning("RESETTING COUNTER")
                self.current_index = 0
            current_close = self.quotes[self.current_index][4]
            diff = math.fabs(current_close - self.last_quote)
            logging.info("{0} valued at {1}, change {2}".format(self.ticker, current_close, diff))
            self.last_quote = current_close
            self.hammer_hit()


def main():
    global ard, NODES
    with open('mapping.json') as fin:
        data = json.loads(fin.read())
        for n in data['mapping']:
            node = LeafNode(n['node'])
            node.load_data(n['datafile'])
            node.metronome = int(n['metronome'])
            node.hammer_timeout = int(n['hammer'])
            node.print_headers()
            node.print_stats()
            NODES.append(node)


    try:
        # find arduino and connect to it
        ards = find_arduinos()
        print ards
        if len(ards) == 0:
            logging.critical("(!!!) Couldn't find any Arduino. Please plug one to continue.")
            sys.exit(2)

        devard = ards[0]  # get first found
        logging.info("Opening arduino at {0}".format(devard))
        ard = serial.Serial(devard, 57600)

        try:
            pass
            # wait forever
            print "Ctrl+C to stop."
            while 1:
                # update the time loop in each node
                for n in NODES:
                    n.update()
                time.sleep(0.01)
        except KeyboardInterrupt, e:
            print "Good bye!"

    except OSError as e:
        logging.error("(!!!) Failed to open serial pipe. Something's fucky with that Arduino...")
    finally:
        if ard:
            ard.flush()
            ard.close()

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s',
                        datefmt='%d.%m.%Y %I:%M:%S %p',
                        level=logging.DEBUG,
                        filename='playback.log',
                        filemode='w')
    print "Stock market playback machine."
    print "(cc) 2015 Luis Rodil-Fernandez <root@derfunke.net>."
    print
    main()


"""
>>> import datetime
>>> dtlast = datetime.datetime.strptime("2015-3-2", '%Y-%m-%d')
>>> dtfirst = datetime.datetime.strptime("2014-3-2", '%Y-%m-%d')
>>> dt = dtlast - dtfirst
>>> dt
datetime.timedelta(365)
>>> print dt
365 days, 0:00:00
>>> dtdiv5 = dt /5
>>> print dtdiv5
73 days, 0:00:00
>>> 73*5
365
>>> datetime.datetime.now()
datetime.datetime(2015, 9, 26, 15, 22, 23, 313872)
>>> now = datetime.datetime.now()
>>> future = now + datetime.timedelta(0, 840000)
>>> future
datetime.datetime(2015, 10, 6, 8, 42, 34, 59984)
"""
