from datetime import datetime
from flask import Flask, request, jsonify, render_template, redirect, url_for ,session, flash, current_app
from flask_sqlalchemy import SQLAlchemy
import serial
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from keras.saving import register_keras_serializable
import base64
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import time
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "Iamnotallowinganyonetoknowmykey"


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost/voters'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


SERIAL_PORT = 'COM3'
BAUD_RATE = 115200
ser = None

try:
    if 'ser' in locals() and ser is not None and ser.is_open:
        ser.close()
        print(f"✅ Successfully closed the previous connection to {SERIAL_PORT}")

    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=5)
    print(f"✅ Successfully connected to {SERIAL_PORT}")
except serial.SerialException as e:
    print(f"❌ Error: Could not open port {SERIAL_PORT}. {e}")


@register_keras_serializable()
def squared_euclidean_distance(tensors):
    return tf.reduce_sum(tf.square(tensors[0] - tensors[1]), axis=-1, keepdims=True)


MODEL_PATH = "fingerprint_siamese_model_1.keras"
try:
    model = tf.keras.models.load_model(MODEL_PATH, custom_objects={"squared_euclidean_distance": squared_euclidean_distance})
    print("✅ Model loaded successfully!")
except Exception as e:
    print(f"❌ Error loading model: {e}")


AES_KEY_BASE64 = os.getenv("AES_KEY")

AES_KEY = b'\xd3\x1f6\t\x15\xab\xe6\xf78[\xbf~\t\xf1\x9ar{\x00\x13>\xcdE\xc4#wR\x1d1\x13\xddU\xce'  

def encrypt_fingerprint(fingerprint_data):
    iv = os.urandom(16)  
    cipher = AES.new(AES_KEY, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(fingerprint_data, AES.block_size))
    
    print(f"🛡️ AES Key Used: {AES_KEY.hex()}")
    print(f"📏 Encrypted Fingerprint Length: {len(encrypted)} bytes")
    print(f"🌀 IV Used: {iv.hex()}")
    print(f"🔐 Encrypted Data (Hex): {encrypted.hex()}")


    return iv + encrypted 

def decrypt_fingerprint(encrypted_data):
    iv = encrypted_data[:16]  
    encrypted_fingerprint = encrypted_data[16:]  

    cipher = AES.new(AES_KEY, AES.MODE_CBC, iv)
    decrypted_fingerprint = unpad(cipher.decrypt(encrypted_fingerprint), AES.block_size)

    print(f"🔓 Decrypted Data Length: {len(decrypted_fingerprint)} bytes")
    print(f"📜 Decrypted Fingerprint (Hex): {decrypted_fingerprint.hex()}")

    return decrypted_fingerprint



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(15), unique=True, nullable=False)
    photo = db.Column(db.String(255), nullable=True)
    voterId = db.Column(db.String(20), unique=True, nullable=False)
    address = db.Column(db.Text, nullable=False)
    aadhaar = db.Column(db.String(12), unique=True, nullable=False)
    fingerprint_template = db.Column(db.LargeBinary, nullable=False)
    has_voted = db.Column(db.Boolean, default=False)
    def get_photo_url(self):
        if self.photo:
            return os.path.join(current_app.config["UPLOAD_FOLDER"], self.photo)
        return None
    
