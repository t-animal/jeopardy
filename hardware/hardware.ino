/*
  Keyboard test

  For the Arduino Leonardo, Micro or Due

  Reads a byte from the serial port, sends a keystroke back.
  The sent keystroke is one higher than what's received, e.g. if you send a,
  you get b, send A you get B, and so forth.

  The circuit:
  - none

  created 21 Oct 2011
  modified 27 Mar 2012
  by Tom Igoe

  This example code is in the public domain.

  http://www.arduino.cc/en/Tutorial/KeyboardSerial
*/
#include <Keyboard.h>

static const byte NOT_CONFIGURED = 255;
static const byte MAX_PINS = 'z' - 'a';

byte inputPins[MAX_PINS];
byte initializedPins = 0;

void setup() {
  Serial.begin(9600);
  Keyboard.begin();

  for(int i = 0; i < MAX_PINS; i++) {
    inputPins[i] = NOT_CONFIGURED;
  }

  setupPair(0, 1);
  setupPair(2, 3);
  setupPair(4, 5);
  setupPair(6, 7);
  setupPair(8, 9);
  setupPair(10, 11);
  setupPair(12, 13);
}

void setupPair(const short pinA, const short pinB) {
  if(initializedPins == MAX_PINS){
    return;
  }
  
  pinMode(pinA, INPUT_PULLUP);
  pinMode(pinB, OUTPUT);
  digitalWrite(pinB, LOW);
  
  inputPins[initializedPins++] = pinA;
}

void loop() {
  for(int i = 0; i < initializedPins; i++) {
    if(digitalRead(inputPins[i]) == LOW){
      Keyboard.print((char) ('a' + i));
    }
  }
}
