// nRF24 wiring.
//     CE       -> 9
//     SS       -> 10
//     MOSI     -> 11
//     MISO     -> 12
//     SCK      -> 13
#include <SPI.h>
#include "nRF24L01.h"
#include "RF24.h"
#include "printf.h"
#include <CmdMessenger.h>  // CmdMessenger

////#define LEAF
//#define ROOT

byte this_node_addr = 2;

// PIN configuration
int outPin = 8;
int ledPin = 7;

long framenr = 0;

char field_separator   = ' ';
char command_separator = ';';

enum {
  kNone = 255,
  kEnable = 1,
  kDisable = 0
};

// Attach a new CmdMessenger object to the default Serial port
CmdMessenger cmdMessenger = CmdMessenger(Serial, field_separator, command_separator);

// RADIO setup
// Pin 9 is CE and 10 CSN/SS
RF24 radio(9,10);
const uint64_t pipes[2] = {0x65646f4e32LL,0x65646f4e31LL};

// Set up roles to simplify testing
boolean role;                           // The main role variable, holds the current role identifier
boolean role_root = 1, role_leaf = 0;   // The two different roles.

struct Payload {
  byte from;
  byte to;
  byte ack;
  byte cmd;
  byte state;
};

Payload payload;

// /////////////////////////////////////
// HANDLERS
void on_enable() {
  int nodenr = cmdMessenger.readInt16Arg();
  int frame = cmdMessenger.readInt16Arg();
  if(frame != framenr+1) {
    Serial.print("Skipped ");
    Serial.print(frame - framenr);
    Serial.println(" frames");
  }
  framenr = frame;
  root_send_message(nodenr, 1);
}

void on_disable() {
  int nodenr = cmdMessenger.readInt16Arg();
  int frame = cmdMessenger.readInt16Arg();
  if(frame != framenr+1) {
    Serial.print("Skipped ");
    Serial.print(frame - framenr);
    Serial.println(" frames");
  }
  framenr = frame;
  root_send_message(nodenr, 0);
}

void on_unknown() {
  Serial.println("Command unknown");
}

void attachCommandCallbacks() {
  cmdMessenger.attach(kEnable, on_enable);
  cmdMessenger.attach(kDisable, on_disable);
  cmdMessenger.attach(on_unknown);
}

// /////////////////////////////////////
// Arduino
void setup(void) {
  Serial.begin(57600);

  printf_begin();

  cmdMessenger.printLfCr();
  attachCommandCallbacks();

  // pin config
  pinMode(outPin, OUTPUT);
  pinMode(ledPin, OUTPUT);

  // radio config
  radio.begin();
  radio.setChannel(0x4c);
  radio.setAutoAck(1);
  radio.setRetries(15,15);
  //radio.setPayloadSize(sizeof(Payload));

  payload.state = 0;
  payload.to = 1;

  set_leaf_mode();
  //set_root_mode();

  radio.startListening();
  radio.printDetails();
  radio.powerUp();
};

void process_payload() {
    Serial.println("[RX] ");
    Serial.print("   FROM=");
    Serial.print(payload.from);
    Serial.print(" TO=");
    Serial.print(payload.to);
    Serial.print(" CMD=");
    Serial.print(payload.cmd);
    Serial.print(" STAT=");
    Serial.print(payload.state);
    Serial.println();

    // react on command by changing state of pin
    if(payload.state == 1) {
        digitalWrite(outPin, HIGH);
        delay(200);
        digitalWrite(outPin, LOW);
    } else {
      digitalWrite(outPin , LOW);
    }
}

void leaf_loop() {
  if (radio.available()){
    Serial.println("got message");
    while (radio.available()) {
      radio.read( &payload, sizeof(Payload) );

      // if message is destined to us or everyone, process it, otherwise ignore
      if((payload.to == 0) || (payload.to == this_node_addr)) {
        process_payload();
      } else {
        Serial.print("Message wasn't meant for me: TO=");
        Serial.print(payload.to);
        Serial.println();
      }
    } // while
  } // if data
}

void root_send_message(uint8_t dstnode, uint8_t state) {
  // compose message
  payload.from = this_node_addr;
  payload.to = dstnode; // TO=0 ==> all nodes
  payload.ack = 0;
  payload.state = state;

  // print message
  Serial.print("[TX]");
  Serial.print(" FROM=");
  Serial.print(payload.from);
  Serial.print(" TO=");
  Serial.print(payload.to);
  Serial.print(" STAT=");
  Serial.print(payload.state);
  Serial.println();

  // dispatch message
  radio.stopListening();
  delay(10);
  bool ok = radio.write( &payload, sizeof(Payload) );
  if(!ok) { Serial.println("send failed"); }
  delay(10);
  radio.startListening();
  delay(1000);
}

void root_loop() {
  if(payload.to > 3) {
    payload.to = 0;
  } else {
    payload.to++;
  }

  if(payload.state == 0) { payload.state = 1; } else { payload.state = 0; }

  root_send_message(payload.to, payload.state);
}

void set_leaf_mode() {
    role = role_leaf;
    radio.openWritingPipe(pipes[1]);
    radio.openReadingPipe(1, pipes[0]);
}

void set_root_mode() {
    this_node_addr = 255;
    role = role_root;
    radio.openWritingPipe(pipes[0]);
    radio.openReadingPipe(1,pipes[1]);
}

void loop() {
  // determine which loop to run
  if(role == role_leaf) {
    leaf_loop();
  } else if (role == role_root) {
    // Process incoming serial data, and perform callbacks
    cmdMessenger.feedinSerialData();
    //root_loop();
  } else {
    Serial.println("undefined role for this node");
  }

  // we are online, light LED
  digitalWrite(ledPin, HIGH);
/*
  // check for any incoming serial data
  if ( Serial.available() )
  {
    char c = toupper(Serial.read());
    if ( (c == 'R') && (role == role_leaf) )
    {
      Serial.println("*** Changing to ROOT role -- PRESS 'L' TO SWITCH BACK\n\r");
      set_root_mode();
    }
    else if ( (c == 'L') && (role == role_root) )
    {
      Serial.println("*** Changing to LEAF role -- PRESS 'R' TO SWITCH BACK\n\r");
      set_leaf_mode();
    }
  } // if serial available
*/
} // loop
