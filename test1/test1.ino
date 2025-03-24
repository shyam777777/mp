#include <Adafruit_Fingerprint.h>
#include <SoftwareSerial.h>

// 🔹 Debugging Serial Monitor (USB)
#define DEBUG Serial

// 🔹 Bluetooth Module (HC-05/HC-06) on Pins 10 (RX) & 11 (TX)
SoftwareSerial bluetooth(10, 11);  // TX → Pin 10, RX → Pin 11

// 🔹 Fingerprint Sensor (Adafruit R305) on Pins 2 (TX) & 3 (RX)
SoftwareSerial mySerial(2, 3);  
Adafruit_Fingerprint finger = Adafruit_Fingerprint(&mySerial);

void setup() {
    DEBUG.begin(19200);  // USB Serial Monitor
    bluetooth.begin(9600);  // Bluetooth Communication
    finger.begin(57600);  // Fingerprint Sensor Baud Rate

    delay(500);  // Allow modules to stabilize

    // ✅ Check Fingerprint Sensor
    if (finger.verifyPassword()) {
        DEBUG.println("✅ Fingerprint sensor detected! Ready to scan.");
        bluetooth.println("✅ Fingerprint sensor detected! Ready to scan.");
    } else {
        DEBUG.println("❌ Fingerprint sensor NOT detected! Check wiring.");
        bluetooth.println("❌ Fingerprint sensor NOT detected! Check wiring.");
        while (1);  // Stop execution if fingerprint sensor is not found
    }

    bluetooth.println("Bluetooth Ready");
}

void loop() {
    // ✅ Check for commands from Flask via Bluetooth
    if (bluetooth.available()) {
        String command = bluetooth.readStringUntil('\n'); // Read full command
        command.trim();  // Remove extra spaces or newlines
        DEBUG.println("📨 Command received: " + command);  

        // ✅ Check Fingerprint
        if (command == "CHECK_FINGERPRINT") {
            DEBUG.println("✅ CHECK_FINGERPRINT command received!");
            bluetooth.println("READY_TO_CHECK");

            int fingerprintID = getFingerprintID();
            
            if (fingerprintID >= 0) {
                bluetooth.print("CHECK_SUCCESS:");
                bluetooth.println(fingerprintID);
                DEBUG.println("✅ Fingerprint Matched! ID: " + String(fingerprintID));
            } else {
                bluetooth.println("CHECK_FAILED");
                DEBUG.println("❌ Fingerprint Not Recognized");
            }
        }
    }
}

// 🔹 Function to Scan Fingerprint with Retry & Timeout
int getFingerprintID() {
    DEBUG.println("👆 Place your finger on the scanner...");
    bluetooth.println("👆 Place your finger on the scanner...");

    int retryCount = 0;
    int maxRetries = 10;  
    unsigned long startTime = millis();
    unsigned long timeout = 10000;  // 10 seconds timeout

    while (millis() - startTime < timeout && retryCount < maxRetries) {
        uint8_t result = finger.getImage();
        if (result == FINGERPRINT_OK) {
            DEBUG.println("🟢 Fingerprint image taken!");
            bluetooth.println("🟢 Fingerprint image taken!");

            result = finger.image2Tz();
            if (result == FINGERPRINT_OK) {
                result = finger.fingerFastSearch();
                if (result == FINGERPRINT_OK) {
                    DEBUG.println("✅ Match found! Fingerprint ID: " + String(finger.fingerID));
                    bluetooth.println("✅ Match found! Fingerprint ID: " + String(finger.fingerID));
                    return finger.fingerID;  // ✅ Return matched ID
                } else {
                    DEBUG.println("❌ No match found in database.");
                    bluetooth.println("❌ No match found in database.");
                    return -1;
                }
            } else {
                DEBUG.println("❌ Image conversion failed.");
                bluetooth.println("❌ Image conversion failed.");
            }
        } else if (result == FINGERPRINT_NOFINGER) {
            retryCount++;
            delay(500);  // 🔄 Keep waiting for a finger
        } else {
            DEBUG.println("⚠️ Fingerprint read error.");
            bluetooth.println("⚠️ Fingerprint read error.");
            return -1;  // Stop if sensor has an error
        }
    }

    DEBUG.println("❌ Timeout! No fingerprint detected.");
    bluetooth.println("❌ Timeout! No fingerprint detected.");
    return -1;  
}
