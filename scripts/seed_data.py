import sqlite3
import random
from datetime import datetime, timedelta

DB_PATH = "/opt/subtracker/data/subscriptions.db"

# Fiktive Beispieldaten für Abos und Fixkosten
MOCK_SUBS = [
    ("Hetzner Server vServer", 5.99, "monthly", 1),       # Hosting
    ("GitHub Copilot", 10.00, "monthly", 2),             # Software
    ("Netflix Premium", 17.99, "monthly", 4),            # Services
    ("Spotify Family", 14.99, "monthly", 4),             # Services
    ("JetBrains All Products Pack", 249.00, "yearly", 2), # Software
    ("DigitalOcean Kubernetes", 24.00, "monthly", 1),    # Hosting
    ("ChatGPT Plus", 22.00, "monthly", 2),               # Software
    ("Domain Name (.de)", 12.00, "yearly", 1),           # Hosting
    ("Notion Plus", 10.00, "monthly", 3),                # Tools
    ("AWS S3 Storage", 8.50, "monthly", 1),              # Hosting
    ("DeepL Pro API", 29.99, "monthly", 3),              # Tools
    ("Cloudflare Pro", 20.00, "monthly", 1)              # Hosting
]

def seed_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Prüfen ob Kategorien existieren
    cursor.execute("SELECT COUNT(*) FROM categories")
    if cursor.fetchone()[0] == 0:
        print("❌ Keine Kategorien gefunden. Bitte starte erst den FastAPI-Server oder initidiere die DB.")
        conn.close()
        return

    print("🌱 Generiere fiktive Testdaten...")
    
    today = datetime.today()
    inserted_count = 0
    
    for name, amount, interval, category_id in MOCK_SUBS:
        # Fälligkeit in den nächsten -10 bis +25 Tagen verteilen, damit Timeline direkt befüllt wird
        random_days = random.randint(-10, 25)
        due_date = today + timedelta(days=random_days)
        due_date_str = due_date.strftime("%Y-%m-%d")
        start_date_str = (due_date - timedelta(days=365 if interval == 'yearly' else 30)).strftime("%Y-%m-%d")
        
        # In subscriptions einfügen
        cursor.execute("""
            INSERT INTO subscriptions (name, amount, interval_type, category_id, start_date, next_due_date, is_active)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        """, (name, amount, interval, category_id, start_date_str, due_date_str))
        
        sub_id = cursor.lastrowid
        
        # Ein paar historische Zahlungen für vergangene Daten erzeugen
        if random_days < 0:
            cursor.execute("""
                INSERT INTO payment_history (subscription_id, amount, paid_date, status)
                VALUES (?, ?, ?, 'paid')
            """, (sub_id, amount, due_date_str))
            
        inserted_count += 1
        
    conn.commit()
    conn.close()
    print(f"✅ Erfolgreich {inserted_count} fiktive Abos und Fixkosten hinzugefügt!")

if __name__ == "__main__":
    seed_database()
