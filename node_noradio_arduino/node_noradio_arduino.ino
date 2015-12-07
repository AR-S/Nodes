#include <SPI.h>
#include <Metro.h>
#include "printf.h"
#include <CmdMessenger.h>  // CmdMessenger

// !!!!!!!!!!!!!!!!!!!!!
// @CHANGEME: change the value of this variable to change the node address
byte this_node_addr = 11;

// PIN configuration
int outPin = 8;
int ledPin = 7;

enum {
  kNone = 255,
  kEnable = 1,
  kDisable = 0
};

enum {
  stWAITING,
  stRUNNING
};

int state;

long framenr = 0;

char field_separator   = ' ';
char command_separator = ';';

// attach a new CmdMessenger object to the default Serial port
CmdMessenger cmdMessenger = CmdMessenger(Serial, field_separator, command_separator);

// set up roles to simplify testing 
boolean role;                           // The main role variable, holds the current role identifier
boolean role_root = 1, role_leaf = 0;   // The two different roles.

Metro ledmetro = Metro(75); // blinker
Metro solmetro = Metro(500);

int ledState = LOW;
int solState = LOW;

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
  //root_send_message(nodenr, 1);

  // react on command by changing state of pin
  if(this_node_addr == nodenr) {
      solState = HIGH;
      solmetro.reset(); 
  }
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
  //root_send_message(nodenr, 0);

  solState = LOW;
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

  state = stWAITING;

  printf_begin();

  cmdMessenger.printLfCr();
  attachCommandCallbacks();
  
  // pin config
  pinMode(outPin, OUTPUT);
  pinMode(ledPin, OUTPUT);

  payload.state = 0;
  payload.to = 1;

  set_leaf_mode();
  //set_root_mode();
};

void process_payload() {
    // if we were waiting, change state and fix led
    if(state == stWAITING) {
      state = stRUNNING;
      ledState = HIGH;
    }

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
        solState = HIGH;
        solmetro.reset(); 
    } else {
      solState = LOW;
    }
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
//  radio.stopListening();
//  delay(5); // give the radio a (small) chance
//  bool ok = radio.write( &payload, sizeof(Payload) );
//  if(!ok) { Serial.println("send failed"); }
//  radio.startListening(); 
}

void root_test_loop() {
  if(payload.to > 3) {
    payload.to = 0;
  } else {
    payload.to++;
  }
    
  if(payload.state == 0) { payload.state = 1; } else { payload.state = 0; }

  root_send_message(payload.to, payload.state);
  delay(1000); 
}

void set_leaf_mode() {
    role = role_leaf;
}

void set_root_mode() {
    this_node_addr = 255;
    role = role_root;
}

void loop() {
  if((state == stWAITING) && (ledmetro.check() == 1) ) {
    ledState = (ledState == LOW) ? HIGH : LOW;
  }
  digitalWrite(ledPin, ledState);
  
  cmdMessenger.feedinSerialData();

  // prevent the solenoid from staying on for too long
  if( (solState == HIGH) && (solmetro.check() == 1) ) {
    solState = LOW;
  }
  digitalWrite(outPin, solState);
} // loop
