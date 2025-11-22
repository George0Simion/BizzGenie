import sqlite3
import datetime

DB_PATH = 'db/inventory.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Create table with: name, quantity, unit (kg/pcs), expiration_date, threshold (for auto-buy)
    c.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            quantity REAL DEFAULT 0,
            unit TEXT DEFAULT 'pcs',
            expiration_date DATE,
            min_threshold REAL DEFAULT 2
        )
    ''')
    conn.commit()
    conn.close()

def add_product(name, qty, unit, expiry):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Check if product with same expiry exists to update, else insert new
    c.execute("SELECT id, quantity FROM inventory WHERE product_name = ? AND expiration_date = ?", (name, expiry))
    row = c.fetchone()
    
    if row:
        new_qty = row[1] + qty
        c.execute("UPDATE inventory SET quantity = ? WHERE id = ?", (new_qty, row[0]))
    else:
        c.execute("INSERT INTO inventory (product_name, quantity, unit, expiration_date) VALUES (?, ?, ?, ?)",
                  (name, qty, unit, expiry))
    
    conn.commit()
    conn.close()
    return f"Added {qty}{unit} of {name} (Exp: {expiry})."

def consume_product(name, qty):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # FIFO Strategy: Consume products expiring soonest first
    c.execute("SELECT id, quantity, unit, expiration_date FROM inventory WHERE product_name = ? AND quantity > 0 ORDER BY expiration_date ASC", (name,))
    rows = c.fetchall()
    
    if not rows:
        return f"Error: {name} not found in stock."
    
    remaining_to_consume = qty
    consumed_details = []

    for row in rows:
        row_id, current_qty, unit, expiry = row
        if remaining_to_consume <= 0:
            break
        
        if current_qty >= remaining_to_consume:
            new_qty = current_qty - remaining_to_consume
            c.execute("UPDATE inventory SET quantity = ? WHERE id = ?", (new_qty, row_id))
            consumed_details.append(f"{remaining_to_consume}{unit} from batch {expiry}")
            remaining_to_consume = 0
        else:
            # Consume this whole batch and move to next
            remaining_to_consume -= current_qty
            c.execute("UPDATE inventory SET quantity = 0 WHERE id = ?", (row_id,))
            consumed_details.append(f"{current_qty}{unit} from batch {expiry}")

    conn.commit()
    conn.close()
    
    if remaining_to_consume > 0:
        return f"Consumed available stock. Still needed {remaining_to_consume} more."
    return f"Consumed {name}: " + ", ".join(consumed_details)

def get_alerts():
    """
    Checks for:
    1. Items expired or expiring in 3 days.
    2. Items below threshold (need buying).
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    today = datetime.date.today()
    warning_date = today + datetime.timedelta(days=3)
    
    alerts = {
        "expired": [],
        "expiring_soon": [],
        "restock_needed": []
    }
    
    # Check Expirations
    c.execute("SELECT product_name, quantity, unit, expiration_date FROM inventory WHERE quantity > 0")
    rows = c.fetchall()
    
    # Aggregate quantities for restock check
    total_stock = {}

    for name, qty, unit, expiry_str in rows:
        expiry = datetime.datetime.strptime(expiry_str, "%Y-%m-%d").date()
        
        # Expiration Logic
        if expiry < today:
            alerts["expired"].append(f"{name}: {qty}{unit} (Expired on {expiry_str})")
        elif expiry <= warning_date:
            alerts["expiring_soon"].append(f"{name}: {qty}{unit} (Expires {expiry_str})")
            
        # Sum for restocking
        if name not in total_stock:
            total_stock[name] = 0
        total_stock[name] += qty

    # Check Restock (Hardcoded threshold of 5 for demo, or fetch from DB)
    for name, total_qty in total_stock.items():
        if total_qty < 2: # Simple threshold
            alerts["restock_needed"].append(f"Buy {name}! Only {total_qty} left.")

    conn.close()
    return alerts