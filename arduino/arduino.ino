#include <Adafruit_Fingerprint.h>
#include <SoftwareSerial.h>

// Software serial for the fingerprint sensor
SoftwareSerial mySerial(2, 3); // RX, TX
Adafruit_Fingerprint finger = Adafruit_Fingerprint(&mySerial);

// Software serial for Bluetooth module
SoftwareSerial bluetooth(4, 5); // RX, TX

// Operation modes
#define MODE_IDLE 0
#define MODE_REGISTER 1
#define MODE_VERIFY 2

int currentMode = MODE_IDLE;
String userData = "";

void setup() {
  Serial.begin(9600);
  bluetooth.begin(9600); // Instead of 9600
  
  // Set the data rate for the sensor serial port
  finger.begin(57600);
  
  if (finger.verifyPassword()) {
    Serial.println("Fingerprint sensor connected!");
  } else {
    Serial.println("Fingerprint sensor not found!");
    while (1) { delay(1); }
  }
}

void loop() {
  if (bluetooth.available()) {
    String command = bluetooth.readStringUntil('\n');
    command.trim();
    
    Serial.println("Received Command from Flask: " + command);  // ✅ Debugging line

    if (command.startsWith("REGISTER:")) {
      currentMode = MODE_REGISTER;
      userData = command.substring(9);
      Serial.println("Register mode activated for: " + userData);
      bluetooth.println("READY_TO_REGISTER");  // ✅ Confirm sending this back
    } 
    else if (command.equals("VERIFY")) {
      currentMode = MODE_VERIFY;
      Serial.println("Verify mode activated.");
      bluetooth.println("READY_TO_VERIFY");  // ✅ Confirm sending this back
    } 
    else {
      Serial.println("Unknown Command Received: " + command);  // ✅ Debugging line
    }
  }
}


// Function to enroll a new fingerprint
bool getFingerprintEnroll() {
  int p = -1;
  Serial.println("Waiting for valid finger to enroll");
  
  while (p != FINGERPRINT_OK) {
    p = finger.getImage();
    switch (p) {
      case FINGERPRINT_OK:
        Serial.println("Image taken");
        break;
      case FINGERPRINT_NOFINGER:
        return false;
      case FINGERPRINT_PACKETRECIEVEERR:
        Serial.println("Communication error");
        return false;
      case FINGERPRINT_IMAGEFAIL:
        Serial.println("Imaging error");
        return false;
      default:
        Serial.println("Unknown error");
        return false;
    }
    
    // Convert image to characteristic features
    p = finger.image2Tz(1);
    switch (p) {
      case FINGERPRINT_OK:
        Serial.println("Image converted");
        break;
      case FINGERPRINT_IMAGEMESS:
        Serial.println("Image too messy");
        return false;
      case FINGERPRINT_PACKETRECIEVEERR:
        Serial.println("Communication error");
        return false;
      case FINGERPRINT_FEATUREFAIL:
        Serial.println("Could not find fingerprint features");
        return false;
      case FINGERPRINT_INVALIDIMAGE:
        Serial.println("Could not find fingerprint features");
        return false;
      default:
        Serial.println("Unknown error");
        return false;
    }
    
    Serial.println("Remove finger");
    delay(2000);
    p = 0;
    while (p != FINGERPRINT_NOFINGER) {
      p = finger.getImage();
    }
    
    // Get second sample of the same finger
    Serial.println("Place same finger again");
    p = -1;
    while (p != FINGERPRINT_OK) {
      p = finger.getImage();
    }
    
    // Convert second image to characteristic features
    p = finger.image2Tz(2);
    
    // Create a model from the two images
    p = finger.createModel();
    if (p == FINGERPRINT_OK) {
      Serial.println("Prints matched!");
    } else {
      Serial.println("Prints did not match");
      return false;
    }
    
    // Find an empty ID location
    uint8_t id = 1;
    while (finger.loadModel(id) != FINGERPRINT_NOTFOUND) {
      id++;
      if (id == 128) { // Sensor capacity reached
        Serial.println("Sensor full");
        return false;
      }
    }
    
    // Store the model
    p = finger.storeModel(id);
    if (p == FINGERPRINT_OK) {
      Serial.println("Stored model with ID #" + String(id));
      return true;
    } else {
      Serial.println("Error storing model");
      return false;
    }
  }
  return false;
}

// Function to verify a fingerprint
int getFingerprintID() {
  uint8_t p = finger.getImage();
  if (p != FINGERPRINT_OK) {
    Serial.println("Failed to capture image.");
    return -1;
  }

  p = finger.image2Tz(1);  // ✅ Added index 1 for consistency
  if (p != FINGERPRINT_OK) {
    Serial.println("Failed to convert image.");
    return -1;
  }

  p = finger.fingerFastSearch();
  if (p != FINGERPRINT_OK) {
    bluetooth.println("VERIFICATION_FAILED");
    Serial.println("Fingerprint not found in database.");
    return -1;
  }
  
  Serial.println("Fingerprint Matched! ID: " + String(finger.fingerID));
  return finger.fingerID;
}
