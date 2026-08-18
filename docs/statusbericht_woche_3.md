
# Statusbericht – Woche 3

**Projekt:** Kfz Insurance Risk & Pure Premium Intelligence Platform
**Berichtszeitraum:** 17.08.2026 – 23.08.2026
**Stand:** 18.08.2026
**Gesamtarbeitszeit:** Wird nach Abschluss der Zeiterfassung ergänzt

## 1. Aktueller Projektstand

In der dritten Projektphase wurden die Datenbereinigung, das Feature Engineering
und das analytische PostgreSQL-Datenmodell umgesetzt.

Die Severity-Daten wurden zunächst auf Policenebene aggregiert und anschließend
kontrolliert mit dem Frequency-Datensatz verbunden. Die zuvor identifizierten
Datenqualitätsprobleme wurden dabei nicht durch pauschale Löschungen oder
Imputationen bereinigt, sondern durch nachvollziehbare fachliche Regeln und
Indikatorspalten behandelt.

Auf dieser Grundlage wurde ein policenbasierter Curated-Datensatz mit
678.013 Zeilen und 25 Spalten erstellt.

Zusätzlich wurden sechs Kerntabellen in PostgreSQL aufgebaut und über einen
Python-basierten Ladeprozess befüllt. Für die spätere explorative Analyse und
die Power-BI-Anbindung wurden drei analytische Views erstellt.

Die Datenaufbereitung und das SQL-Datenmodell sind damit für die nächste
Projektphase vorbereitet. Die explorative Datenanalyse und die Modellierung
wurden noch nicht begonnen.

## 2. Abgeschlossene Arbeiten

- Severity-Daten vor dem policenbasierten Join nach `IDpol` aggregiert
- `total_claim_amount` und `claim_record_count` je Police berechnet
- 195 verwaiste Severity-Zeilen aus sechs Policen identifiziert und aus der
  Curated- und analytischen Claim-Schicht ausgeschlossen
- `Exposure > 1` in der Curated-Schicht auf 1,0 begrenzt
- 1.224 betroffene Policen mit `exposure_capped` gekennzeichnet
- Neun Policen mit `ClaimNb > 4` unverändert beibehalten und mit
  `high_claim_count` gekennzeichnet
- 9.116 Policen mit gemeldetem Schaden, aber fehlender Severity-Information,
  mit `missing_severity` gekennzeichnet
- Unbekannte Schadenhöhen ausdrücklich nicht mit null imputiert
- Eine Police mit abweichender Schadenanzahl zwischen Frequency und Severity
  mit `claim_count_mismatch` gekennzeichnet
- Potenziell doppelte Severity-Zeilen nicht automatisch entfernt
- Kategorische Merkmale auf fehlende und sehr seltene Kategorien geprüft;
  keine zusätzliche Zusammenfassung zu `Unknown` oder `Other` erforderlich
- Beobachtete Schadenfrequenz als `ClaimNb / Exposure` berechnet
- Beobachtete Severity für gültige Schadenpolicen berechnet
- Beobachtete Pure Premium als `total_claim_amount / Exposure` berechnet
- Fahrer-Altersgruppen erstellt
- Fahrzeugalter-Gruppen erstellt
- Bonus-Malus-Segmente erstellt
- Logarithmisch transformiertes Density-Merkmal erstellt
- Feature-Engineering-Funktionen zu einer gemeinsamen Pipeline zusammengeführt
- Policenbasierten Curated-Datensatz `policy_curated.pq` mit
  678.013 Zeilen und 25 Spalten erstellt
- Curated-Datensatz auf Zeilenanzahl, eindeutige `IDpol`, Exposure-Grenzen,
  Datentypen und DQ-Indikatoren geprüft
- PostgreSQL-Schema mit sechs Kerntabellen erstellt:
  `stg_policy`, `stg_claim`, `fact_policy_exposure`, `fact_claim`,
  `pipeline_runs` und `dq_check_results`
- PostgreSQL-Anbindung aus Python mit Psycopg eingerichtet
- `stg_policy` mit 678.013 Frequency-Zeilen geladen
- `stg_claim` mit 26.639 Severity-Zeilen geladen
- `fact_policy_exposure` mit 678.013 Curated-Policen geladen
- `fact_claim` mit 26.444 gültig verknüpfbaren Claim-Level-Zeilen geladen
- Drei vorhandene Pipeline-Läufe in `pipeline_runs` übernommen
- 27 historische Data-Quality-Ergebnisse in `dq_check_results` übernommen
- Ältere und neuere DQ-JSONL-Schemata beim Laden vereinheitlicht
- JSON-Strukturen in PostgreSQL als `JSONB` gespeichert
- Geladene Tabellen mit SQL-Abfragen auf Zeilenanzahl und fachliche
  Konsistenz geprüft
- Analytische View `vw_policy_risk_base` mit 678.013 Policen erstellt
- Analytische View `vw_claim_analysis` mit 26.444 Claim-Level-Zeilen erstellt
- Analytische View `vw_dq_summary` mit den neun aktuellsten
  Data-Quality-Prüfergebnissen erstellt
