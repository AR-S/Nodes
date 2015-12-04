#!/usr/bin/env python
import time, sys
import serial
import random
import glob
import datetime
import traceback

FRAME_NR = 0
ard = None

index = 0

def find_arduinos():
    return glob.glob('/dev/cu.wchusb*') + glob.glob('/dev/tty.usbserial-*')

def node_bang(addr, tags, stuff, source):
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

def main():
    global ard, DEV_ARDUINO, lastclick
    st = None
    rx = None

    try:
        ards = find_arduinos()
        if len(ards) == 0:
            print "(!!!) Couldn't find any Arduino. Please plug one to continue."
            #sys.exit(2)
        else:
            devard = ards[0]  # get first found
            print "Opening arduino at", devard
            ard = serial.Serial(devard, 57600)

        try:
            node_bang('', '', [11, 1], '') # bang node 11
            time.sleep(0.5)
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
    main()