class Candidates(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    party = db.Column(db.String(255), nullable=False)
    symbol = db.Column(db.String(255))  # Stores only the file name
    position = db.Column(db.String(255), nullable=False)
    state = db.Column(db.String(255), nullable=False)
    constituency = db.Column(db.String(255), nullable=False)
    bio = db.Column(db.Text)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    contact_info = db.Column(db.String(255))
    votes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def get_fingerprint_template():
    try:
        if ser is None or not ser.is_open:
            return None, "Serial port not available"

        ser.write(b'SEND_TEMPLATE\n')
        time.sleep(3)

        received_data = ser.read(512)
        print(f"📡 Raw Data Received (Hex): {received_data.hex()}")
        print(f"📡 Raw Data Length: {len(received_data)} bytes")

        if not received_data:
            return None, "No fingerprint data received. Possible sensor issue."
        print(f"📡 Received Data (Hex): {received_data.hex()}")
        print(f"📡 Received Data (Raw): {received_data}")
        print()
        if not received_data:
            return None, "No fingerprint data received"

        return received_data, None

    except Exception as e:
        return None, f"Error reading from serial: {e}"


@app.route("/capture_fingerprint", methods=["GET"])
def capture_fingerprint():
    try:
        fingerprint_data, error = get_fingerprint_template()
        if error:
            return jsonify({"error": error}), 400

        return jsonify({"status": "success", "fingerprint": base64.b64encode(fingerprint_data).decode("utf-8")})

    except Exception as e:
        return jsonify({"error": str(e)}), 400



@app.route("/register_user", methods=["POST"])
def register_user():
    try:
        name = request.form.get("name")
        voterid = request.form.get("voterid")
        phone_number = request.form.get("phone_number")
        address = request.form.get("address")
        aadhaar = request.form.get("aadhaar")
        fingerprint_base64 = request.form.get("fingerprint")

        if "photo" not in request.files:
            return jsonify({"error": "No photo uploaded"}), 400

        photo = request.files["photo"]
        if photo.filename == "" or not allowed_file(photo.filename):
            return jsonify({"error": "Invalid photo file"}), 400

        filename = secure_filename(photo.filename)
        photo_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        photo.save(photo_path)  # Save photo to the folder


        if not name or not fingerprint_base64:
            return jsonify({"error": "Missing name or fingerprint data"}), 400

        
        fingerprint_data = base64.b64decode(fingerprint_base64)

        
        if len(fingerprint_data) != 512:
            return jsonify({"error": f"Invalid fingerprint data size: {len(fingerprint_data)} bytes (Expected: 512)"}), 400

        fingerprint_npy = np.frombuffer(fingerprint_data, dtype=np.uint8)

        print(f"✅ Fingerprint successfully received, shape: {fingerprint_npy.shape}")


        
        encrypted_fingerprint = encrypt_fingerprint(fingerprint_data)

        
        existing_user = User.query.filter_by(voterId=voterid).first()
        if existing_user:
            return jsonify({"error": "User already exists"}), 400
        
        new_user = User(
            name=name,
            voterId=voterid,
            phone_number=phone_number,
            address=address,
            aadhaar=aadhaar,
            fingerprint_template=encrypted_fingerprint,
            photo=filename,  # Store filename in DB
        )
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"status": "success", "message": "User registered successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400



@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/fingerprint", methods=["GET", "POST"])
def verify_fingerprint():
    if request.method == "GET":
        purpose = request.args.get("purpose", "login")
        return render_template("fingerprint_verification.html", purpose=purpose)

    try:
        data = request.get_json()
        fingerprint_base64 = data.get("fingerprint")
        purpose = data.get("purpose", "login")

        if not fingerprint_base64:
            return jsonify({"error": "Missing fingerprint data"}), 400

        if 'voterid' not in session:
            return jsonify({"error": "User not logged in"}), 401

        fingerprint_data = base64.b64decode(fingerprint_base64)
        voterid = session['voterid']

        user = User.query.filter_by(voterId=voterid).first()
        if not user:
            session.pop('voterid', None)
            return jsonify({"error": "User not found", "redirect": url_for('login')}), 404

        # Fingerprint matching logic
        try:
            decrypted_fp = decrypt_fingerprint(user.fingerprint_template)
            stored_fp = np.frombuffer(decrypted_fp, dtype=np.uint8).reshape(1, 1, -1)
            input_fp = np.frombuffer(fingerprint_data, dtype=np.uint8).reshape(1, 1, -1)

            similarity = model.predict([input_fp, stored_fp])[0][0]
            print(f"[DEBUG] Similarity score: {similarity}")

            if similarity > 0.5:
                session['authenticated'] = True
                print(f"[DEBUG] Fingerprint matched for purpose: {purpose}")

                if purpose == "vote":
                    candidate_id = session.get('selected_candidate')
                    if not candidate_id:
                        return jsonify({"error": "No candidate selected", "redirect": url_for('candidates_list')}), 400

                    candidate = Candidates.query.get(candidate_id)
                    if not candidate:
                        return jsonify({"error": "Candidate not found", "redirect": url_for('candidates_list')}), 404

                    if user.has_voted:
                        return jsonify({
                            "status": "already_voted",
                            "redirect": url_for('vote_success', candidate_id=candidate_id)
                        })

                    candidate.votes += 1
                    user.has_voted = True
                    db.session.commit()

                    return jsonify({
                        "status": "vote_success",
                        "redirect": url_for('vote_success', candidate_id=candidate_id)
                    })

                # For login flow
                return jsonify({
                    "status": "match",
                    "redirect": url_for('candidates_list')
                })

            # Fingerprint did not match
            session.pop('voterid', None)
            return jsonify({"status": "no_match", "redirect": url_for('login')})

        except Exception as decrypt_error:
            print(f"[ERROR] Decryption or verification failed: {decrypt_error}")
            session.pop('voterid', None)
            return jsonify({"error": "Fingerprint verification failed", "redirect": url_for('login')}), 400

    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        session.pop('voterid', None)
        return jsonify({"error": str(e), "redirect": url_for('login')}), 400


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        voterid = request.form['voterid']

        user = User.query.filter_by(voterId=voterid).first()

        if user:
            session['voterid'] = voterid
            return redirect(url_for("verify_fingerprint", purpose="login"))
        else:
            flash("VoterId not found. Please try again.")
    return render_template('login.html')



@app.route('/candidates')
def candidates_list():
    if 'voterid' not in session:
        return redirect(url_for('login'))
    
    candidates = Candidates.query.all()
    
    return render_template('candidates_list.html', candidates=candidates)


@app.route('/candidate/<int:candidate_id>', methods=['GET', 'POST'])
def candidate_detail(candidate_id):
    if 'voterid' not in session:
        return redirect(url_for('login'))

    session['selected_candidate'] = candidate_id
    # Fetch candidate details from the database
    candidate = Candidates.query.get(candidate_id)
    if not candidate:
        flash("Candidate not found!")
        return redirect(url_for('candidates_list'))

    if request.method == 'POST':
        print("stored")
        return redirect(url_for("verify_fingerprint", purpose="vote"))

    return render_template('candidate_detail.html', candidate=candidate)

@app.route('/vote_success/<int:candidate_id>')
def vote_success(candidate_id):
    if 'voterid' not in session:
        return redirect(url_for('login'))

    candidate = Candidates.query.get(candidate_id)
    if not candidate:
        flash("Candidate not found!")
        return redirect(url_for('candidates_list'))

    return render_template('vote_success.html', candidate=candidate)



@app.route('/logout')
def logout():
    session.pop('user_phone', None)
    session.pop('fingerprint_id', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=False)