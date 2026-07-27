
# Statusbericht – Woche 1

**Projekt:** Kfz Insurance Risk & Pure Premium Intelligence Platform
**Berichtszeitraum:** Projektstart am 27.07.2026
**Stand:** 27.07.2026
**Gesamtarbeitszeit:** Wird nach Abschluss der Zeiterfassung ergänzt

## 1. Aktueller Projektstand

In der ersten Projektphase wurde das technische und organisatorische Grundgerüst des Abschlussprojekts eingerichtet.

Das private GitHub-Repository, die lokale Projektstruktur und die virtuelle Python-Umgebung wurden vorbereitet. Die beiden freMTPL2-Datensätze wurden beschafft, technisch geprüft und erstmals in Python geöffnet.

Zusätzlich wurden die fachlichen Grundlagen des Projekts dokumentiert. PostgreSQL wurde lokal installiert und für das Projekt konfiguriert. Die Verbindung zur Projektdatenbank wurde erfolgreich mit `psql`, DBeaver und Power BI getestet.

Die explorative Datenanalyse, die Data-Quality-Prüfungen, die Datenbereinigung und die Modellierung wurden noch nicht begonnen.

## 2. Abgeschlossene Arbeiten

- Privates GitHub-Repository erstellt und mit dem lokalen Projekt verbunden
- Grundlegende Projekt- und Ordnerstruktur eingerichtet
- Virtuelle Python-Umgebung erstellt
- Benötigte Python-Pakete installiert und in `requirements.txt` dokumentiert
- OpenML-Datenquelle untersucht und wiederholte Serverfehler dokumentiert
- Offizielle freMTPL2-Parquet-Dateien heruntergeladen
- Dateigrößen und SHA256-Prüfsummen in einem Source Manifest dokumentiert
- Frequency- und Severity-Datensatz mit Python geöffnet
- Struktur, Spalten und erste Datensätze geprüft
- Fachliche Projektbeschreibung in `business_understanding.md` erstellt
- Variablen und geplante Prüfungen in `data_dictionary.md` dokumentiert
- PostgreSQL 17 lokal installiert
- Projektspezifische Rolle `kfz_app` angelegt
- Projektdatenbank `kfz_insurance` erstellt
- Datenbankverbindung mit `psql` erfolgreich getestet
- Datenbankverbindung mit DBeaver erfolgreich getestet
- Verbindung zwischen Power BI und PostgreSQL erfolgreich getestet
- Aktuellen Projektstand und nächste Schritte in `NEXT_STEPS.md` dokumentiert

## 3. Technische Probleme und Lösungen

### OpenML-Serverfehler

Beim Zugriff auf die OpenML-Metadaten und Download-Endpunkte trat wiederholt ein HTTP-504-Fehler auf.

**Lösung:**
Die offiziellen statischen Parquet-Dateien wurden direkt heruntergeladen. Herkunft, Dateigrößen und SHA256-Prüfsummen wurden in `data/raw/source_manifest.json` dokumentiert.

### Probleme mit Python-Bibliotheken

Windows Smart App Control blockierte einzelne DLL-Dateien von `pandas` und `pyarrow`. Dadurch konnten bestimmte Paketversionen nicht zuverlässig verwendet werden.

**Lösung:**
`pyarrow` wurde entfernt, `pandas` wurde auf Version `2.2.3` festgelegt und für das Lesen der Parquet-Dateien wird aktuell `fastparquet` verwendet.

### Fehlgeschlagene PostgreSQL-Initialisierung

Bei der ersten PostgreSQL-Installation wurde `initdb.exe` durch Smart App Control blockiert. Deshalb wurde kein Datenbank-Cluster initialisiert und kein PostgreSQL-Dienst erstellt.

**Lösung:**
Smart App Control wurde deaktiviert, der Rechner neu gestartet und die unvollständige PostgreSQL-Installation vollständig entfernt. Anschließend wurde PostgreSQL erneut mit Administratorrechten installiert. Der Dienst `postgresql-x64-17` läuft seitdem erfolgreich.

### Power-BI-Test ohne vorhandene Tabellen

