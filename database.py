import sqlite3

DB_NAME = "orders.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            phone TEXT,
            operator TEXT,
            amount INTEGER,
            status TEXT DEFAULT 'pending'
        )
    """)
    conn.commit()
    conn.close()

def add_order(user_id, username, phone, operator, amount):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO orders (user_id, username, phone, operator, amount) VALUES (?, ?, ?, ?, ?)",
              (user_id, username, phone, operator, amount))
    conn.commit()
    conn.close()

def update_status(phone, status):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE orders SET status = ? WHERE phone = ?", (status, phone))
    conn.commit()
    conn.close()
