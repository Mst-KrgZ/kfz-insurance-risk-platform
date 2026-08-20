# NEXT STEPS

**Stand:** 20.08.2026

## 1. Aktueller Projektstatus

Die technischen Arbeitspakete Woche 1 bis Woche 4 wurden erfolgreich
abgeschlossen beziehungsweise vorgezogen umgesetzt.

Die beiden freMTPL2-Datensätze wurden reproduzierbar beschafft, im Raw Layer
unverändert gespeichert und durch Metadaten, Dateigrößen und
SHA256-Prüfsummen dokumentiert.

Eine wiederholbare Ingestion-Pipeline sowie neun automatisierte
Data-Quality-Prüfungen wurden entwickelt. Die wesentlichen
Datenqualitätsbefunde wurden dokumentiert und anschließend durch
nachvollziehbare Regeln in der Curated-Schicht behandelt.

Der policenbasierte Curated-Datensatz umfasst 678.013 Policen und 25 Spalten.

Die Daten wurden in ein analytisches PostgreSQL-Datenmodell überführt.
Zusätzlich stehen Views für policenbasierte Analysen, Claim-Level-Analysen,
Data-Quality-Monitoring und den aktuellen Frequency-Prediction-Checkpoint zur
Verfügung.

Die geschäftsorientierte explorative Datenanalyse in
`notebooks/03_eda.ipynb` wurde vollständig abgeschlossen und mit einem
frischen Kernel über `Run All` validiert.

Darüber hinaus wurde der kritische End-to-End-Kontrollpunkt erfolgreich
umgesetzt:

`PostgreSQL → Python → einfaches Poisson-Modell → Vorhersagen in PostgreSQL → Power BI`

Das hierfür verwendete Poisson-Modell ist ausdrücklich nur ein technischer
Checkpoint und noch nicht das finale Frequency-Modell.

Die Hauptmodellierungsphase mit Train-/Test-Split, finalem Poisson-Modell,
Gamma-Severity-Modell, Pure Premium, Deviance-Metriken und
Risk-Decile-Kalibrierung wurde noch nicht begonnen.

## 2. Bereits abgeschlossen

### Projektgrundlage

- [X] Privates GitHub-Repository und Projektstruktur eingerichtet
- [X] Virtuelle Python-Umgebung erstellt
- [X] `requirements.txt` erstellt und aktualisiert
- [X] `docs/business_understanding.md` erstellt
- [X] `docs/data_dictionary.md` erstellt
- [X] PostgreSQL 17 lokal installiert
- [X] Projektdatenbank `kfz_insurance` eingerichtet
- [X] PostgreSQL-Rolle `kfz_app` eingerichtet
- [X] PostgreSQL-Verbindung mit `psql`, DBeaver und Power BI getestet

### Datenbeschaffung und Ingestion

- [X] OpenML-Datenquelle geprüft
- [X] Frequency-Datensatz `freMTPL2freq` beschafft
- [X] Severity-Datensatz `freMTPL2sev` beschafft
- [X] Raw-Daten unverändert gespeichert
- [X] Source Manifest mit Dateigrößen und SHA256-Prüfsummen erstellt
- [X] OpenML-Datensatzversionen dokumentiert
- [X] Ingestion-Pipeline in `src/ingestion/fetch_openml.py` entwickelt
- [X] Schema- und Datentypprüfungen implementiert
- [X] Logging und Fehlerbehandlung umgesetzt
- [X] Pipeline-Läufe in `pipeline_runs.jsonl` dokumentiert
- [X] Wiederholte Pipeline-Ausführung erfolgreich validiert

### Data Quality

- [X] Neun automatisierte Data-Quality-Prüfungen implementiert
- [X] Missing Values geprüft
- [X] Exposure-Grenzen geprüft
- [X] ClaimNb-Grenzen geprüft
- [X] ClaimAmount geprüft
- [X] Frequency-Severity-Konsistenz geprüft
- [X] Orphan-Severity-Datensätze identifiziert
- [X] Potenzielle Duplikate geprüft
- [X] Join-Kardinalität geprüft
- [X] DQ-Ergebnisse mit `PASS`, `WARN` und `FAIL` standardisiert
- [X] DQ-Historie dauerhaft gespeichert
- [X] `docs/data_quality_report.md` erstellt und aktualisiert
- [X] Manuelle Validierung in `notebooks/02_data_quality.ipynb` durchgeführt
- [X] Automatisierte und manuelle DQ-Ergebnisse miteinander abgeglichen

### Curated Layer und Feature Engineering

