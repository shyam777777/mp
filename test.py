import serial
import time

BLUETOOTH_PORT = 'COM5'  # ✅ Correct port (found earlier)
BLUETOOTH_BAUD = 9600

try:
    bt_serial = serial.Serial(BLUETOOTH_PORT, BLUETOOTH_BAUD, timeout=2)
    time.sleep(2)  # Allow time for HC-05 to initialize

    print(f"✅ Connected to HC-05 on {BLUETOOTH_PORT}")

    # ✅ Send test message
    bt_serial.write(b"HELLO_ARDUINO\n")
    print("🚀 Flask sent: HELLO_ARDUINO")

    # ✅ Read response from Arduino
    response = bt_serial.readline().decode('utf-8').strip()
    print(f"📩 Received from Arduino: {response}")

except serial.SerialException as e:
    print(f"❌ Bluetooth Connection Failed: {e}")

finally:
    if 'bt_serial' in locals() and bt_serial.is_open:
        bt_serial.close()
