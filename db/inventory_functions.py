import sqlite3
import datetime
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = 'db/inventory.db'

def init_db():
    db_dir = os.path.dirname(DB_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT, product_name TEXT NOT NULL, category TEXT DEFAULT 'general',
            quantity REAL DEFAULT 0, unit TEXT DEFAULT 'pcs', expiration_date DATE,
            auto_buy BOOLEAN DEFAULT 0, min_threshold REAL DEFAULT 2)''')
    conn.commit()
    conn.close()

def add_product(name, category, qty, unit, expiry, auto_buy):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, quantity FROM inventory WHERE product_name = ? AND expiration_date = ?", (name, expiry))
    row = c.fetchone()
    if row:
        c.execute("UPDATE inventory SET quantity = ?, category = ?, auto_buy = ? WHERE id = ?", 
                  (row[1] + qty, category, auto_buy, row[0]))
    else:
        c.execute("INSERT INTO inventory (product_name, category, quantity, unit, expiration_date, auto_buy) VALUES (?, ?, ?, ?, ?, ?)", 
                  (name, category, qty, unit, expiry, auto_buy))
    conn.commit()
    conn.close()
    return f"Added {qty}{unit} of '{name}'"

def consume_product(name, qty):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, quantity, unit, expiration_date FROM inventory WHERE product_name = ? AND quantity > 0 ORDER BY expiration_date ASC", (name,))
    rows = c.fetchall()
    if not rows:
        conn.close()
        return f"Error: '{name}' not found."
    
    remaining = qty
    consumed_log = []
    for row in rows:
        row_id, current_qty, unit, exp = row
        if remaining <= 0: break
        
        take = min(current_qty, remaining)
        new_qty = current_qty - take
        c.execute("UPDATE inventory SET quantity = ? WHERE id = ?", (new_qty, row_id))
        consumed_log.append(f"{take}{unit} (Exp: {exp})")
        remaining -= take
    conn.commit()
    conn.close()
    return f"Consumed {name}: " + ", ".join(consumed_log)

def get_all_inventory():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM inventory WHERE quantity > 0 ORDER BY category, product_name")
    rows = [dict(row) for row in c.fetchall()]
    conn.close()
    return rows

def get_alerts():
    # Simplified alert logic for brevity
    return {"restock_needed": []}