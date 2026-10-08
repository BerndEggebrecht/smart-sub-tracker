DOCUMENTATION.md
# 📚 Technische Dokumentation

## 🏗️ Architektur & Verzeichnisstruktur
Das Projekt folgt einer modularen Aufteilung im Backend-Frontend-Prinzip:


/opt/subtracker/
│
├── app/
│   ├── __init__.py
│   ├── database.py       # SQLite-Verbindung und Tabelleninitialisierung
│   ├── models.py         # Pydantic-Validierungsmodelle (Create, Update)
│   ├── main.py           # FastAPI-Anwendung, API-Endpunkte & Startup-Logik
│   └── static/
│       └── index.html    # Frontend (Tailwind CSS, Chart.js, Vanilla JS)
│
├── data/
│   └── subscriptions.db  # SQLite-Datenbankdatei (wird automatisch erstellt)
│
├── venv/                 # Python Virtual Environment
├── .env                  # Lokale Umgebungsvariablen (SMTP, Credentials)
├── README.md             # Projektübersicht
├── CHANGELOG.md          # Versionshistorie
└── DOCUMENTATION.md      # Diese Dokumentation

🔌 API-Endpunkte Übersicht
Methode Endpoint                Beschreibung
GET     /                       Liefert die HTML-Oberfläche aus.
GET     /api/dashboard          Liefert alle Kennzahlen, Abos, Kategorien und die 30-Tage-Timeline.
GET     /api/categories         Listet alle Kategorien auf.
POST    /api/categories         Legt eine neue Kategorie an (mit Farbcode).
DELETE  /api/categories/{id}    Löscht eine Kategorie (sofern sie nicht mehr genutzt wird).
POST    /api/subscriptions      Erstellt ein neues Abonnement / Fixkosten-Eintrag.
PUT     /api/subscriptions/{id} Aktualisiert ein bestehendes Abonnement.
POST    /api/pay/{id}           Verbucht eine Zahlung in der Historie und schaltet das Fälligkeitsdatum weiter. 
GET     /api/export/csv         Generiert und lädt den CSV-Export herunter.
GET     /api/export/pdf         Generiert und lädt den PDF-Report herunter.
GET     /api/report/markdown    Liefert den Report im Markdown-Format.
GET     /api/test-email         Sendet manuell eine Test-E-Mail über den konfigurierten SMTP-Server.

⚙️ Kernlogiken
1. Banktags-Berechnung (adjust_to_bank_day)
Wochenenden werden im Abrechnungsprozess automatisch erkannt. Fällt ein Fälligkeitstermin auf einen Samstag oder Sonntag, wird das Datum schrittweise auf den nächsten Werktag (Montag) verschoben.

2. Automatischer Datums-Sprung
Bei Zahlungsarten vom Typ Dauerauftrag oder Einzugsermächtigung prüft das System beim Laden des Dashboards, ob der Stichtag in der Vergangenheit liegt. Ist dies der Fall, wird das Fälligkeitsdatum automatisch so oft um ein Intervall (wöchentlich, monatlich, jährlich) nach vorn verschoben, bis es wieder in der Zukunft liegt.

3. Benachrichtigungs-Daemon
Beim Starten der Anwendung prüft die Funktion check_due_notifications(), ob Abos heute, morgen oder überfällig sind. Treffen Bedingungen zu, wird ein System-Befehl (notify-send) abgesetzt und eine E-Mail über smtplib versendet.
