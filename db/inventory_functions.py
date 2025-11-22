import sqlite3
import datetime

DB_PATH = 'db/inventory.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Added: category, auto_buy (boolean)
    c.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            category TEXT DEFAULT 'general',
            quantity REAL DEFAULT 0,
            unit TEXT DEFAULT 'pcs',
            expiration_date DATE,
            auto_buy BOOLEAN DEFAULT 0,
            min_threshold REAL DEFAULT 2
        )
    ''')
    conn.commit()
    conn.close()

def add_product(name, category, qty, unit, expiry, auto_buy):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 1. Check if this specific batch (Name + Expiry) exists
    c.execute("SELECT id, quantity FROM inventory WHERE product_name = ? AND expiration_date = ?", (name, expiry))
    row = c.fetchone()
    
    if row:
        # Update existing batch
        new_qty = row[1] + qty
        # We also update category/auto_buy just in case they changed preferences
        c.execute("UPDATE inventory SET quantity = ?, category = ?, auto_buy = ? WHERE id = ?", 
                  (new_qty, category, auto_buy, row[0]))
        action = "Updated existing batch"
    else:
        # Insert new batch
        c.execute("""
            INSERT INTO inventory (product_name, category, quantity, unit, expiration_date, auto_buy) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, category, qty, unit, expiry, auto_buy))
        action = "Created new batch"
    
    conn.commit()
    conn.close()
    return f"{action}: {qty}{unit} of '{name}' (Category: {category}, Exp: {expiry})"

def consume_product(name, qty):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # FIFO Strategy: Consume products expiring soonest first
    c.execute("SELECT id, quantity, unit, expiration_date FROM inventory WHERE product_name = ? AND quantity > 0 ORDER BY expiration_date ASC", (name,))
    rows = c.fetchall()
    
    if not rows:
        conn.close()
        return f"Error: '{name}' not found in stock."
    
    remaining_to_consume = qty
    consumed_details = []

    for row in rows:
        row_id, current_qty, unit, expiry = row
        if remaining_to_consume <= 0:
            break
        
        if current_qty >= remaining_to_consume:
            new_qty = current_qty - remaining_to_consume
            c.execute("UPDATE inventory SET quantity = ? WHERE id = ?", (new_qty, row_id))
            consumed_details.append(f"{remaining_to_consume}{unit} (batch {expiry})")
            remaining_to_consume = 0
        else:
            remaining_to_consume -= current_qty
            c.execute("UPDATE inventory SET quantity = 0 WHERE id = ?", (row_id,))
            consumed_details.append(f"{current_qty}{unit} (batch {expiry})")

    conn.commit()
    conn.close()
    
    if remaining_to_consume > 0:
        return f"Consumed available stock of {name}. Still need {remaining_to_consume} more."
    return f"Consumed {name}: " + ", ".join(consumed_details)

def get_alerts():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    today = datetime.date.today()
    warning_date = today + datetime.timedelta(days=3)
    
    alerts = {
        "expired": [],
        "expiring_soon": [],
        "restock_needed": []
    }
    
    c.execute("SELECT product_name, quantity, unit, expiration_date, min_threshold, auto_buy FROM inventory WHERE quantity > 0")
    rows = c.fetchall()
    
    total_stock = {} 
    product_meta = {}

    for name, qty, unit, expiry_str, threshold, auto_buy in rows:
        expiry = datetime.datetime.strptime(expiry_str, "%Y-%m-%d").date()
        
        if expiry < today:
            alerts["expired"].append(f"{name}: {qty}{unit} (Expired {expiry_str})")
        elif expiry <= warning_date:
            alerts["expiring_soon"].append(f"{name}: {qty}{unit} (Expires {expiry_str})")
            
        if name not in total_stock:
            total_stock[name] = 0
            product_meta[name] = {"threshold": threshold, "auto_buy": auto_buy}
        total_stock[name] += qty

    for name, total_qty in total_stock.items():
        meta = product_meta[name]
        if meta["auto_buy"] and total_qty < meta["threshold"]:
            alerts["restock_needed"].append(f"Auto-Buy Alert: {name} (Stock: {total_qty}, Threshold: {meta['threshold']})")

    conn.close()
    return alerts

def get_all_inventory():
    """
    Returns the full inventory list as a list of dictionaries for JSON API.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # This allows us to access columns by name
    c = conn.cursor()
    
    c.execute("SELECT * FROM inventory WHERE quantity > 0 ORDER BY category, product_name")
    rows = c.fetchall()
    
    inventory_list = []
    for row in rows:
        inventory_list.append({
            "id": row["id"],
            "product_name": row["product_name"],
            "category": row["category"],
            "quantity": row["quantity"],
            "unit": row["unit"],
            "expiration_date": row["expiration_date"],
            "auto_buy": bool(row["auto_buy"]),
            "min_threshold": row["min_threshold"]
        })
    
    conn.close()
    return inventory_list