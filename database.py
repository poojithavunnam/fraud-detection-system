import sqlite3

def get_db():
    conn = sqlite3.connect("bank.db")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY,
        email TEXT,
        password TEXT
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS transactions(
        id INTEGER PRIMARY KEY,
        email TEXT,
        amount REAL,
        location TEXT,
        fraud INTEGER
    )
    """)

    conn.commit()