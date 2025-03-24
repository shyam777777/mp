from flask import Flask, render_template, request, redirect, url_for, session, flash
import time

app = Flask(__name__)
app.secret_key = "securekey"

users = {
    "1234567890": {"fingerprint_id": 1},
    "0987654321": {"fingerprint_id": 2},
    "9876543210": {"fingerprint_id": 3}
}


candidates = {
    1: {"name": "A Dhanwati Chandela A", "party": "AAP", "Education": "10th Pass"},
    2: {"name": "Aahir Deepak Chaudharyy", "party": "BJP", "Education": "Graduate Professional"},
    3: {"name": "Aakash Goel", "party": "IND", "Education": "Graduate Professional."},
    4: {"name": "Aaley Mohammed Iqbal", "party": "AAP", "Education": "12th Pass"},
    5: {"name": "Abdul Rehman", "party": "INC", "Education": "8th Pass."},
    6: {"name": "Abhishek Dutt", "party": "INC", "Education": "5th Pass."},
    7: {"name": "Ajay Kumar", "party": "Peace Party", "Education": "10th pass."},
    8: {"name": "Babita", "party": "IND", "Education": "8th Pass."},
    9: {"name": "Mahesh Kumar", "party": "BSP", "Education": "Graduate Professional."},
    10: {"name": "Mange Ram", "party": "INC", "Education": "Illiterate."}
}


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone_number = request.form['phone_number']


        if phone_number in users:
            session['user_phone'] = phone_number
            session['fingerprint_id'] = users[phone_number]["fingerprint_id"]
            return redirect(url_for('fingerprint_verification'))
        else:
            flash("Phone number or Aadhaar number not found. Please try again.")
    return render_template('login.html')



@app.route('/fingerprint', methods=['GET', 'POST'])
def fingerprint_verification():
    if 'user_phone' not in session:
        return redirect(url_for('login'))


    if request.method == 'POST':
        fingerprint_verified = request.form.get("fingerprint") == "verified"  

        if fingerprint_verified:
            return redirect(url_for('candidates_list'))  
        else:
            flash("Fingerprint verification failed. Please try again.")
            return redirect(url_for('fingerprint_verification'))

    return render_template('fingerprint_verification.html')



@app.route('/candidates')
def candidates_list():
    if 'user_phone' not in session:
        return redirect(url_for('login'))
    return render_template('candidates_list.html', candidates=candidates)



@app.route('/candidate/<int:candidate_id>', methods=['GET', 'POST'])
def candidate_detail(candidate_id):
    if 'user_phone' not in session:
        return redirect(url_for('login'))

    candidate = candidates.get(candidate_id)
    if not candidate:
        return "Candidate not found", 404


    if request.method == 'POST':
        return redirect(url_for('fingerprint_verification_for_vote', candidate_id=candidate_id))

    return render_template('candidate_detail.html', candidate=candidate)



@app.route('/fingerprint_for_vote/<int:candidate_id>', methods=['GET', 'POST'])
def fingerprint_verification_for_vote(candidate_id):
    if 'user_phone' not in session:
        return redirect(url_for('login'))


    if request.method == 'POST':
        fingerprint_verified = request.form.get("fingerprint") == "verified"  

        if fingerprint_verified:
            return redirect(url_for('vote_success', candidate_id=candidate_id)) 
        else:
            flash("Fingerprint verification failed. Please try again.")
            return redirect(url_for('fingerprint_verification_for_vote', candidate_id=candidate_id))

    return render_template('fingerprint_verification_for_vote.html', candidate_id=candidate_id)



@app.route('/vote_success/<int:candidate_id>')
def vote_success(candidate_id):
    if 'user_phone' not in session:
        return redirect(url_for('login'))


    return render_template('vote_success.html', candidate=candidates[candidate_id])



@app.route('/logout')
def logout():
    session.pop('user_phone', None)
    session.pop('fingerprint_id', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
