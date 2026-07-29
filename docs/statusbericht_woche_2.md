
# Statusbericht – Woche 2

**Projekt:** Kfz Insurance Risk & Pure Premium Intelligence Platform
**Berichtszeitraum:** Technisches Arbeitspaket Woche 2, vorgezogen bearbeitet vom 27.07.2026 bis 30.07.2026
**Stand:** 30.07.2026
**Gesamtarbeitszeit:** Wird nach Abschluss der Zeiterfassung ergänzt

## 1. Aktueller Projektstand

Im zweiten technischen Arbeitspaket wurden die Datenaufnahme und die systematischen Datenqualitätsprüfungen für die beiden freMTPL2-Datensätze umgesetzt.

Für die Datensätze `freMTPL2freq` und `freMTPL2sev` wurde eine wiederholbar ausführbare Ingestion-Pipeline entwickelt. Die unveränderten Quelldateien werden im Raw Layer gespeichert und mithilfe von Dateigrößen und SHA256-Prüfsummen gegen das Source Manifest validiert.

Die Ingestion-Pipeline erfasst zusätzlich die Datensatzversion, den Ladezeitpunkt, die Zeilenanzahl, die Spaltenliste und die Datentypen. Die erwarteten Spalten und Datentypen werden für beide Datensätze automatisch überprüft.

Daneben wurden neun automatisierte Data-Quality-Prüfungen entwickelt. Die Ergebnisse werden standardisiert als `PASS`, `WARN` oder `FAIL` ausgegeben und dauerhaft in einer JSONL-Datei gespeichert. Jeder Prüflauf erhält eine eindeutige `run_id` und einen gemeinsamen UTC-Zeitstempel.

Die Datenbereinigung, die Erstellung des Curated Layers, die Severity-Aggregation für das analytische Datenmodell und die Übernahme der Ergebnisse in PostgreSQL wurden noch nicht begonnen.

## 2. Abgeschlossene Arbeiten

- Ingestion-Pipeline in `src/ingestion/fetch_openml.py` entwickelt und erfolgreich getestet
- Frequency- und Severity-Datensatz aus den offiziellen OpenML-Quellen verarbeitet
- Unveränderte Parquet-Dateien im Raw Layer gespeichert
- Vorhandene Rohdateien anhand ihrer Dateigrößen und SHA256-Prüfsummen validiert
- Kontrollierte alternative Datenbeschaffung für den Fall eines OpenML-HTTP-504-Fehlers umgesetzt
- Datensatzversionen für `freMTPL2freq` und `freMTPL2sev` im Source Manifest dokumentiert
- Ingestion-Metadaten mit Ladezeitpunkt, Zeilenanzahl, Spaltenliste und Datentypen erstellt
- Vollständige Spalten- und Datentypprüfung für beide Datensätze implementiert
- Fehlerbehandlung mit `try/except` ergänzt
- Strukturiertes Logging mit INFO-, WARNING-, ERROR- und Exception-Meldungen umgesetzt
- Pipeline-Starts und Validierungsergebnisse in `pipeline_runs.jsonl` gespeichert
- Ingestion-Pipeline mehrfach ausgeführt und identische fachliche Ergebnisse bestätigt
- Neun automatisierte Data-Quality-Prüfungen in `src/data_quality/checks.py` entwickelt
- Fehlende Werte in Frequency und Severity geprüft
- Gültigkeitsbereich von `Exposure` geprüft
- Auffällig hohe und fachlich ungültige `ClaimNb`-Werte geprüft
- Einzelne und auf Policenebene aggregierte Schadenbeträge geprüft
- Anzahl der Severity-Datensätze mit `ClaimNb` verglichen
- Orphan-Severity-Datensätze identifiziert
- Frequency- und Severity-Daten auf potenzielle Duplikate geprüft
- Join-Kardinalität zwischen Frequency und Severity geprüft
- Data-Quality-Ergebnisse mit einer einheitlichen Ergebnisstruktur versehen
- DQ-Ergebnisse dauerhaft in `dq_check_results.jsonl` gespeichert
- DQ-Ergebnisse um `run_id`, `table_name`, `affected_rows`, `affected_pct`, `severity`, `status`, `executed_at` und `description` erweitert
- Deutschen Datenqualitätsbericht in `docs/data_quality_report.md` erstellt
- Änderungen mit Git versioniert und in das GitHub-Repository übertragen

