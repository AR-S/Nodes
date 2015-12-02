import time, sys
import serial
import random
import urllib2
import glob
import csv
import StringIO
import datetime
import traceback

FRAME_NR = 0
ard = None

index = 0
lastclick = None

def find_arduinos():
    return glob.glob('/dev/cu.wchusb*') + glob.glob('/dev/tty.usbserial-*')

def cb_bell(addr, tags, stuff, source):
    """ Handle bell message from eternal controller """
    global ard, FRAME_NR
    #print "params:", stuff
    idx = stuff[0]
    stat = stuff[1]
    if ard:
        cmd = "{0} {1} {2};\r\n".format(stat, idx, FRAME_NR)
        print "sending: ", cmd
        # cmd:on/off  node  frame
        ard.write(cmd)
        FRAME_NR += 1

def get_last_row(csvreader):
    for line in csvreader:
        lastline = line
    return lastline

def poll_clicks():
    sys.stdout.write('.')
    sys.stdout.flush()

    response = urllib2.urlopen('http://www.butttton.com/lastclicks.txt')
    data = response.read()
    return data
    # with open('data.txt') as f:
    #     data = f.read()
    #     f.close()
    #
    #     return data

def main():
    global ard, DEV_ARDUINO, lastclick
    st = None
    rx = None

    try:
        ards = find_arduinos()
        if len(ards) == 0:
            print "(!!!) Couldn't find any Arduino. Please plug one to continue."
            sys.exit(2)

        devard = ards[0]  # get first found
        print "Opening arduino at", devard
        ard = serial.Serial(devard, 57600)

        try:
            while True:
                data = poll_clicks()
                reader = csv.reader(StringIO.StringIO(data), csv.excel)
                row = get_last_row(reader)

                dt = datetime.datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
                if lastclick:
                    if lastclick < dt:
                        print( "\nNew click detected [{0}]".format(dt) )
                        lastclick = dt
                        cb_bell('', '', [11, 1], '') # activate node 11
                else:
                    lastclick = dt

                time.sleep(1)
        except KeyboardInterrupt, e:
            print "Good bye!"
        except Exception, e:
            print(traceback.format_exc())
            pass

    except OSError as e:
        print "(!!!) Failed to open serial pipe. Something's fucky with that Arduino..."
    finally:
        if ard:
            ard.flush()
            ard.close()

if __name__ == '__main__':
    print "Pool for remote clicks."
    print "(cc) 2015 Luis Rodil-Fernandez <root@derfunke.net>."
    print
    main()
