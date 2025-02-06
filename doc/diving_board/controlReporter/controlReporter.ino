#include <Encoder.h>

Encoder e1(2, 3);
Encoder e2(4, 5);
Encoder e3(6, 7);
Encoder e4(8, 9);
Encoder e5(10, 11);

void setup() {
  Serial.begin(9600);//Write to console- number (9600) = baud rate
}

int controls[] = {A0,A1,A2,A3,A4,A5,A6,A7};
int encVals[] = {0,0,0,0,0};
int oldValues[] = {0,0,0,0,0,0,0,0,0,0,0,0,0};
//int testValues[] = {0,0,0,0,0,0,0,0,0,0,0,0,0};
int tries = 0;
void loop() {
  for (int a = 0; a < 8; a++){
    if ((analogRead(controls[a]) > oldValues[a]+10) || (analogRead(controls[a]) < oldValues[a]-10)){
      Serial.print(",");
      Serial.print(a);
      Serial.print(",");
      Serial.print(analogRead(controls[a]));
      Serial.println(",");
      oldValues[a] = analogRead(controls[a]);
    }
  }

  encVals[0] = e1.read();
  encVals[1] = e2.read();
  encVals[2] = e3.read();
  encVals[3] = e4.read();
  encVals[4] = e5.read();

  for (int b = 0; b < 3; b++){
    if (encVals[b] > oldValues[b+8]){
      Serial.print(",");
      Serial.print(b+8);
      Serial.println(",+,");
      oldValues[b+8] = encVals[b];
    }
    else if (encVals[b] < oldValues[b+8]){
      Serial.print(",");
      Serial.print(b+8);
      Serial.println(",-,");
      oldValues[b+8] = encVals[b];
    }
  }
}
