# 💳 Smart Sub-Tracker

Ein lokaler, datenschutzfreundlicher Abo- und Fixkosten-Tracker, maßgeschneidert für Linux-Umgebungen (z. B. Kali Linux). Entwickelt mit **FastAPI**, **SQLite**, **Tailwind CSS** und **Chart.js**.

---

## ✨ Features
* **Echtzeit-Dashboard & 30-Tage-Prognose:** Visualisierung der monatlichen Gesamtkosten via Chart.js und Timeline der anstehenden Zahlungen.
* **Intelligente Banktags-Logik:** Berücksichtigung von Wochenenden (automatischer Sprung auf den nächsten Werktag) und automatisches Fortschalten bei Daueraufträgen oder Einzugsermächtigungen.
* **Visuelles Status-Ampelsystem:** Sofortige Übersicht über den Status (🟢 Im Zeitplan, 🟡 Bald fällig, 🔴 Überfällig).
* **Kategorien-Verwaltung:** Dynamische Erstellung, Farbanpassung und Zuweisung von Kategorien.
* **Live-Suche & Filter:** Schnelles Durchsuchen und Filtern der Abonnements nach Name und Kategorie.
* **Export-Assistent:** Export als formatierter PDF-Report, strukturierte CSV-Datei oder Markdown-Notiz.
* **Multi-Channel-Benachrichtigungen:** Desktop-Benachrichtigungen (`notify-send`) und automatisierter E-Mail-Versand (via SMTP & `.env`) mit manuellem Test-Button.

---

## 🚀 Schnellstart & Installation

1. **In das Projektverzeichnis wechseln:**
   ```bash
   cd /opt/subtracker
   
Virtuelle Umgebung aktivieren & Abhängigkeiten installieren:
   source venv/bin/activate
   pip install -r requirements.txt
   
Umgebungskonfiguration (.env) anlegen:
Erstelle eine .env-Datei im Stammverzeichnis:

   SMTP_SERVER=mail.gmx.net
   SMTP_PORT=465
   SMTP_USER=deine-email@gmx.de
   SMTP_PASSWORD=dein-app-passwort
   EMAIL_RECIPIENT=empfaenger@gmail.com
   
Server starten:

   ./venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   
Im Browser öffnen:

   Rufe http://127.0.0.1:8000 auf.

## 🛠️ Tech Stack
* **Backend:** Python, FastAPI, SQLite
* **Frontend:** HTML5, Tailwind CSS, Chart.js
* **System:** Systemd Service / Linux (Kali/Ubuntu)

## 🚀 Schnellstart

1. **Abhängigkeiten installieren:**
   ```bash
   pip install -r requirements.txt
   
Server starten:
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

Im Browser öffnen: 
http://127.0.0.1:8000

📅 Automatischer Report (Cron)
Um monatlich automatisch einen Report zu generieren, füge folgenden Cronjob hinzu (crontab -e):
0 0 1 * * /usr/bin/python3 /opt/subtracker/scripts/cron_report.py
