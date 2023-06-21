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

  assignNextCharTo(2); // a
  assignNextCharTo(4); // b
  assignNextCharTo(7); // c
  assignNextCharTo(8); // d
}

void assignNextCharToaabccd(const short pin) {
  if(initializedPins == MAX_PINS){
    return;
  }
  
  pinMode(pin, INPUT_PULLUP);
  
  inputPins[initializedPins++] = pin;
}

void loop() {
  for(int i = 0; i < initializedPins; i++) {
    if(digitalRead(inputPins[i]) == LOW){
      Keyboard.print((char) ('a' + i));
      while(digitalRead(inputPins[i]) == LOW){
        delay(50);
      }
    }
  }
}
