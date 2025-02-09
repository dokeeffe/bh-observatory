/*
 * Very basic firmware to control relay switches
 */
#include <Firmata.h>

const int RELAY_1 =  2;
const int RELAY_2 =  3;
const int RELAY_3 =  4;
const int RELAY_4 =  5;
const int RELAY_5 =  6;
const int RELAY_6 =  7;
const int RELAY_7 =  8;
const int RELAY_8 =  9;

/**
 * Interpret the command string and set the pin state.
 */
void stringCallback(char *myString)
{
  String commandString = String(myString);
  if (commandString.equals("ON1")) {
    digitalWrite(RELAY_1, HIGH);
  } else if (commandString.equals("ON2")) {
    digitalWrite(RELAY_2, HIGH);
  } else if (commandString.equals("ON3")) {
    digitalWrite(RELAY_3, HIGH);
  } else if (commandString.equals("ON4")) {
    digitalWrite(RELAY_4, HIGH);
  } else if (commandString.equals("ON5")) {
    digitalWrite(RELAY_5, HIGH);
  } else if (commandString.equals("ON6")) {
    digitalWrite(RELAY_6, HIGH);
  } else if (commandString.equals("ON7")) {
    digitalWrite(RELAY_7, HIGH);
  } else if (commandString.equals("ON8")) {
    digitalWrite(RELAY_8, HIGH);
  } else if (commandString.equals("OFF1")) {
    digitalWrite(RELAY_1, LOW);
  } else if (commandString.equals("OFF2")) {
    digitalWrite(RELAY_2, LOW);
  } else if (commandString.equals("OFF3")) {
    digitalWrite(RELAY_3, LOW);
  } else if (commandString.equals("OFF4")) {
    digitalWrite(RELAY_4, LOW);
  } else if (commandString.equals("OFF5")) {
    digitalWrite(RELAY_5, LOW);
  } else if (commandString.equals("OFF6")) {
    digitalWrite(RELAY_6, LOW);
  } else if (commandString.equals("OFF7")) {
    digitalWrite(RELAY_7, LOW);
  } else if (commandString.equals("OFF8")) {
    digitalWrite(RELAY_8, LOW);
  }
  Firmata.sendString(myString);
}

void setup()
{
  pinMode(RELAY_1, OUTPUT);
  pinMode(RELAY_2, OUTPUT);
  pinMode(RELAY_3, OUTPUT);
  pinMode(RELAY_4, OUTPUT);
  pinMode(RELAY_5, OUTPUT);
  pinMode(RELAY_6, OUTPUT);
  pinMode(RELAY_7, OUTPUT);
  pinMode(RELAY_8, OUTPUT);
  digitalWrite(RELAY_1, LOW);
  digitalWrite(RELAY_2, LOW);
  digitalWrite(RELAY_3, LOW);
  digitalWrite(RELAY_4, LOW);
  digitalWrite(RELAY_5, LOW);
  digitalWrite(RELAY_6, LOW);
  digitalWrite(RELAY_7, LOW);
  digitalWrite(RELAY_8, LOW);
  Firmata.setFirmwareVersion(FIRMATA_MAJOR_VERSION, FIRMATA_MINOR_VERSION);
  Firmata.attach(STRING_DATA, stringCallback);
  Firmata.begin(57600);
  
}

void loop()
{
  while (Firmata.available()) {
    Firmata.processInput();
  } 
}
