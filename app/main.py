from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, StreamingResponse
import sqlite3
import csv
import io
import subprocess
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from app.database import get_db, init_db
from app.models import SubscriptionCreate, SubscriptionUpdate, PaymentRecord, CategoryCreate
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# .env Datei laden
load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER", "mail.gmx.net")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT", "")

app = FastAPI(title="Smart Sub-Tracker", version="1.7.0")

def send_email_notification(subject: str, body: str):
    """Sendet eine E-Mail Benachrichtigung über anstehende Zahlungen."""
    try:
        msg = MIMEMultipart()
        msg["From"] = SMTP_USER
        msg["To"] = EMAIL_RECIPIENT
        msg["Subject"] = subject
        
        msg.attach(MIMEText(body, "plain", "utf-8"))
        
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, EMAIL_RECIPIENT, msg.as_string())
        print("📧 E-Mail-Benachrichtigung erfolgreich gesendet.")
        return True
    except Exception as e:
        print(f"E-Mail-Versand fehlgeschlagen: {e}")
        raise e

@app.get("/api/test-email")
def trigger_test_email():
    """Manueller Test-Endpunkt für den E-Mail-Versand."""
    try:
        subject = "🧪 Smart Sub-Tracker: Test-Benachrichtigung"
        body = "Hallo Bernd,\n\nDies ist eine erfolgreiche Test-E-Mail von deinem lokalen Smart Sub-Tracker auf Kali Linux!\n\nViele Grüße\nDein Tracker"
        send_email_notification(subject, body)
        return {"status": "success", "message": "Test-E-Mail wurde erfolgreich versendet!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def check_due_notifications():
    try:
        conn = sqlite3.connect("data/subscriptions.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        today_str = datetime.today().strftime("%Y-%m-%d")
        tomorrow_str = (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        due_subs = cursor.execute("""
            SELECT name, amount, next_due_date 
            FROM subscriptions 
            WHERE is_active = 1 AND next_due_date <= ?
        """, (tomorrow_str,)).fetchall()
        
        if due_subs:
            count = len(due_subs)
            title = f"💳 Abo-Tracker: {count} Zahlung(en) fällig!"
            message = "Folgende Zahlungen stehen heute/morgen an oder sind überfällig:\n\n"
            message += "\n".join([f"• {s['name']} ({s['amount']:.2f} €) am {s['next_due_date']}" for s in due_subs])
            
            subprocess.run(["notify-send", "-u", "critical", title, message])
            
            if SMTP_SERVER != "smtp.example.com" and SMTP_USER:
                send_email_notification(title, message)
            
        conn.close()
    except Exception as e:
        print(f"Benachrichtigungs-Fehler: {e}")

@app.on_event("startup")
def startup_event():
    init_db()
    check_due_notifications()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    with open("app/static/index.html", "r", encoding="utf-8") as f:
        return f.read()

def get_next_due_date(current_due_str: str, interval: str) -> str:
    current_due = datetime.strptime(current_due_str, "%Y-%m-%d")
    if interval == 'weekly':
        next_due = current_due + timedelta(weeks=1)
    elif interval == 'monthly':
        month = current_due.month % 12 + 1
        year = current_due.year + (current_due.month // 12)
        try:
            next_due = current_due.replace(year=year, month=month)
        except ValueError:
            next_due = (current_due.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    elif interval == 'yearly':
        try:
            next_due = current_due.replace(year=current_due.year + 1)
        except ValueError:
            next_due = current_due + timedelta(days=365)
    else:
        next_due = current_due
    return next_due.strftime("%Y-%m-%d")

def adjust_to_bank_day(date_str: str) -> str:
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    while dt.weekday() >= 5:
        dt += timedelta(days=1)
    return dt.strftime("%Y-%m-%d")

@app.get("/api/dashboard")
def get_dashboard_data(db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    subs = cursor.execute("""
        SELECT s.*, c.name as category_name, c.color 
        FROM subscriptions s 
        LEFT JOIN categories c ON s.category_id = c.id 
        WHERE s.is_active = 1
    """).fetchall()
    
    today = datetime.today()
    today_str = today.strftime("%Y-%m-%d")
    in_30_days = today + timedelta(days=30)
    
    upcoming_costs = []
    projected_monthly_total = 0.0
    categories = cursor.execute("SELECT * FROM categories").fetchall()
    category_totals = {c["name"]: 0.0 for c in categories}
    
    for sub in subs:
        sub_id = sub["id"]
        due_date_str = sub["next_due_date"]
        interval = sub["interval_type"]
        p_type = sub["payment_type"]
        
        if p_type in ["Dauerauftrag", "Einzugsermächtigung"]:
            while due_date_str < today_str:
                due_date_str = get_next_due_date(due_date_str, interval)
                cursor.execute("UPDATE subscriptions SET next_due_date = ? WHERE id = ?", (due_date_str, sub_id))
                db.commit()
        
        due_date_str = adjust_to_bank_day(due_date_str)
        
        amount = sub["amount"]
        cat_name = sub["category_name"] or "Sonstige"
        
        monthly_val = 0.0
        if interval == 'weekly':
            monthly_val = amount * 4.33
            projected_monthly_total += monthly_val
        elif interval == 'monthly':
            monthly_val = amount
            projected_monthly_total += monthly_val
        elif interval == 'yearly':
            monthly_val = amount / 12.0
            projected_monthly_total += monthly_val
            
        if cat_name in category_totals:
            category_totals[cat_name] += monthly_val
        else:
            category_totals[cat_name] = monthly_val
            
        try:
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
            if today <= due_date <= in_30_days:
                upcoming_costs.append({
                    "id": sub_id,
                    "name": sub["name"],
                    "amount": amount,
                    "due_date": due_date_str,
                    "category": cat_name
                })
        except ValueError:
            pass
            
    updated_subs = cursor.execute("""
        SELECT s.*, c.name as category_name, c.color 
        FROM subscriptions s 
        LEFT JOIN categories c ON s.category_id = c.id 
        WHERE s.is_active = 1
    """).fetchall()
    
    return {
        "projected_monthly_total": round(projected_monthly_total, 2),
        "upcoming_costs": upcoming_costs,
        "subscriptions": [dict(s) for s in updated_subs],
        "category_distribution": category_totals,
        "categories": [dict(c) for c in categories]
    }

@app.get("/api/export/csv")
def export_csv(db: sqlite3.Connection = Depends(get_db)):
    subs = db.execute("""
        SELECT s.name, s.amount, s.interval_type, s.payment_type, s.next_due_date, c.name as category_name
        FROM subscriptions s 
        LEFT JOIN categories c ON s.category_id = c.id 
        WHERE s.is_active = 1
        ORDER BY s.next_due_date ASC
    """).fetchall()
    
    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')
    writer.writerow(["Name", "Betrag (€)", "Intervall", "Zahlungsart", "Nächste Fälligkeit", "Kategorie"])
    
    for s in subs:
        writer.writerow([s["name"], f"{s['amount']:.2f}".replace('.', ','), s["interval_type"], s["payment_type"], s["next_due_date"], s["category_name"]])
    
    output.seek(0)
    response = StreamingResponse(iter([output.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename=abo-report-{datetime.now().strftime('%Y-%m')}.csv"
    return response

@app.get("/api/export/pdf")
def export_pdf(db: sqlite3.Connection = Depends(get_db)):
    subs = db.execute("""
        SELECT s.name, s.amount, s.interval_type, s.payment_type, s.next_due_date, c.name as category_name
        FROM subscriptions s 
        LEFT JOIN categories c ON s.category_id = c.id 
        WHERE s.is_active = 1
        ORDER BY s.next_due_date ASC
    """).fetchall()
    
    total = db.execute("SELECT SUM(amount) as total FROM subscriptions WHERE is_active = 1").fetchone()["total"] or 0.0

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50, "Smart Sub-Tracker - Abo & Kostenreport")
    
    p.setFont("Helvetica", 10)
    p.drawString(50, height - 70, f"Erstellt am: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    p.drawString(50, height - 85, f"Monatliche Gesamtkosten (Schnitt): {total:.2f} EUR")
    
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, height - 120, "Aktive Abonnements und Fixkosten:")
    
    y = height - 145
    p.setFont("Helvetica-Bold", 9)
    p.drawString(50, y, "Name")
    p.drawString(200, y, "Kategorie")
    p.drawString(300, y, "Betrag")
    p.drawString(370, y, "Art")
    p.drawString(450, y, "Fälligkeit")
    
    y -= 15
    p.setLineWidth(0.5)
    p.line(50, y + 10, width - 50, y + 10)
    
    p.setFont("Helvetica", 9)
    for s in subs:
        if y < 50:
            p.showPage()
            y = height - 50
        p.drawString(50, y, s["name"][:25])
        p.drawString(200, y, str(s["category_name"] or "-")[:18])
        p.drawString(300, y, f"{s['amount']:.2f} EUR")
        p.drawString(370, y, s["payment_type"] or "Überweisung")
        p.drawString(450, y, s["next_due_date"])
        y -= 20
        
    p.save()
    buffer.seek(0)
    
    response = StreamingResponse(buffer, media_type="application/pdf")
    response.headers["Content-Disposition"] = f"attachment; filename=abo-report-{datetime.now().strftime('%Y-%m')}.pdf"
    return response

@app.get("/api/categories")
def get_categories(db: sqlite3.Connection = Depends(get_db)):
    return [dict(c) for c in db.execute("SELECT * FROM categories").fetchall()]

@app.post("/api/categories")
def create_category(cat: CategoryCreate, db: sqlite3.Connection = Depends(get_db)):
    try:
        cursor = db.cursor()
        cursor.execute("INSERT INTO categories (name, color) VALUES (?, ?)", (cat.name, cat.color))
        db.commit()
        return {"status": "success", "id": cursor.lastrowid}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Kategorie existiert bereits.")

@app.delete("/api/categories/{cat_id}")
def delete_category(cat_id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    count = cursor.execute("SELECT COUNT(*) FROM subscriptions WHERE category_id = ?", (cat_id,)).fetchone()[0]
    if count > 0:
        raise HTTPException(status_code=400, detail="Kategorie wird noch von Abos verwendet.")
    cursor.execute("DELETE FROM categories WHERE id = ?", (cat_id,))
    db.commit()
    return {"status": "success"}

@app.post("/api/subscriptions")
def create_subscription(sub: SubscriptionCreate, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    adjusted_due = adjust_to_bank_day(sub.next_due_date)
    cursor.execute("""
        INSERT INTO subscriptions (name, amount, interval_type, category_id, start_date, next_due_date, payment_type, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, 1)
    """, (sub.name, sub.amount, sub.interval_type, sub.category_id, sub.start_date, adjusted_due, sub.payment_type))
    db.commit()
    return {"status": "success", "id": cursor.lastrowid}

@app.put("/api/subscriptions/{sub_id}")
def update_subscription(sub_id: int, sub: SubscriptionUpdate, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    adjusted_due = adjust_to_bank_day(sub.next_due_date)
    cursor.execute("""
        UPDATE subscriptions 
        SET name = ?, amount = ?, interval_type = ?, category_id = ?, next_due_date = ?, payment_type = ?
        WHERE id = ?
    """, (sub.name, sub.amount, sub.interval_type, sub.category_id, adjusted_due, sub.payment_type, sub_id))
    db.commit()
    return {"status": "success"}

@app.post("/api/pay/{sub_id}")
def mark_as_paid(sub_id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    sub = cursor.execute("SELECT * FROM subscriptions WHERE id = ?", (sub_id,)).fetchone()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    today_str = datetime.today().strftime("%Y-%m-%d")
    
    cursor.execute("""
        INSERT INTO payment_history (subscription_id, amount, paid_date, status)
        VALUES (?, ?, ?, 'paid')
    """, (sub_id, sub["amount"], today_str))
    
    next_due = get_next_due_date(sub["next_due_date"], sub["interval_type"])
    next_due = adjust_to_bank_day(next_due)
            
    cursor.execute("""
        UPDATE subscriptions SET next_due_date = ? WHERE id = ?
    """, (next_due, sub_id))
    
    db.commit()
    return {"status": "success", "new_due_date": next_due}

@app.get("/api/report/markdown")
def generate_markdown_report(db: sqlite3.Connection = Depends(get_db)):
    data = db.execute("SELECT SUM(amount) as total FROM subscriptions WHERE is_active = 1").fetchone()
    total = data["total"] or 0.0
    
    subs = db.execute("""
        SELECT s.name, s.amount, s.interval_type, s.next_due_date, s.payment_type, c.name as category_name
        FROM subscriptions s 
        LEFT JOIN categories c ON s.category_id = c.id 
        WHERE s.is_active = 1
        ORDER BY s.next_due_date ASC
    """).fetchall()
    
    report = f"""# 📊 Monatlicher Abo- & Kostenreport
**Erstellt am:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 💡 Kennzahlen & Prognose
* **Monatliche Gesamtkosten (Schnitt):** {total:.2f} €
* **Aktive Abos / Fixkosten:** {len(subs)} Einträge

## 📋 Aktive Abonnements
| Name | Kategorie | Betrag | Intervall | Zahlungsart | Nächste Fälligkeit |
| :--- | :--- | :--- | :--- | :--- | :--- |
"""
    for s in subs:
        report += f"| {s['name']} | {s['category_name']} | {s['amount']:.2f} € | {s['interval_type']} | {s['payment_type']} | {s['next_due_date']} |\n"
        
    return {"markdown": report}
