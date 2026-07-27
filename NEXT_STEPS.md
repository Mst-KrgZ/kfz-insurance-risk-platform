
# NEXT STEPS

**Stand:** 27.07.2026

## 1. Aktueller Projektstatus

Das technische Grundgerüst des Projekts ist eingerichtet.
Die Rohdaten wurden erfolgreich beschafft, geprüft und in einem ersten Notebook geöffnet.

PostgreSQL 17 wurde lokal installiert. Für das Projekt wurden die Rolle `kfz_app` und die Datenbank `kfz_insurance` angelegt. Die Verbindung wurde erfolgreich mit `psql`, DBeaver und Power BI getestet.

Die fachlichen Grundlagen wurden in `docs/business_understanding.md` und `docs/data_dictionary.md` dokumentiert.

In PostgreSQL wurden bisher noch keine Tabellen, Views oder Projektdaten angelegt. Die explorative Datenanalyse, die Data-Quality-Prüfungen, die Datenbereinigung und die Modellierung wurden noch nicht begonnen.


## 2. Bereits abgeschlossen

- [X] Privates GitHub-Repository und Projektstruktur eingerichtet
- [X] Virtuelle Python-Umgebung erstellt
- [X] `requirements.txt` angelegt
- [X] OpenML-Datenquelle geprüft und API-Fehler dokumentiert
- [X] Offizielle Parquet-Dateien heruntergeladen
- [X] Dateigrößen und SHA256-Prüfsummen im Source Manifest dokumentiert
- [X] Frequency- und Severity-Datensatz erfolgreich geöffnet
- [X] Grundstruktur und Variablen beider Datensätze geprüft
- [X] `docs/business_understanding.md` erstellt
- [X] `docs/data_dictionary.md` erstellt
- [X] PostgreSQL 17 lokal installiert und getestet
- [X] PostgreSQL-Rolle `kfz_app` erstellt
- [X] PostgreSQL-Datenbank `kfz_insurance` erstellt
- [X] Verbindung mit `psql` erfolgreich geprüft
- [X] Verbindung mit DBeaver erfolgreich geprüft
- [X] Verbindung zwischen Power BI und PostgreSQL erfolgreich geprüft



## 3. Offene Aufgaben vor dem Abschluss der ersten Projektwoche

- [ ] Excel-Zeiterfassung anlegen und bisherige Arbeitsblöcke nachvollziehbar dokumentieren
- [ ] Statusbericht #1 erstellen
- [ ] Git-Status kontrollieren
- [ ] Neue Dokumentationen committen und zu GitHub pushen

## 4. Nächster konkreter Arbeitsschritt

Beim nächsten Einstieg wird zuerst die Zeiterfassung abgeschlossen. Danach wird der erste wöchentliche Statusbericht vorbereitet.

Erst nach Abschluss dieser organisatorischen Aufgaben beginnt die nächste fachliche Phase mit der Datenaufnahme in PostgreSQL und den geplanten Data-Quality-Prüfungen.

## 5. Wichtige technische Hinweise

- Die Rohdaten befinden sich lokal im Verzeichnis `data/raw` und werden nicht zu GitHub hochgeladen.
- Für Parquet-Dateien wird aktuell `fastparquet` verwendet.
- Die PostgreSQL-Datenbank heißt `kfz_insurance`.
- Die PostgreSQL-Rolle heißt `kfz_app`.
- Passwörter dürfen nicht in Projektdateien oder GitHub gespeichert werden.
- Die Severity-Daten müssen vor einem Join nach `IDpol` aggregiert werden.
- Die Frequency-Daten müssen bei späteren Joins vollständig erhalten bleiben.
