/*
 * ART
 * Robocon 2022
 * 
 * This file contains functions to be called by the main controller for automation.
 */

const char ORIENT_PIN_0 = A3;
const char ORIENT_PIN_1 = A2;
const char ORIENT_PIN_2 = A1;
const char ORIENT_PIN_3 = A0; // Reserved pin

void setup() {
  
  pinMode(ORIENT_PIN_0, INPUT_PULLUP);
  pinMode(ORIENT_PIN_1, INPUT_PULLUP);
  pinMode(ORIENT_PIN_2, INPUT_PULLUP);
  
  //Reserved pins;
  //pinMode(ORIENT_PIN_3, INPUT_PULLUP);
  //-------------------------
  
}

void inAutoMode(){
  
  while (true){ //placeholder while loop
      
    if ((analogRead(ORIENT_PIN_2) < 500) && (analogRead(ORIENT_PIN_1) < 500) && (analogRead(ORIENT_PIN_0) > 500)) {
      //ANTICLOCKWISE ROTATE

    }
    else if (analogRead(ORIENT_PIN_2) < 500 && analogRead(ORIENT_PIN_1) > 500 && analogRead(ORIENT_PIN_0) < 500) {
      //CLOCKWISE ROTATE

    }
    else if (analogRead(ORIENT_PIN_2) < 500 && digitalRead(ORIENT_PIN_1) > 500 && analogRead(ORIENT_PIN_0) > 500) {
      //ANGLE 1 [BALL 1 and 4]
    }
    else if (analogRead(ORIENT_PIN_2) > 500 && (analogRead(ORIENT_PIN_1) < 500) && (analogRead(ORIENT_PIN_0) < 500)) {
      //ANGLE 2 [BALL 2 and 3]
    }
    
  }
}

void loop() {
}
