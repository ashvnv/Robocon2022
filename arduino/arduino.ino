/*
 * ART
 * Robocon 2022
 *
 * This code is to be uploaded on Arduino Nano which is isolating the Laptop and the main bot controller. The 
 * orientation pins of this arduino can be read to know where to orient the bot. The orientation pins are defined below.
 * The state change pin will complement it's output whenever the orientation pin changes its states.
 * The state pin can be polled or can be used to invoke interrupt.
 */

//State change pin 
const char STATE_PIN = LED_BUILTIN;

//Orientation pin
const char ORIENT_PIN_0 = 2; //lsb
const char ORIENT_PIN_1 = 3;
const char ORIENT_PIN_2 = 4; //msb

const char ORIENT_PIN_3 = 5; //RESERVED


/*<------------------>
 * codes returned when readManv() is called
 * 
 * l - left
 * r - right
 * m - Angle 1 [Ball 1 & 4]
 * n - Angle 2 [Ball 2 & 3]
 * 

 * q - started
 * k - error sent from computer
 * z - computer could not respond within allotted time
 * 
 * 
 * <------------------>
 * Comm codes between linux and arduino
 * a - ack
 * 
 * l - left
 * r - right
 * u - micro left
 * v - micro right
 * m - Angle 1 [Ball 1 & 4]
 * n - Angle 2 [Ball 2 & 3]
 */

//orientation pins [4 pins]. These pins can be used to read the maneuver commands given by object detection program
//pin 4 is reserved for future use
/*
* 0 0 0 0 <- No command
* 0 0 0 1 <- Left
* 0 0 1 0 <- Right
* 0 0 1 1 <- Angle1
* 0 1 0 0 <- Angle2
* 0 1 0 1 <- Reserved
* 0 1 1 0 <- Reserved
* 0 1 1 1 <- Reserved
* 1 0 0 0 <- Reserved
* 1 0 0 1 <- Reserved
* 1 0 1 0 <- Reserved
* 1 0 1 1 <- Reserved
* 1 1 0 0 <- Reserved
* 1 1 0 1 <- Reserved
* 1 1 1 0 <- Reserved
* 1 1 1 1 <- Reserved
*/

#include "SerialTransfer.h"

SerialTransfer myTransfer;

constexpr char manv[] = {'l','r','m','n','u','v'};


void ack(){
  return;
  //ack is skipped to reduce delay
  //myTransfer.packet.txBuff[0] = 'a';
  //myTransfer.sendData(myTransfer.bytesRead);
}



boolean serialAvail(){
  int wait = 0;
  while(!myTransfer.available()){
    if (wait < 7) { //wait multiplier
      delay(100); //wait 100ms 
      wait += 1;
    } else {
      //took too much time to respond
      
      //no command
      digitalWrite(ORIENT_PIN_0, LOW);
      digitalWrite(ORIENT_PIN_1, LOW);
      digitalWrite(ORIENT_PIN_2, LOW);
      
      return false;
    }
  }
  return true;
}

//========================================
int readManv(){
  /*
   * Function will return l,r,m,n
  */
  
  if (!serialAvail()){
    return 'z'; // error code
  }
  
  char temprec = myTransfer.packet.rxBuff[0];
  ack();
  
  switch(temprec) {
             
    case manv[0]: //left
    
                  digitalWrite(ORIENT_PIN_0, HIGH);
                  digitalWrite(ORIENT_PIN_1, LOW);
                  digitalWrite(ORIENT_PIN_2, LOW);
                  
                  return manv[0];

    case manv[4]: //micro left
    
                  digitalWrite(ORIENT_PIN_0, HIGH);
                  digitalWrite(ORIENT_PIN_1, LOW);
                  digitalWrite(ORIENT_PIN_2, LOW);
                  delay(30);
                  digitalWrite(ORIENT_PIN_0, LOW);
                  digitalWrite(ORIENT_PIN_1, LOW);
                  digitalWrite(ORIENT_PIN_2, LOW);
                  
                  return manv[4];
                  
    case manv[1]: //right
                  
                  digitalWrite(ORIENT_PIN_0, LOW);
                  digitalWrite(ORIENT_PIN_1, HIGH);
                  digitalWrite(ORIENT_PIN_2, LOW);

                  return manv[1];
                  
    case manv[5]: //micro right
                  
                  digitalWrite(ORIENT_PIN_0, LOW);
                  digitalWrite(ORIENT_PIN_1, HIGH);
                  digitalWrite(ORIENT_PIN_2, LOW);
                  delay(30);
                  digitalWrite(ORIENT_PIN_0, LOW);
                  digitalWrite(ORIENT_PIN_1, LOW);
                  digitalWrite(ORIENT_PIN_2, LOW);

                  return manv[5];
                  
    case manv[2]: //Angle 1
                  
                  digitalWrite(ORIENT_PIN_0, HIGH);
                  digitalWrite(ORIENT_PIN_1, HIGH);
                  digitalWrite(ORIENT_PIN_2, LOW);
                  
                  return manv[2];
                  
    case manv[3]: //Angle 2
                  
                  digitalWrite(ORIENT_PIN_0, LOW);
                  digitalWrite(ORIENT_PIN_1, LOW);
                  digitalWrite(ORIENT_PIN_2, HIGH);
                  
                  return manv[3];

    default: //error
                  
             digitalWrite(ORIENT_PIN_0, LOW);
             digitalWrite(ORIENT_PIN_1, LOW);
             digitalWrite(ORIENT_PIN_2, LOW);
             
             return 'k';
  }
}


// Important to call this function to discard old manoeuvre command
int start(){
  if (!serialAvail()){
    return 'z'; // error code
  }
  ack();
  return 'q';
}
//=========================================

void setup()
{
  Serial.begin(115200);
  myTransfer.begin(Serial);

  //state change pin. can be polled or used as interrupt pins to know if the state of the orientation pins change
  //This pin's output will complement whenever the state changes.
  pinMode(STATE_PIN, OUTPUT);
  digitalWrite(STATE_PIN, LOW);

  pinMode(ORIENT_PIN_0, OUTPUT);
  digitalWrite(ORIENT_PIN_0, LOW);

  pinMode(ORIENT_PIN_1, OUTPUT);
  digitalWrite(ORIENT_PIN_1, LOW);

  pinMode(ORIENT_PIN_2, OUTPUT);
  digitalWrite(ORIENT_PIN_2, LOW);

  //Reserved PIN
//  pinMode(ORIENT_PIN_3, OUTPUT);
//  digitalWrite(ORIENT_PIN_2, LOW);

  start();
}

//make sure last_state value here is some arbitary char
char last_state = 'x';
char current_state = 's';

void loop()
{ 

  current_state = readManv(); //read orientation state

  if (current_state != last_state) {
    //change in state
    last_state = current_state;
    digitalWrite(STATE_PIN, !digitalRead(STATE_PIN));
  }
  
}
