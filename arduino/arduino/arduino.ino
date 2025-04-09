#include <Adafruit_Fingerprint.h>
#include <SoftwareSerial.h>

#define RX_PIN 2  // TX of R307 to pin 2
#define TX_PIN 3  // RX of R307 to pin 3

SoftwareSerial mySerial(RX_PIN, TX_PIN);
Adafruit_Fingerprint finger = Adafruit_Fingerprint(&mySerial);

void setup() {
    Serial.begin(115200);
    mySerial.begin(57600);
    finger.begin(57600);

}

void loop() {
    if (Serial.available()) {
        String command = Serial.readStringUntil('\n');
        command.trim();

        if (command == "SEND_TEMPLATE") {
            sendFingerprintTemplate();
        }
    }
}

void sendFingerprintTemplate() {
    uint8_t p = finger.getImage();
    if (p != FINGERPRINT_OK) {
        Serial.println("❌ Failed to capture image.");
        return;
    }
    
    // Convert image to template (Buffer 1)
    p = finger.image2Tz(1);
    if (p != FINGERPRINT_OK) {
        Serial.println("❌ Failed to convert image to template (Buffer 1).");
        return;
    }
        // Convert the same image to template (Buffer 2) before merging
    p = finger.image2Tz(2);
    if (p != FINGERPRINT_OK) {
        Serial.println("❌ Failed to convert image to template (Buffer 2).");
        return;
    }

    // Try creating a model
    p = finger.createModel();
    if (p != FINGERPRINT_OK) {
        Serial.println("❌ Failed to create model.");
        return;
    }
    

    // ✅ **Store the model into the sensor's database at position 1**
    p = finger.storeModel(1);
    if (p != FINGERPRINT_OK) {
        Serial.println("❌ Failed to store template.");
        return;
    }
    

    // ✅ **Now load the stored model into buffer 1**
    p = finger.loadModel(1);
    if (p != FINGERPRINT_OK) {
        Serial.println("❌ Failed to load template.");
        return;
    }
    

    // **Extract and send template**
    uint8_t templateBuffer[512];
    p = finger.getModel();
    if (p != FINGERPRINT_OK) {
        Serial.println("❌ Failed to retrieve template.");
        return;
    }


    for (int i = 0; i < 512; i++) {
        Serial.print(templateBuffer[i], HEX);
        Serial.print(" ");
        if ((i + 1) % 16 == 0) Serial.println();  // New line every 16 bytes
    }
}
