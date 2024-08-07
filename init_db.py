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
    cur.execute('''
    CREATE TABLE IF NOT EXISTS changes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        domain_id INTEGER,
        change_text TEXT,
        change_time TIMESTAMP,
        FOREIGN KEY(domain_id) REFERENCES domains(id)
    )
    ''')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