Die Verbindung zwischen Power BI und PostgreSQL konnte erfolgreich hergestellt werden. Da in der Datenbank noch keine Tabellen vorhanden sind, wurden noch keine Projektdaten geladen.

Bei einem Test wurde nur das technische Navigationselement der PostgreSQL-Verbindung geladen. Dieses enthielt keine Versicherungsdaten und wurde nicht gespeichert.


## 3. Technische Probleme und Lösungen

### OpenML-Serverfehler

Beim Zugriff auf die OpenML-Metadaten und Download-Endpunkte trat wiederholt ein HTTP-504-Fehler auf.

**Lösung:**
Die offiziellen statischen Parquet-Dateien wurden direkt heruntergeladen. Herkunft, Dateigrößen und SHA256-Prüfsummen wurden in `data/raw/source_manifest.json` dokumentiert.

### Probleme mit Python-Bibliotheken

Windows Smart App Control blockierte einzelne DLL-Dateien von `pandas` und `pyarrow`. Dadurch konnten bestimmte Paketversionen nicht zuverlässig verwendet werden.

**Lösung:**
`pyarrow` wurde entfernt, `pandas` wurde auf Version `2.2.3` festgelegt und für das Lesen der Parquet-Dateien wird aktuell `fastparquet` verwendet.

### Fehlgeschlagene PostgreSQL-Initialisierung

Bei der ersten PostgreSQL-Installation wurde `initdb.exe` durch Smart App Control blockiert. Deshalb wurde kein Datenbank-Cluster initialisiert und kein PostgreSQL-Dienst erstellt.

**Lösung:**
Smart App Control wurde deaktiviert, der Rechner neu gestartet und die unvollständige PostgreSQL-Installation vollständig entfernt. Anschließend wurde PostgreSQL erneut mit Administratorrechten installiert. Der Dienst `postgresql-x64-17` läuft seitdem erfolgreich.

### Power-BI-Test ohne vorhandene Tabellen

Die Verbindung zwischen Power BI und PostgreSQL konnte erfolgreich hergestellt werden. Da in der Datenbank noch keine Tabellen vorhanden sind, wurden noch keine Projektdaten geladen.

Bei einem Test wurde nur das technische Navigationselement der PostgreSQL-Verbindung geladen. Dieses enthielt keine Versicherungsdaten und wurde nicht gespeichert.

## 4. Offene Aufgaben

- Excel-Zeiterfassung anlegen und die bisherigen Arbeitsblöcke nachvollziehbar dokumentieren
- Gesamtarbeitszeit für die erste Projektwoche ergänzen
- PostgreSQL-Schema und Projekttabellen planen
- Frequency- und Severity-Daten für die spätere Datenaufnahme vorbereiten
- Geplante Data-Quality-Prüfungen konkretisieren
- Explorative Datenanalyse vorbereiten

## 5. Nächste Schritte

Zuerst wird die Zeiterfassung für die bisherige Projektarbeit abgeschlossen. Danach wird die Gesamtarbeitszeit in diesem Statusbericht ergänzt.

Im nächsten fachlichen Arbeitspaket wird die Aufnahme der Frequency- und Severity-Daten in PostgreSQL vorbereitet. Dabei werden zunächst das relationale Datenmodell, die benötigten Tabellen sowie die spätere Aggregation der Severity-Daten auf Ebene von `IDpol` definiert.

Anschließend beginnen die geplanten Data-Quality-Prüfungen. Die explorative Datenanalyse, die Datenbereinigung und die Modellierung folgen erst nach Abschluss dieser vorbereitenden Schritte.

## 6. Zusammenfassung

Die grundlegende technische Infrastruktur des Projekts ist einsatzbereit. Die Datenquellen wurden gesichert und dokumentiert, die fachlichen Grundlagen wurden beschrieben und die Verbindungen zwischen PostgreSQL, DBeaver und Power BI wurden erfolgreich getestet.

Trotz mehrerer technischer Probleme konnte die erste Projektphase erfolgreich abgeschlossen werden. Die nächsten Arbeiten konzentrieren sich auf die nachvollziehbare Zeiterfassung, die Datenbankstruktur und die systematischen Data-Quality-Prüfungen.
