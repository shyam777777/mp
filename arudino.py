from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import serial
import threading
import time

app = Flask(__name__)

# Configuration
BLUETOOTH_PORT = 'COM5'  # Update this with the correct Bluetooth port
BLUETOOTH_BAUD = 9600

app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:123456@localhost/voters"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

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
                if message.startswith(prefix):
                    return message  # Return matched message immediately

        time.sleep(0.1)  
    
    print("❌ Timeout: No valid fingerprint message received")
    with bt_lock:
        bt_data_buffer.clear()  # Clear buffer to prevent looping
    return None


def send_bluetooth_command(command):
    """Send a command to the Arduino via Bluetooth."""
    global bt_serial, bt_connected
    
    if not bt_connected or not bt_serial:
        return False, "❌ Bluetooth not connected"

    try:
        full_command = f"{command}\n"
        bt_serial.write(full_command.encode('utf-8'))
        bt_serial.flush()
        time.sleep(0.5)
        return True, "✅ Command sent successfully"
    except Exception as e:
        print(f"❌ Command send error: {e}")
        return False, str(e)


class Voter(db.Model):
    __tablename__ = 'voters'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    aadhaar_number = db.Column(db.String(12), nullable=False)
    fingerprint_id = db.Column(db.Integer, unique=True, nullable=False)


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
        voter = Voter.query.filter_by(fingerprint_id=fingerprint_id).first()
        if not voter:
            return jsonify({'success': False, 'message': '❌ User not found in database'}), 404

        return jsonify({
            'success': True,
            'message': '✅ Fingerprint matched successfully',
            'voter': {
                'id': voter.id,
                'username': voter.username,
                'phone_number': voter.phone_number,
                'aadhaar_number': voter.aadhaar_number,
                'fingerprint_id': fingerprint_id
                
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'❌ Database error: {e}'}), 500


if __name__ == '__main__':
    initialize_bluetooth()
    app.run(debug=True, use_reloader=False)
