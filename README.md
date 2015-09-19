## Broker
(cc) 2015 Hrvoje Hirsl & Luis Rodil-Fernandez

Code for the installation at Dortyart Sept 2015.

## Some technical notes

The installation needs several components to be working simultaneously and talking to each other in the following way:

GUI  -> broker.py -> arduino nano -> solenoid nodes

### Order of things

1. the **root** node must be plugged to the USB port of the controller computer, be it a laptop or a Rpi. Make sure that the **root** nano is plugged first.
2. Run the **broker.py** script.
3. Load the puredata interface.

At this point your *leaf* nodes should be powered and up, but this can happen before or after, it doesn't matter so much.

## Running the broker

To run the broker, open a terminal, go to the directory where the broker.py script is and type `python broker.py`. To change directories in the terminal's command line you can use the `cd <dir>` command, where `<dir>` is the directory you want to change to.

The python script will start listening on port 2222 on the localhost.


## Troubleshooting
Some problems and how to fix them.

#### I can run the broker.py but when I try to connect from the puredata sketch it fails with this message *error: udpsend: not connected*.
This means that the network connection between the puredata GUI and the broker.py script couldn't be opened. This is almost certainly the IP number. Check that the "connect" message in the puredata GUI, says: *"connect localhost 2222"*. And verify that the python script is also listening on that address/port. Open the script with a plain text editor and go to the line that reads `listen_address = (‘localhost', 2222)` and make sure it has the word "localhost" in it instead of an IP address.

#### How do I find my IP address?

If you are on OSX, you can open a tool called "Network Utility" and you can see your IP there.