- `docs/data_quality_report.md` an die tatsächlich umgesetzten
  Bereinigungsentscheidungen und Curated-Ergebnisse angepasst

## 3. Technische Probleme und Lösungen

### PostgreSQL-Kommando in Windows nicht direkt verfügbar

Der Befehl `psql` konnte zunächst in der Windows-Kommandozeile nicht gefunden
werden, da das PostgreSQL-Bin-Verzeichnis nicht im System-PATH eingetragen war.

**Lösung:**
`psql.exe` wurde über den vollständigen Installationspfad von PostgreSQL 17
aufgerufen. Die Verbindung zur Projektdatenbank `kfz_insurance` und zum
Projektbenutzer `kfz_app` konnte damit erfolgreich geprüft werden.

### Fehlender PostgreSQL-Treiber in der Python-Umgebung

In der virtuellen Python-Umgebung war zunächst kein PostgreSQL-Treiber
installiert.

**Lösung:**
Psycopg 3 wurde installiert und in `requirements.txt` dokumentiert.
Die Datenbankverbindung wird über den Benutzer `kfz_app` aufgebaut. Das
Passwort wird beim Start des Ladeprozesses abgefragt und nicht im Quellcode
gespeichert.

### Behandlung von NULL-Werten beim PostgreSQL-Import

Beim Laden des Curated-Datensatzes mussten unbekannte Schadenhöhen als echte
SQL-NULL-Werte erhalten bleiben.

**Lösung:**
Beim CSV-basierten PostgreSQL-`COPY`-Prozess wird für fehlende Werte explizit
`\N` verwendet. Dadurch bleiben insbesondere die 9.116 unbekannten
Schadenhöhen als NULL erhalten und werden nicht fälschlicherweise als null
Euro interpretiert.

### Datentyp von `affected_rows`

Beim ersten Import der Data-Quality-Historie wurde `affected_rows` durch
fehlende Werte von Pandas als Float-Spalte interpretiert. Dadurch entstanden
Werte wie `0.0`, die nicht direkt in die PostgreSQL-Spalte vom Typ `INTEGER`
geladen werden konnten.

**Lösung:**
Die Spalte wurde vor dem Export in den nullable Pandas-Datentyp `Int64`
umgewandelt. Fehlende Werte bleiben dadurch erhalten und vorhandene
Zeilenanzahlen werden als Ganzzahlen an PostgreSQL übergeben.

## 4. Offene Aufgaben

- Explorative Datenanalyse im Notebook `03_eda.ipynb` durchführen
- Datenstruktur, Verteilungen, fehlende Werte und Duplikate im Notebook
  zusätzlich interaktiv untersuchen und dokumentieren
- Schadenfrequenz nach Fahrer- und Fahrzeugmerkmalen analysieren
- Region, Area, Density, BonusMalus und Kraftstoffart untersuchen
- Schadenhöhenverteilung und Einfluss von Großschäden analysieren
- Observed Pure Premium nach relevanten Segmenten auswerten
- Tatsächliche EDA-Kennzahlen und zentrale fachliche Erkenntnisse dokumentieren
- Durchgängige Kette bis zu einem ersten einfachen Poisson-Modell vorbereiten

## 5. Nächste Schritte

Im nächsten Arbeitspaket beginnt die geschäftsorientierte explorative
Datenanalyse im Notebook `notebooks/03_eda.ipynb`.

Zunächst wird der aufbereitete Datensatz erneut interaktiv untersucht. Dazu
werden unter anderem Struktur, Datentypen, deskriptive Statistiken, fehlende
Werte, Duplikate, Verteilungen und auffällige Werte geprüft.

Anschließend werden die Beziehungen zwischen zentralen Risikomerkmalen und
Schadenfrequenz, Schadenhöhe sowie beobachteter Pure Premium analysiert.
Besonderes Augenmerk liegt auf Fahrer- und Fahrzeugalter, BonusMalus, Region,
Area, Density, Kraftstoffart sowie der stark rechtsschiefen Verteilung der
Schadenhöhen.

Die Ergebnisse werden mit tatsächlichen Kennzahlen und geeigneten
Visualisierungen dokumentiert und bilden die Grundlage für die anschließende
Modellierung.

## 6. Zusammenfassung

Die Bereinigungs- und SQL-Phase wurde erfolgreich abgeschlossen.

Die zuvor identifizierten Datenqualitätsprobleme wurden durch nachvollziehbare
Regeln behandelt, ohne die Raw-Daten zu verändern. Ein policenbasierter
Curated-Datensatz mit 678.013 Policen und 25 Spalten wurde erstellt und
erfolgreich in PostgreSQL überführt.

Das PostgreSQL-Datenmodell umfasst sechs Kerntabellen sowie analytische Views
für policenbasierte Analysen, Claim-Level-Auswertungen und
Data-Quality-Monitoring.

Damit steht eine reproduzierbare und analysefähige Datenbasis für die
explorative Analyse und die späteren Frequency-, Severity- und
Pure-Premium-Modelle zur Verfügung.
