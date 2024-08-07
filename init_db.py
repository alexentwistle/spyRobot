# init_db.py
import sqlite3

def init_db():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS domains (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        domain TEXT NOT NULL,
        last_checked TEXT,
        last_checked_at TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
