The **broker.py** is a simple message forwarding broker that receives messages in the OSC protocol through a network connection and pumps those messages through the *serial* interface to an Arduino that then broadcasts them through radio.

**broker.py** must be running and listening on the `localhost` address on port `2222` in order to do its job.
