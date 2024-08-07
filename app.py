import os
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import requests
from datetime import datetime
from init_db import init_db

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

    errors = []
    
    for domain in domains:
        try:
            response = requests.get(f'http://{domain[1]}/robots.txt')
            response.raise_for_status()
            new_content = response.text
            last_checked = domain[2]

            if last_checked is None or new_content != last_checked:
                # Log the change in the changes table
                cur.execute('INSERT INTO changes (domain_id, change_text, change_time) VALUES (?, ?, ?)',
                            (domain[0], 'robots.txt has changed', datetime.now()))
                conn.commit()
            
            cur.execute('UPDATE domains SET last_checked = ?, last_checked_at = ? WHERE id = ?',
                        (new_content, datetime.now(), domain[0]))
            conn.commit()
        except requests.RequestException as e:
            errors.append(f"Error checking {domain[1]}: {str(e)}")
        except Exception as e:
            errors.append(f"Unexpected error for {domain[1]}: {str(e)}")
    
    if errors:
        flash("Some domains could not be checked: " + "; ".join(errors))
    
    flash('Domains checked successfully!')
    return redirect(url_for('index'))

@app.route('/delete/<int:domain_id>', methods=['POST'])
def delete_domain(domain_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('DELETE FROM domains WHERE id = ?', (domain_id,))
    conn.commit()
    flash('Domain deleted successfully!')
    return redirect(url_for('index'))

@app.route('/changes')
def view_changes():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
    SELECT domains.domain, changes.change_text, changes.change_time
    FROM changes
    JOIN domains ON changes.domain_id = domains.id
    ORDER BY changes.change_time DESC
    ''')
    changes = cur.fetchall()
    return render_template('changes.html', changes=changes)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
