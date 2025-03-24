import serial
import time

port = "COM3"

try:
    ser = serial.Serial(port, 9600, timeout=1)
    ser.close()
    print(f"🔄 Port {port} closed to reset connection.")
    time.sleep(2)
    
    ser = serial.Serial(port, 9600, timeout=1)
    print(f"✅ Successfully opened {port}!")
except serial.SerialException as e:
    print(f"❌ Error opening {port}: {e}")