- [X] Severity-Daten vor dem Join auf `IDpol` aggregiert
- [X] `total_claim_amount` berechnet
- [X] `claim_record_count` berechnet
- [X] 195 Orphan-Severity-Zeilen aus der analytischen Schicht ausgeschlossen
- [X] `Exposure > 1` auf 1,0 begrenzt
- [X] `exposure_capped` erstellt
- [X] `high_claim_count` erstellt
- [X] `missing_severity` erstellt
- [X] `claim_count_mismatch` erstellt
- [X] Unbekannte Schadenhöhen nicht mit null imputiert
- [X] `observed_claim_frequency` berechnet
- [X] `observed_severity` berechnet
- [X] `observed_pure_premium` berechnet
- [X] Fahrer-Altersgruppen erstellt
- [X] Fahrzeugalter-Gruppen erstellt
- [X] Bonus-Malus-Segmente erstellt
- [X] `log_density` erstellt
- [X] `data/processed/policy_curated.pq` mit 678.013 Policen und 25 Spalten erstellt
- [X] Curated Layer technisch validiert

### PostgreSQL Analytics Layer

- [X] `stg_policy` erstellt und befüllt
- [X] `stg_claim` erstellt und befüllt
- [X] `fact_policy_exposure` erstellt und befüllt
- [X] `fact_claim` erstellt und befüllt
- [X] `pipeline_runs` erstellt und befüllt
- [X] `dq_check_results` erstellt und befüllt
- [X] `vw_policy_risk_base` erstellt
- [X] `vw_claim_analysis` erstellt
- [X] `vw_dq_summary` erstellt
- [X] JSON-Strukturen als PostgreSQL `JSONB` gespeichert
- [X] Tabellen und Views über SQL-Abfragen validiert

### Explorative Datenanalyse

- [X] `notebooks/03_eda.ipynb` erstellt
- [X] Curated-Datenstruktur erneut interaktiv geprüft
- [X] Fehlende Werte und Duplikate geprüft
- [X] Feature-Gruppen und Segmentgrenzen validiert
- [X] Fahrer-Alter und Schadenfrequenz analysiert
- [X] Fahrzeugalter und Schadenfrequenz analysiert
- [X] Fahrzeugleistung analysiert
- [X] Bonus-Malus und Schadenfrequenz analysiert
- [X] Area analysiert
- [X] Region analysiert
- [X] Density analysiert
- [X] Kraftstoffart analysiert
- [X] Schadenhöhenverteilung und Tail-Effekt untersucht
- [X] Beobachteten Pure Premium nach Risikosegmenten analysiert
- [X] Tatsächliche Portfoliokennzahlen dokumentiert
- [X] Severity-Matching-Quote von 99,27 % dokumentiert
- [X] Severity-Abdeckung bei Schadenpolicen von 73,24 % dokumentiert
- [X] Spearman-Korrelationsanalyse und Heatmap erstellt
- [X] Starke Konzentration von `ClaimNb = 0` untersucht
- [X] Exposure-Verteilung analysiert
- [X] EDA mit abschließendem Fazit dokumentiert
- [X] Notebook mit Restart Kernel + Run All erfolgreich validiert

### Kritischer End-to-End-Kontrollpunkt

- [X] `src/models/checkpoint_poisson.py` erstellt
- [X] Modellierungsdaten direkt aus `vw_policy_risk_base` geladen
- [X] Numerische und kategorische Features in einer sklearn-Pipeline verarbeitet
- [X] Annualisierte Frequency als `ClaimNb / Exposure` verwendet
- [X] `Exposure` als Sample Weight verwendet
- [X] Ein einfaches `PoissonRegressor`-Modell erfolgreich trainiert
- [X] Policy-Level-Frequency-Vorhersagen erzeugt
- [X] `predicted_claim_count = predicted_frequency × Exposure` berechnet
- [X] Beobachtete Portfoliofrequenz von ca. 0,100742 validiert
- [X] Prognostizierte Portfoliofrequenz von ca. 0,100733 validiert
- [X] `policy_frequency_predictions` als Checkpoint-Tabelle erstellt
- [X] Primärschlüssel `(idpol, model_name)` eingerichtet
- [X] 678.013 Prediction-Zeilen mit PostgreSQL `COPY` gespeichert
- [X] `vw_frequency_prediction_analysis` erstellt
- [X] SQL-seitige Prediction-Zahlen kontrolliert
- [X] `powerbi/week4_checkpoint.pbix` erstellt
- [X] PostgreSQL-Prediction-View in Power BI importiert
- [X] Separate `KPI_Measures`-Tabelle erstellt
- [X] `Total Exposure` als DAX Measure erstellt
- [X] `Actual Claims` als DAX Measure erstellt
- [X] `Predicted Claims` als DAX Measure erstellt
- [X] `Actual Frequency` als DAX Measure erstellt
- [X] `Predicted Frequency` als DAX Measure erstellt
- [X] Actual vs. Predicted Frequency nach Area visualisiert
- [X] Kritischen End-to-End-Kontrollpunkt erfolgreich abgeschlossen

## 3. Aktueller technischer Kontrollpunkt

Der aktuelle Checkpoint bestätigt, dass die gesamte technische Architektur
grundsätzlich funktioniert:

```text
OpenML / Raw Data
        ↓
Python Ingestion
        ↓
Data Quality
        ↓
Curated Layer
        ↓
PostgreSQL
        ↓
Python Modeling
        ↓
Poisson Checkpoint
        ↓
Policy-Level Predictions
        ↓
PostgreSQL
        ↓
Power BI
```
