# app.py
from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash
import os
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import pandas as pd

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Change in production

# Dummy user
users = {
    "teacher": generate_password_hash("password123")  # username: teacher, password: password123
}

# Login route
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and check_password_hash(users[username], password):
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials')
            return redirect(url_for('login'))
    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Dashboard to list attendance files
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    files = [f for f in os.listdir() if f.startswith("attendance_") and f.endswith(".csv")]
    return render_template('dashboard.html', files=files)

# Download attendance as Excel
@app.route('/download/<filename>')
def download(filename):
    if 'user' not in session:
        return redirect(url_for('login'))

    csv_path = os.path.join(os.getcwd(), filename)
    excel_path = filename.replace('.csv', '.xlsx')

    df = pd.read_csv(csv_path)
    df.to_excel(excel_path, index=False)

    return send_file(excel_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
