from flask import Flask, request, jsonify
import sqlite3
import serial
import threading
import time

app = Flask(__name__)

# Configuration
BLUETOOTH_PORT = 'COM5'  # Update this with the correct Bluetooth port
BLUETOOTH_BAUD = 9600

def setup_database():
    """Create the voters database if it doesn't exist."""
    conn = sqlite3.connect('voters.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS voters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        phone_number TEXT NOT NULL,
        aadhaar_number TEXT NOT NULL,
        fingerprint_id INTEGER UNIQUE NOT NULL,
        registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()

# Global variables for Bluetooth connection
bt_serial = None
bt_connected = False
bt_data_buffer = []
bt_lock = threading.Lock()

def initialize_bluetooth():
    """Initialize Bluetooth communication."""
    global bt_serial, bt_connected
    try:
        if bt_serial and bt_serial.is_open:
            bt_serial.close()
            time.sleep(2)  # Allow Bluetooth module to reset
        
        bt_serial = serial.Serial(BLUETOOTH_PORT, BLUETOOTH_BAUD, timeout=1)
        time.sleep(3)  # Allow time for initialization
        bt_connected = True
        print(f"✅ Connected to Bluetooth on {BLUETOOTH_PORT}")

        # Start listening for incoming messages
        threading.Thread(target=bluetooth_reader, daemon=True).start()

        # Send a test command to confirm Bluetooth is working
        send_bluetooth_command("HELLO_ARDUINO")

        return True
    except serial.SerialException as e:
        print(f"❌ Failed to connect to Bluetooth: {e}")
        bt_connected = False
        return False

def bluetooth_reader():
    """Continuously read messages from Arduino via Bluetooth."""
    global bt_serial, bt_data_buffer, bt_connected
    time.sleep(2)  # Allow Bluetooth to stabilize
    
    while bt_connected:
        try:
            if bt_serial and bt_serial.in_waiting > 0:
                data = bt_serial.readline().decode('utf-8', errors='ignore').strip()
                if data:
                    with bt_lock:
                        bt_data_buffer.append(data)
                    print(f"📩 Received from Arduino: {data}")
        except serial.SerialException as e:
            print(f"❌ Error reading from Bluetooth: {e}")
            bt_connected = False
            break
        time.sleep(0.1)

def wait_for_message(prefix, timeout=10):  
    """Wait for a specific message from Arduino, ignoring old messages."""
    global bt_data_buffer
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        with bt_lock:
            while bt_data_buffer:  # Process only new messages
                message = bt_data_buffer.pop(0)  # Remove oldest message
                print(f"🟢 Checking received message: {message}")  
                
                if message.startswith(prefix):
                    return message  # Return matched message immediately

        time.sleep(0.1)  
    
    print("❌ Timeout: No valid fingerprint message received")
    bt_data_buffer.clear()  # 🛑 Clear buffer to prevent looping
    return None


def send_bluetooth_command(command):
    global bt_serial, bt_connected
    
    print("🔍 Entering send_bluetooth_command() function...")  # Step 1: Check if function is even running

    if not bt_connected:
        print("⚠️ Bluetooth not connected. Trying to reinitialize...")
        if not initialize_bluetooth():
            return False, "Bluetooth not connected"

    try:
        time.sleep(1)  # Give time before sending
        full_command = f"{command}\r\n"  # Ensure proper termination
        
        # Check if Bluetooth is initialized
        if bt_serial is None:
            print("❌ bt_serial is None!")
            return False, "Serial object not initialized"
        
        print(f"🔍 Bluetooth connection status: {bt_serial.is_open}")  # Step 2: Check if port is open
        if not bt_serial.is_open:
            return False, "Bluetooth port is closed"

        print(f"🚀 Flask is sending: {full_command.encode('utf-8')}")  # Step 3: Print command being sent

        bt_serial.write(full_command.encode('utf-8'))  # Send command
        print("📤 Data written, flushing now...")  # Step 4: Confirm data written
        bt_serial.flush()
        print("✅ Command sent successfully!")  # Step 5: Confirm success

        time.sleep(1)  # Allow Arduino time to process
        return True, "Command sent"
    except Exception as e:
        bt_connected = False
        print(f"❌ Error sending command: {e}")  # Step 6: Catch errors
        return False, f"Error sending command: {e}"



@app.route('/api/check_fingerprint', methods=['POST'])
def check_fingerprint():
    """Check fingerprint from the website using Arduino."""
    success, message = send_bluetooth_command("CHECK_FINGERPRINT")
    if not success:
        return jsonify({'success': False, 'message': message}), 500

    if not wait_for_message("READY_TO_CHECK", timeout=10):
        return jsonify({'success': False, 'message': '❌ Arduino not responding'}), 500

    check_msg = wait_for_message("CHECK_SUCCESS:", timeout=10)
    if not check_msg:
        if wait_for_message("CHECK_FAILED", timeout=5):
            return jsonify({'success': False, 'message': '❌ Fingerprint not recognized'}), 404
        return jsonify({'success': False, 'message': '❌ Fingerprint check timed out'}), 500

    fingerprint_id = int(check_msg.split(":")[-1])

    try:
        conn = sqlite3.connect('voters.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, phone_number, aadhaar_number FROM voters WHERE fingerprint_id = ?", (fingerprint_id,))
        result = cursor.fetchone()
        conn.close()

        if not result:
            return jsonify({'success': False, 'message': '❌ User not found in database'}), 404

        voter_id, username, phone_number, aadhaar_number = result
        return jsonify({
            'success': True,
            'message': '✅ Fingerprint matched successfully',
            'voter': {
                'id': voter_id,
                'username': username,
                'phone_number': phone_number,
                'aadhaar_number': aadhaar_number,
                'fingerprint_id': fingerprint_id
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'❌ Database error: {e}'}), 500

if __name__ == '__main__':
    setup_database()
    initialize_bluetooth()
    app.run(debug=True, use_reloader=False)
