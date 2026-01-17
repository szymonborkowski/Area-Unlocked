/*
Logging data from a GPS module using SD card and Arduino
*/

// Libraries:
#include <SD.h>
#include <SoftwareSerial.h>

// SD Card Shield:
const int chipSelect = 4;  // CS for Arduino Uno Rev3e + seeed studio SD Card Shield v4.4
File coordinateLogs;

// Button for saving to SD card:
const int buttonPin = 2;

// GPS: 
SoftwareSerial gpsSerial(8,7);  // Change to hardware serial when I swap to Mega board
#define PMTK_SET_NMEA_OUTPUT_RMCONLY "$PMTK314,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0*29"
#define PMTK_SET_NMEA_UPDATE_1HZ "$PMTK220,1000*1F"


void setup() {
  while(!Serial);

  // Open serial communications
  Serial.begin(115200);   // Arduino <-> Laptop
  gpsSerial.begin(9600);  // GPS Module <-> Arduino
  delay(2000);            // Allow for opening of serial monitor tool

  if (!SD.begin(chipSelect)) {
    Serial.println("init failed.");
    while (1);
  }
  Serial.println("init done.");

  // Open file and overwrite data if exists
  Serial.println("creating file");
  coordinateLogs = SD.open("coords.txt", O_WRITE | O_CREAT | O_TRUNC);  // limited by 8.3 filename format  

  Serial.println("init gps");
  gpsSerial.println(PMTK_SET_NMEA_OUTPUT_RMCONLY);  // only need RMC sentences for coordinates
  gpsSerial.println(PMTK_SET_NMEA_UPDATE_1HZ);

  attachInterrupt(digitalPinToInterrupt(buttonPin), saveToSD, RISING);  // if button is pressed save data

}

void loop() {
  if (gpsSerial.available()) {
    char c = gpsSerial.read();  // Read stream from GPS
    Serial.write(c);

    // If the file opened okay, write to it:
    if (coordinateLogs) {
      coordinateLogs.print(c);
    } else {
      Serial.println("error opening file");
    }
  }
}

void saveToSD() {
  coordinateLogs.flush();  // Save contents to SD card
  Serial.println("SAVED");
}
