import os
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import requests
from datetime import datetime
from init_db import init_db  # Ensure this import is correct

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'default_secret_key')

DATABASE = 'database.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    return conn

@app.route('/')
def index():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM domains')
    domains = cur.fetchall()
    return render_template('index.html', domains=domains)

@app.route('/add', methods=['POST'])
def add_domain():
    domain = request.form['domain']
    if not domain:
        flash('Domain is required!')
        return redirect(url_for('index'))
    
    conn = get_db()
    cur = conn.cursor()
    cur.execute('INSERT INTO domains (domain, last_checked) VALUES (?, ?)', (domain, None))
    conn.commit()
    flash('Domain added successfully!')
    return redirect(url_for('index'))

@app.route('/check')
def check_domains():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM domains')
    domains = cur.fetchall()
    
    for domain in domains:
        response = requests.get(f'http://{domain[1]}/robots.txt')
        new_content = response.text
        last_checked = domain[2]
        
        if last_checked is None or new_content != last_checked:
            # Notify the user
            send_notification(domain[1])
        
        cur.execute('UPDATE domains SET last_checked = ?, last_checked_at = ? WHERE id = ?',
                    (new_content, datetime.now(), domain[0]))
        conn.commit()
    
    flash('Domains checked successfully!')
    return redirect(url_for('index'))

def send_notification(domain):
    import smtplib
    from email.mime.text import MIMEText

    msg = MIMEText(f'The robots.txt file for {domain} has changed.')
    msg['Subject'] = 'robots.txt Change Alert'
    msg['From'] = 'your_email@example.com'
    msg['To'] = 'user_email@example.com'

    with smtplib.SMTP('smtp.example.com', 587) as server:
        server.starttls()
        server.login('your_email@example.com', 'your_password')
        server.sendmail(msg['From'], [msg['To']], msg.as_string())

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
