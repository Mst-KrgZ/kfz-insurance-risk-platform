# NEXT STEPS

**Stand:** 24.08.2026

## 1. Aktueller Projektstatus

Die technischen Arbeitspakete Woche 1 bis Woche 5 wurden erfolgreich
abgeschlossen beziehungsweise vorgezogen umgesetzt.

Die Datenbeschaffung, Ingestion, Data-Quality-Prüfungen, Curated-Schicht,
PostgreSQL-Analytics-Layer und die geschäftsorientierte explorative
Datenanalyse sind vollständig umgesetzt.

Der policenbasierte Curated-Datensatz umfasst 678.013 Policen und 25 Spalten.

Nach dem erfolgreichen End-to-End-Kontrollpunkt wurde die Hauptmodellierung
auf Basis eines einmalig definierten und reproduzierbaren Policy-Level-
Train/Test-Splits durchgeführt.

Für die Schadenhäufigkeit wurde ein Poisson-Modell mit Spline-basiertem
Feature Engineering entwickelt und über Cross-Validation optimiert. Das
finale Holdout-Modell erreicht eine Mean Poisson Deviance von 0,601319 und
eine sehr gute Portfolio-Kalibrierung mit 7.211,98 prognostizierten gegenüber
7.236 tatsächlich beobachteten Schäden.

Für die Schadenhöhe wurde ein Gamma-Modell entwickelt. Die Spline-
Spezifikation zeigte innerhalb der Cross-Validation die beste Leistung,
konnte die konstante Severity-Baseline auf dem Holdout-Datensatz jedoch nicht
übertreffen. Diese eingeschränkte Generalisierungsfähigkeit wurde als
Modelllimitierung dokumentiert.

Frequency und Severity wurden anschließend zur prognostizierten Pure Premium
zusammengeführt. Die Risk-Decile-Analyse zeigt eine erkennbare
Risikodifferenzierung, gleichzeitig jedoch eine Überprognose in den höchsten
Risikogruppen. Die Interpretation der Schadenbetragskalibrierung berücksichtigt
explizit die fehlenden Severity-Informationen bei einem Teil der Schadenpolicen.

Nach Abschluss der Holdout-Bewertung wurden die festgelegten Frequency- und
Severity-Spezifikationen auf den vollständig verfügbaren Daten neu geschätzt.
Damit wurden für alle 678.013 Policen finale Policy-Level-Prognosen erzeugt.

Die finalen Prognosen wurden reproduzierbar gespeichert und anschließend in
die PostgreSQL-Tabelle `model_predictions` geladen. Die View
`vw_model_prediction_analysis` stellt den aktuellsten Scoring-Lauf für
nachgelagerte Analysen und Power BI bereit.

Der aktuelle technische Stand ist auf GitHub versioniert und der Working Tree
ist clean.

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

### Hauptmodelle und Pure Premium

- [X] Gemeinsamen Policy-Level-Train/Test-Split erstellt
- [X] Split-Artefakt reproduzierbar gespeichert und validiert
- [X] Train-/Test-Leakage ausgeschlossen
- [X] `notebooks/04_frequency_model.ipynb` erstellt
- [X] Exposure-korrekte Poisson-Frequency-Modellierung umgesetzt
- [X] 5-Fold-Cross-Validation durchgeführt
- [X] Grouped-, Raw- und Spline-Spezifikationen verglichen
- [X] Spline-Hyperparameter innerhalb der Trainingsdaten optimiert
- [X] Finales Frequency-Modell mit 6 Knoten, Grad 3 und `alpha=0` festgelegt
- [X] Holdout Mean Poisson Deviance von 0,601319 erreicht
- [X] Poisson-D² von 0,0390 dokumentiert
- [X] Frequency-Kalibrierung nach Risikodezilen durchgeführt
- [X] Holdout-Portfoliofrequenz exposure-korrekt validiert
- [X] Frequency-Holdout-Modell als reproduzierbares Artefakt gespeichert
- [X] `notebooks/05_severity_model.ipynb` erstellt
- [X] Konsistente Severity-Eligibility-Regeln umgesetzt
- [X] ClaimNb-gewichtete Gamma-Modellierung umgesetzt
- [X] Grouped-, Raw- und Spline-Severity-Spezifikationen verglichen
- [X] Severity-Spline-Hyperparameter per Cross-Validation optimiert
- [X] Finales Severity-Modell mit 6 Knoten, Grad 3 und `alpha=0` festgelegt
- [X] Holdout Mean Gamma Deviance von 1,615760 dokumentiert
- [X] Eingeschränkte Severity-Generalisation gegenüber der Baseline dokumentiert
- [X] Severity-Kalibrierung und Heavy-Tail-Effekte analysiert
- [X] Severity-Holdout-Modell als reproduzierbares Artefakt gespeichert
- [X] `notebooks/05_severity_model.ipynb` mit Restart Kernel + Run All validiert
- [X] `notebooks/06_model_comparison.ipynb` erstellt
- [X] Predicted Pure Premium als Frequency × Severity berechnet
- [X] Expected Claim Count exposure-korrekt berechnet
- [X] Expected Claim Amount exposure-korrekt berechnet
- [X] Pure-Premium-Risikodezile analysiert
- [X] Datenlimitation durch fehlende Severity-Informationen dokumentiert
- [X] Frequency- und Severity-Modelle auf Full Data neu geschätzt
- [X] Full-Data-Modellartefakte gespeichert und reproduzierbar validiert
- [X] Finales Scoring für alle 678.013 Policen durchgeführt
- [X] `data/output/model_predictions.pq` erzeugt
- [X] PostgreSQL-Tabelle `model_predictions` erstellt
- [X] 678.013 finale Prediction-Zeilen mit PostgreSQL `COPY` gespeichert
- [X] Prediction-Run- und Modellversionierung implementiert
- [X] `vw_model_prediction_analysis` erstellt
- [X] Python- und PostgreSQL-Aggregate vollständig abgeglichen

## 3. Aktueller technischer Kontrollpunkt

Der aktuelle technische Stand bestätigt die vollständige Modellierungs- und
Prediction-Pipeline:

```text
OpenML / Raw Data
        ↓
Python Ingestion
        ↓
Data Quality
        ↓
Curated Layer
        ↓
PostgreSQL Analytics Layer
        ↓
Gemeinsamer Train/Test-Split
        ↓
Poisson Frequency + Gamma Severity
        ↓
Holdout Evaluation
        ↓
Predicted Pure Premium
        ↓
Full-Data-Refit
        ↓
Policy-Level Scoring
        ↓
PostgreSQL model_predictions
        ↓
vw_model_prediction_analysis
        ↓
Power BI / weitere Modellvergleiche
```

## 4. Nächste technische Schritte

Der nächste technische Arbeitsblock beginnt mit dem Challenger-Modell und
wird erst nach dem Abschluss der Dokumentations- und Reporting-Aufgaben der
aktuellen Modellierungsphase gestartet.

Geplante nächste Schritte:

1. TweedieRegressor als Challenger-Modell entwickeln
2. Mean Tweedie Deviance berechnen
3. Lorenz-/Gini-Analyse ergänzen
4. Poisson × Gamma und Tweedie fair vergleichen
5. Vier finale Risikosegmente definieren
6. Handlungsempfehlungen je Risikosegment ableiten
7. FastAPI-Endpunkte für Policy- und Batch-Scoring vorbereiten
