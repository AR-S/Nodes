import time, sys
import random
from OSC import *
import glob
import serial
import random

bells = []
freqs = [1479, 780, 2000, 1800, 1600]

listen_address = ('192.168.2.5', 2222)

FRAME_NR = 0
ard = None

index = 0

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

def out_test():
    global index
    leafs = [0, 1, 2, 3, 4, 5] #4, 5, 6, 7, 8, 9, 10]
    onoff = [0, 1]
    cb_bell('', '', [leafs[index], random.choice(onoff)], '')
    if index < len(leafs)-1:
        index += 1
    else:
        index = 0;

def main():
    global ard, DEV_ARDUINO
    st = None
    rx = None

    try:
        ards = find_arduinos()
        if len(ards) == 0:
            print "(!!!) Couldn't find any Arduino. Please plug one to continue."
            sys.exit(2)

        devard = [0]  # get first found
        print "Opening arduino at", devard
        ard = serial.Serial(devard, 57600)

        rx = OSCServer(listen_address)
        rx.addDefaultHandlers()
        rx.addMsgHandler("/knock", cb_bell)

        print "Registered Callback-functions:"
        for addr in rx.getOSCAddressSpace():
            print addr

        try:
            print "\nStarting OSCServer. Use ctrl-C to quit."
            st = threading.Thread(target=rx.serve_forever)
            st.thread = True
            st.start()

            # wait forever
            while True:
                #print "boo!"
                out_test()
                time.sleep(1)

        except KeyboardInterrupt, e:
            rx.close() # stop osc server
            print "Good bye!"

    except OSError as e:
        print "(!!!) Failed to open serial pipe. Something's fucky with that Arduino..."
    finally:
        if ard:
            ard.flush()
            ard.close()

if __name__ == '__main__':
    print "OSC to Serial message broker."
    print "(cc) 2015 Luis Rodil-Fernandez <root@derfunke.net>."
    print
    main()