## 3. Technische Probleme und Lösungen

### OpenML-Metadaten-API nicht erreichbar

Die OpenML-Metadaten-API antwortete während der Datenbeschaffung wiederholt mit HTTP 504. Eine ausschließlich von der API abhängige Pipeline wäre deshalb nicht zuverlässig ausführbar gewesen.

**Lösung:**
Die offiziellen statischen OpenML-Parquet-Dateien wurden als kontrollierter alternativer Zugriffsweg verwendet. Die Herkunft der Dateien, OpenML-Datensatz-IDs, Datensatzversionen, Quell-URLs, Dateigrößen und SHA256-Prüfsummen sind im Source Manifest dokumentiert.

Die Ingestion-Pipeline verwendet bereits vorhandene lokale Dateien nur dann, wenn Dateigröße und SHA256-Prüfsumme mit dem Manifest übereinstimmen.

### Nachvollziehbarkeit wiederholter Pipeline-Läufe

Die Pipeline musste mehrfach ausführbar sein, ohne die Rohdaten unkontrolliert zu verändern oder unterschiedliche Ergebnisse zu erzeugen.

**Lösung:**
Die Quelldateien werden vor jeder Verwendung geprüft. Mehrere Pipeline-Läufe ergaben dieselben Zeilenzahlen, Schemas, Datentypen und Validierungsergebnisse. Jeder Lauf wird separat und append-basiert in `pipeline_runs.jsonl` dokumentiert.

### Dauerhafte Speicherung der Data-Quality-Ergebnisse

Die Data-Quality-Prüfungen gaben ihre Ergebnisse zunächst nur im Terminal aus. Dadurch wären frühere Prüfläufe nicht dauerhaft nachvollziehbar gewesen.

**Lösung:**
Die neun Prüfergebnisse werden nun pro Lauf als separate JSONL-Datensätze gespeichert. Alle Ergebnisse eines Laufs besitzen dieselbe `run_id` und denselben Ausführungszeitpunkt. Die Felder wurden so vorbereitet, dass sie im nächsten Arbeitspaket in die PostgreSQL-Tabelle `dq_check_results` übernommen werden können.

### Trennung von Datenqualitätsprüfung und Datenbereinigung

Mehrere festgestellte Werte sind auffällig oder für einzelne Modellarten ungeeignet. Eine automatische Veränderung im Raw Layer würde jedoch die Nachvollziehbarkeit der Quelldaten beeinträchtigen.

**Lösung:**
Die Rohdaten bleiben unverändert. Die festgestellten Probleme werden dokumentiert und erst im Curated Layer nach begründeten Regeln behandelt. Potenzielle Duplikate werden nicht automatisch gelöscht.

## 4. Ergebnisse und Datenqualitätsbefunde

Die Frequency-Tabelle enthält 678.013 Policen und 12 Spalten. Die Severity-Tabelle enthält 26.639 Schadenzeilen und 2 Spalten.

Insgesamt wurden neun automatisierte Prüfungen ausgeführt:

- 4 Prüfungen mit Status `PASS`
- 2 Prüfungen mit Status `WARN`
- 3 Prüfungen mit Status `FAIL`

Die wichtigsten Ergebnisse sind:

