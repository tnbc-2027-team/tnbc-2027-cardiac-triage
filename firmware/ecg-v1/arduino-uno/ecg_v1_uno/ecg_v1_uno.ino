// ECG v1 - Arduino Uno
// Board:   hardware/ecg-schematic-v1 (AD8232 front end, Rev A), header J2 "TO_MCU"
// Wiring:  see ../PINOUT.md
// Author:  Rushil (Electrical), first working version, 2026-11-06
//
// Streams the raw ECG reading over Serial at 115200 baud, one value per line
// (0-1023). Prints '!' instead when an electrode is off (LO+ or LO- high).
// View it with Tools > Serial Plotter in the Arduino IDE.
// Data captured with this sketch: ../../data/

void setup() {
  // initialize the serial communication:
  Serial.begin(115200);

  pinMode(11, INPUT); // Setup for leads off detection LO +
  pinMode(10, INPUT); // Setup for leads off detection LO -

}

void loop() {

  if((digitalRead(10) == 1)||(digitalRead(11) == 1)){
    Serial.println('!');
  }
  else{
    // send the value of analog input 0:
      Serial.println(analogRead(A0));
  }
  //Wait for a bit to keep serial data from saturating
}
