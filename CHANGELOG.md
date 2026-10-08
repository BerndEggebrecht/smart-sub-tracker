# 📜 Changelog

Alle nennenswerten Änderungen am **Smart Sub-Tracker** werden in dieser Datei dokumentiert.

## [1.7.0] - 2026-09-28
### Hinzugefügt
* Manueller Test-Button im Dashboard zum direkten Auslösen von Test-E-Mails.
* Sichere Passwort-Verwaltung und Konfiguration über `.env`-Dateien (`python-dotenv`).

## [1.6.0] - 2026-09-27
### Hinzugefügt
* Integrierter E-Mail-Benachrichtigungsdienst via SMTP (mit SSL/TLS-Unterstützung) für anstehende und überfällige Zahlungen.

## [1.5.0] - 2026-09-26
### Hinzugefügt
* Automatischer Startup-Check, der fällige Zahlungen erkennt und native Desktop-Benachrichtigungen (`notify-send`) auf Kali Linux auslöst.

## [1.4.0] - 2026-09-25
### Hinzugefügt
* Professioneller PDF-Report-Export (generiert mit ReportLab).
* CSV-Export-Endpunkt für die einfache Weiterverarbeitung in Tabellenkalkulationen (Excel/LibreOffice Calc).

## [1.3.0] - 2026-09-24
### Hinzugefügt
* Bearbeiten-Funktion (`✏️`) für bestehende Abonnements direkt in der Tabelle.
* Dynamisches Umschalten des Erfassungsformulars zwischen Neu-Erstellung und Bearbeitung.

## [1.2.0] - 2026-09-22
### Hinzugefügt
* Auswahl der Zahlungsart (*Überweisung*, *Dauerauftrag*, *Einzugsermächtigung*).
* Automatische Banktags-Berechnung (überspringt Samstage und Sonntage).
* Intelligenter Stichtags-Sprung für Daueraufträge und Einzugsermächtigungen in der Vergangenheit.
* Visuelle Status-Ampel (Grün, Gelb, Rot/Blinkend) in der Abo-Tabelle.

## [1.1.0] - 2026-09-20
### Hinzugefügt
* Dedizierte Kachel zur Verwaltung von Kategorien (inklusive individueller Farbgestaltung und Schutz vor dem Löschen von genutzten Kategorien).
* Dynamische Anbindung der Kategorien an das Abo-Formular und das Chart.js-Diagramm.

## [1.0.0] - 2026-09-18
### Hinzugefügt
* Initiale Projektstruktur mit FastAPI-Backend und SQLite-Datenbank.
* Grundlegendes Dashboard mit Echtzeit-Uhr, Chart.js-Kostenverteilung und 30-Tage-Fälligkeits-Timeline.
* Markdown-Report-Export.
