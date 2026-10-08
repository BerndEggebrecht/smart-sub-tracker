import sqlite3
import os
from datetime import datetime

DB_PATH = "/opt/subtracker/data/subscriptions.db"
REPORT_DIR = "/opt/subtracker/reports"

def generate_monthly_report():
    os.makedirs(REPORT_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    data = conn.execute("SELECT SUM(amount) as total FROM subscriptions WHERE is_active = 1").fetchone()
    total = data["total"] or 0.0
    
    subs = conn.execute("""
        SELECT s.name, s.amount, s.interval_type, s.next_due_date, c.name as category_name
        FROM subscriptions s 
        LEFT JOIN categories c ON s.category_id = c.id 
        WHERE s.is_active = 1
        ORDER BY s.next_due_date ASC
    """).fetchall()
    
    filename = f"abo-report-{datetime.now().strftime('%Y-%m')}.md"
    filepath = os.path.join(REPORT_DIR, filename)
    
    report = f"""# 📊 Automatisierter Abo- & Kostenreport
**Erstellungsdatum:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 💡 Monats-Prognose
* **Gesamtkosten (monatlich berechnet):** {total:.2f} €
* **Aktive Abonnements:** {len(subs)}

## 📋 Aktive Fixkosten
| Name | Kategorie | Betrag | Intervall | Nächste Fälligkeit |
| :--- | :--- | :--- | :--- | :--- |
"""
    for s in subs:
        report += f"| {s['name']} | {s['category_name']} | {s['amount']:.2f} € | {s['interval_type']} | {s['next_due_date']} |\n"
        
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(report)
        
    print(f"Report erfolgreich erstellt: {filepath}")
    conn.close()

if __name__ == "__main__":
    generate_monthly_report()
