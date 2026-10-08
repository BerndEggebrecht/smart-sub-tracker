import sqlite3
import os

DB_PATH = "data/subscriptions.db"

def get_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            color TEXT DEFAULT '#3b82f6'
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            amount REAL NOT NULL,
            interval_type TEXT NOT NULL CHECK(interval_type IN ('weekly', 'monthly', 'yearly')),
            category_id INTEGER,
            start_date TEXT NOT NULL,
            next_due_date TEXT NOT NULL,
            payment_type TEXT DEFAULT 'Überweisung' CHECK(payment_type IN ('Überweisung', 'Dauerauftrag', 'Einzugsermächtigung')),
            is_active INTEGER DEFAULT 1,
            FOREIGN KEY (category_id) REFERENCES categories(id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payment_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subscription_id INTEGER,
            amount REAL NOT NULL,
            paid_date TEXT NOT NULL,
            status TEXT DEFAULT 'paid' CHECK(status IN ('paid', 'pending', 'skipped')),
            FOREIGN KEY (subscription_id) REFERENCES subscriptions(id)
        )
    """)
    
    # Prüfen ob payment_type Spalte bei bestehender DB existiert, falls nicht hinzufügen
    cursor.execute("PRAGMA table_info(subscriptions)")
    columns = [col[1] for col in cursor.fetchall()]
    if "payment_type" not in columns:
        cursor.execute("ALTER TABLE subscriptions ADD COLUMN payment_type TEXT DEFAULT 'Überweisung'")
    
    cursor.execute("SELECT COUNT(*) FROM categories")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO categories (name, color) VALUES (?, ?)", [
            ("Hosting", "#3b82f6"),
            ("Software", "#10b981"),
            ("Tools", "#f59e0b"),
            ("Services", "#8b5cf6")
        ])
    
    conn.commit()
    conn.close()