- In beiden Datensätzen wurden keine fehlenden Werte festgestellt.
- Es wurden keine nicht positiven `Exposure`-Werte gefunden.
- 1.224 Policen besitzen einen `Exposure`-Wert größer als 1.
- 9 Policen besitzen einen `ClaimNb`-Wert größer als 4.
- Der höchste festgestellte `ClaimNb`-Wert beträgt 16.
- Es wurden keine negativen oder nicht positiven einzelnen Schadenbeträge gefunden.
- Es wurden keine Policen mit einem aggregierten `total_claim_amount <= 0` gefunden.
- Der höchste einzelne Schadenbetrag beträgt 4.075.400,56.
- 9.116 Policen mit einem gemeldeten Schaden besitzen keinen entsprechenden Severity-Datensatz.
- Bei einer weiteren Police stimmt `ClaimNb` nicht mit der vorhandenen Anzahl der Severity-Zeilen überein.
- In der Severity-Tabelle wurden 195 Orphan-Zeilen gefunden, die keiner Frequency-Police zugeordnet werden können.
- Die 195 Orphan-Zeilen betreffen 6 unterschiedliche Policy-IDs.
- In der Severity-Tabelle wurden 255 potenzielle Duplikatzeilen in 241 Gruppen festgestellt.
- In der Frequency-Tabelle wurden keine doppelten Policy-IDs festgestellt.
- Die erwartete One-to-Many-Kardinalität des Frequency-Severity-Joins wurde bestätigt.

Die Befunde wurden nicht automatisch bereinigt. Die fachlichen Entscheidungen für den Curated Layer sind im Datenqualitätsbericht dokumentiert.

## 5. Offene Aufgaben

- Gesamtarbeitszeit anhand der Excel-Zeiterfassung ergänzen
- Severity-Daten vor dem Join auf Ebene von `IDpol` aggregieren
- `total_claim_amount` und `claim_record_count` für jede Police berechnen
- Festgelegte Bereinigungsentscheidungen im Curated Layer umsetzen
- `Exposure > 1` auf 1,0 begrenzen und mit `exposure_capped` kennzeichnen
- Auffällig hohe `ClaimNb`-Werte beibehalten und mit `high_claim_count` kennzeichnen
- Orphan-Severity-Datensätze aus dem Curated und Modeling Layer ausschließen
- Potenzielle Duplikate fachlich prüfen und nicht automatisch löschen
- Features für Schadenfrequenz, Schadenhöhe und beobachtete Pure Premium erstellen
- PostgreSQL-Kerntabellen und analytische Views anlegen
- JSONL-Laufdaten in `pipeline_runs` und `dq_check_results` in PostgreSQL übernehmen
- Erst nach Abschluss der Bereinigung und des SQL-Modells mit der EDA beginnen

## 6. Nächste Schritte

Im nächsten technischen Arbeitspaket wird zuerst die Severity-Tabelle vor dem Join auf Ebene von `IDpol` aggregiert. Dabei werden pro Police der gesamte Schadenbetrag als `total_claim_amount` und die Anzahl der vorhandenen Schadenzeilen als `claim_record_count` berechnet.

Anschließend werden die dokumentierten Bereinigungsentscheidungen im Curated Layer umgesetzt. Dazu gehören unter anderem die Begrenzung von `Exposure > 1`, die Kennzeichnung hoher Schadenanzahlen sowie der kontrollierte Ausschluss von Orphan-Severity-Datensätzen.

Danach folgen das Feature Engineering und die Erstellung der PostgreSQL-Kerntabellen `stg_policy`, `stg_claim`, `fact_policy_exposure`, `fact_claim`, `pipeline_runs` und `dq_check_results`.

Die explorative Datenanalyse in `notebooks/03_eda.ipynb` beginnt erst, wenn der Curated Layer und das PostgreSQL-Analysemodell vollständig aufgebaut und technisch geprüft wurden.

## 7. Zusammenfassung

Die wiederholbare Datenaufnahme und die systematische Prüfung der Datenqualität sind einsatzbereit. Beide Rohdatensätze werden unverändert gespeichert, durch Metadaten dokumentiert und technisch gegen das Source Manifest geprüft.

Die neun automatisierten Data-Quality-Prüfungen liefern reproduzierbare und dauerhaft gespeicherte Ergebnisse. Dabei wurden mehrere für die weitere Verarbeitung relevante Datenprobleme festgestellt, insbesondere ungültig hohe Exposure-Werte, fehlende Severity-Informationen, Orphan-Severity-Datensätze und potenzielle Duplikate.

Damit ist das technische Arbeitspaket Ingestion & Data Quality abgeschlossen. Der nächste Projektschritt ist die kontrollierte Severity-Aggregation, Datenbereinigung und Erstellung des PostgreSQL-Analysemodells.
