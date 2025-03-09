#include <Servo.h>
#include <Wire.h>
#include <SPI.h>

Servo armL;  
Servo armR;  

#define L 76
#define R 82
#define l 108
#define r 114
#define D 68
#define U 85

int arm = -1;
int top = 180;
int bot = 0;

void setup() {
  Serial.begin(9600);

  pinMode(13,OUTPUT);
   
  armL.attach(9);  
  armR.attach(10); 
  armL.write(bot);
  armR.write(top);
}


void loop() {

   if (Serial.available() > 0) {

      arm = Serial.read();

      switch(arm){
        case R:
          armR.write(top);
          break;
        case L:
          armL.write(bot);
          break;
        case r:
          armR.write(bot);
          break;
        case l:
          armL.write(top);
          break;
        case D:
          armL.write(bot);
          armR.write(top);
          break;
        case U:
          armL.write(top);
          armR.write(bot);
          break;
        default:
          break;
        
      }

   }
}