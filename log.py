import serial

SERIAL_PORT = "COM3"  # Change if needed
BAUD_RATE = 9600

try:
    with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
        print(f"✅ Logging Arduino output from {SERIAL_PORT}...")
        while True:
            line = ser.readline().decode("utf-8", errors="ignore").strip()
            if line:
                print(line)
except serial.SerialException as e:
    print(f"❌ Error: {e}")
