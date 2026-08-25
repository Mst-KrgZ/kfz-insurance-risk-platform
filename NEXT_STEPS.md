# NEXT STEPS

**Stand:** 25.08.2026

## 1. Aktueller Projektstatus

Die technischen Arbeitspakete Woche 1 bis Woche 5 wurden erfolgreich
abgeschlossen beziehungsweise vorgezogen umgesetzt.

Die Datenbeschaffung, Ingestion, Data-Quality-Prüfungen, Curated-Schicht,
PostgreSQL-Analytics-Layer, explorative Datenanalyse sowie die
Hauptmodellierung sind vollständig umgesetzt.

Der policenbasierte Curated-Datensatz umfasst 678.013 Policen und 25 Spalten.

Die Curated-Schicht wurde im Rahmen eines zusätzlichen technischen Reviews
erneut aus dem versionierten Source Code aufgebaut. Der rekonstruierte
Datensatz ist wertidentisch mit dem bestehenden `policy_curated.pq`.
Damit ist die Curated-Pipeline reproduzierbar ausführbar.

Für Frequency und Severity wird ein gemeinsamer, einmalig definierter
Policy-Level-Train/Test-Split verwendet.

Nach der ursprünglichen Modellierung wurde ein Post-Audit-Quality-Pass
durchgeführt. Dabei wurden die wichtigsten Modellannahmen und
Validierungsverfahren erneut geprüft und gezielt verbessert.

Als finale Hauptmodelle wurden festgelegt:

- Frequency:
  `frequency_poisson_quantile_spline_full_v2`
- Severity:
  `severity_gamma_spline_scaled_full_v2`

Frequency v2 verbessert die Holdout Mean Poisson Deviance auf 0,592685,
erreicht ein Poisson-D² von 0,0528 und eine Portfolioabweichung von nur
−0,25 %. Der Frequency-Gini steigt gegenüber v1 von 0,2683 auf 0,2903.

Severity v2 verbessert die erste Severity-Version, bleibt auf dem Holdout
jedoch leicht schlechter als die konstante Gamma-Baseline. Die finale
Holdout Mean Gamma Deviance beträgt 1,567498 gegenüber 1,543630 für die
Baseline. Die Portfolioabweichung verbessert sich von +7,19 % auf +3,99 %.

Die Severity-Komponente besitzt nur eine sehr geringe Ranking-Fähigkeit
(Gini 0,0033). Sie wird deshalb primär zur monetären Quantifizierung der
erwarteten Schadenhöhe eingesetzt. Frequency v2 bleibt der wichtigste
Risikodifferenzierer.

Die Pure-Premium-Auswertung wurde methodisch korrigiert. Die zuvor
beobachtete Abweichung von +37,79 % auf dem Teilbestand mit vollständig
beobachtbarer Schadenhöhe wird nicht als unbiased Modellkalibrierung
interpretiert, da dieser Vergleich durch fehlende Severity-Informationen
selektionsverzerrt ist.

Die finale Pure Premium wird weiterhin berechnet als:

`Predicted Pure Premium = Predicted Frequency × Predicted Severity`

Lorenz- und Gini-Auswertungen wurden bereits durchgeführt.

Ergebnisse:

- Frequency v1 Gini: 0,2683
- Frequency v2 Gini: 0,2903
- Severity v1 Gini: 0,0333
- Severity v2 Gini: 0,0033
- Frequency-only Loss Gini: 0,2372
- Pure-Premium-v2 Loss Gini: 0,2358

Die Severity-Komponente verbessert die Loss-Rangfolge gegenüber Frequency
allein nicht. Dieses Ergebnis wird als fachliche Modellgrenze dokumentiert.

Nach Abschluss der Modellauswahl wurden Frequency v2 und Severity v2 auf
dem vollständig verfügbaren Datenbestand neu trainiert.

Finale Full-Data-Artefakte:

- `models/frequency_poisson_quantile_spline_full_v2.joblib`
- `models/severity_gamma_spline_scaled_full_v2.joblib`

Finale Holdout-Artefakte:

- `models/frequency_poisson_quantile_spline_holdout_v2.joblib`
- `models/severity_gamma_spline_scaled_holdout_v2.joblib`

Die Full-Data-Artefakte wurden erneut geladen und auf dem gesamten Portfolio
ausgeführt.

Ergebnis:

- Frequency-Prognosen exakt reproduziert
- Severity-Prognosen exakt reproduziert
- maximale absolute Abweichung jeweils 0,000000000000

Für alle 678.013 Policen wurde anschließend ein neuer finaler
Prediction Run erzeugt.

Prediction Run ID:

`3e79d43b-d9e2-4edf-9056-be0827aa22f0`

Die finale Datei

`data/output/model_predictions.pq`

enthält:

- 678.013 Zeilen
- 678.013 eindeutige `IDpol`
- 0 Duplikate
- 0 Missing Values
- 1 Prediction Run

Die Prediction-Datei wurde erfolgreich in PostgreSQL geladen.

PostgreSQL-Validierung:

- `model_predictions`: 678.013 Zeilen
- eindeutige `IDpol`: 678.013
- Frequency-Modell:
  `frequency_poisson_quantile_spline_full_v2`
- Severity-Modell:
  `severity_gamma_spline_scaled_full_v2`

Damit ist der vollständige Pfad

`Curated Data → Modellierung → Full-Data-Refit → Artifact → Parquet → PostgreSQL`

für die finalen v2-Hauptmodelle reproduzierbar validiert.

## 2. Bereits abgeschlossen

### Projektgrundlage

- [X] Privates GitHub-Repository und Projektstruktur eingerichtet
- [X] Virtuelle Python-Umgebung erstellt
- [X] `requirements.txt` erstellt und aktualisiert
- [X] `docs/business_understanding.md` erstellt
- [X] `docs/data_dictionary.md` erstellt
- [X] PostgreSQL lokal eingerichtet
- [X] Projektdatenbank `kfz_insurance` eingerichtet
- [X] PostgreSQL-Rolle `kfz_app` eingerichtet
- [X] PostgreSQL-Verbindung mit Terminal, DBeaver und Power BI getestet

### Datenbeschaffung und Ingestion

- [X] OpenML-Datenquelle geprüft
- [X] Frequency-Datensatz `freMTPL2freq` beschafft
- [X] Severity-Datensatz `freMTPL2sev` beschafft
- [X] Raw-Daten unverändert gespeichert
- [X] Source Manifest mit Dateigrößen und SHA256-Prüfsummen erstellt
- [X] OpenML-Datensatzversionen dokumentiert
- [X] Ingestion-Pipeline entwickelt
- [X] Schema- und Datentypprüfungen implementiert
- [X] Logging und Fehlerbehandlung umgesetzt
- [X] Pipeline-Läufe dokumentiert
- [X] Wiederholte Pipeline-Ausführung validiert

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
- [X] DQ-Ergebnisse standardisiert
- [X] DQ-Historie gespeichert
- [X] `docs/data_quality_report.md` erstellt und aktualisiert
- [X] Manuelle Notebook-Validierung durchgeführt
- [X] Automatisierte und manuelle DQ-Ergebnisse abgeglichen

### Curated Layer und Feature Engineering

- [X] Severity vor dem Join auf `IDpol` aggregiert
- [X] `total_claim_amount` berechnet
- [X] `claim_record_count` berechnet
- [X] Orphan-Severity-Datensätze ausgeschlossen
- [X] Exposure-Capping umgesetzt
- [X] `exposure_capped` erstellt
- [X] `high_claim_count` erstellt
- [X] `missing_severity` erstellt
- [X] `claim_count_mismatch` erstellt
- [X] unbekannte Schadenhöhen nicht mit null imputiert
- [X] beobachtete Frequency berechnet
- [X] beobachtete Severity berechnet
- [X] beobachtete Pure Premium berechnet
- [X] Fahrer-Altersgruppen erstellt
- [X] Fahrzeugalter-Gruppen erstellt
- [X] Bonus-Malus-Segmente erstellt
- [X] `log_density` erstellt
- [X] `policy_curated.pq` mit 678.013 Policen und 25 Spalten erstellt
- [X] Curated Layer fachlich validiert
- [X] Curated-Pipeline über `src/preprocessing/build_curated.py` reproduzierbar gemacht
- [X] Curated-Datensatz vollständig rekonstruiert
- [X] Rekonstruierten und bestehenden Curated-Datensatz wertidentisch validiert

### PostgreSQL Analytics Layer

- [X] `stg_policy` erstellt und befüllt
- [X] `stg_claim` erstellt und befüllt
- [X] `fact_policy_exposure` erstellt und befüllt
- [X] `fact_claim` erstellt und befüllt
- [X] `pipeline_runs` erstellt und befüllt
- [X] `dq_check_results` erstellt und befüllt
- [X] analytische Views erstellt
- [X] JSON-Strukturen als PostgreSQL `JSONB` gespeichert
- [X] Tabellen und Views über SQL-Abfragen validiert

### Explorative Datenanalyse

- [X] `notebooks/03_eda.ipynb` erstellt
- [X] Datenstruktur, Missing Values und Duplikate geprüft
- [X] Frequency nach relevanten Risikomerkmalen analysiert
- [X] Severity-Verteilung und Heavy-Tail-Effekt untersucht
- [X] Pure Premium nach Risikosegmenten analysiert
- [X] Portfolio-Kennzahlen dokumentiert
- [X] Severity-Abdeckung dokumentiert
- [X] Korrelationsanalyse durchgeführt
- [X] Exposure-Verteilung analysiert
- [X] EDA vollständig dokumentiert
- [X] Notebook mit Restart Kernel + Run All validiert

### End-to-End-Kontrollpunkt

- [X] PostgreSQL → Python → Modell → PostgreSQL → Power BI getestet
- [X] einfachen Poisson-Checkpoint entwickelt
- [X] 678.013 Policy-Level-Predictions erzeugt
- [X] Prediction-Tabelle und View erstellt
- [X] Power-BI-Checkpoint umgesetzt
- [X] End-to-End-Datenfluss erfolgreich validiert

### Gemeinsamer Modell-Split

- [X] einmaligen Policy-Level-Train/Test-Split erstellt
- [X] Split-Artefakt gespeichert
- [X] 542.410 Train-Policen
- [X] 135.603 Test-Policen
- [X] Überschneidung der `IDpol`: 0
- [X] Frequency und Severity verwenden denselben Split
- [X] Split wird für weitere Challenger-Modelle nicht neu erzeugt

### Frequency v1

- [X] Exposure-gewichtetes Poisson-Modell entwickelt
- [X] Baseline berechnet
- [X] Cross-Validation durchgeführt
- [X] uniforme Spline-Spezifikation entwickelt
- [X] Holdout Mean Poisson Deviance 0,601319
- [X] Poisson-D² 0,0390
- [X] Portfolioabweichung −0,33 %
- [X] Gini 0,2683
- [X] Holdout- und Full-Data-Artefakte gespeichert

### Frequency v2 / Post-Audit

- [X] Uniform- und Quantile-Knoten über wiederholte CV verglichen
- [X] Quantile-Knoten über alle fünf Seeds stabil besser
- [X] Knotenzahl und Grad ausschließlich auf Trainingsdaten optimiert
- [X] `n_knots = 8`
- [X] `degree = 2`
- [X] `knots = "quantile"`
- [X] `alpha = 0.0`
- [X] `log_density` linear belassen
- [X] Holdout Mean Poisson Deviance 0,592685
- [X] Poisson-D² 0,0528
- [X] Portfolioabweichung −0,25 %
- [X] Frequency-Gini 0,2903
- [X] Frequency v2 als finales Frequency-Modell festgelegt
- [X] Holdout-v2-Artefakt gespeichert
- [X] Full-Data-v2-Artefakt gespeichert

### Severity v1

- [X] konsistente Severity-Eligibility-Regeln umgesetzt
- [X] ClaimNb-gewichtetes Gamma-Modell entwickelt
- [X] Baseline berechnet
- [X] Cross-Validation durchgeführt
- [X] ursprüngliche Spline-Spezifikation entwickelt
- [X] Holdout Mean Gamma Deviance 1,615760
- [X] Gamma-D² −0,0540
- [X] Portfolioabweichung +7,19 %
- [X] eingeschränkte Holdout-Generalisation dokumentiert
- [X] Holdout- und Full-Data-Artefakte gespeichert

### Severity v2 / Post-Audit

- [X] wiederholte stratifizierte 5-Fold-CV mit fünf Seeds durchgeführt
- [X] gepoolte Out-of-Fold-Metriken berechnet
- [X] CV-Signal gegenüber Baseline über alle fünf Seeds bestätigt
- [X] vollständige Matrix-Skalierung diagnostisch getestet und verworfen
- [X] selektive Skalierung numerischer Modellblöcke umgesetzt
- [X] Regularisierung untersucht
- [X] 1-SE-Regel angewendet
- [X] `alpha = 1.0` als finale v2-Spezifikation festgelegt
- [X] Large-Loss-Capping und Loading untersucht
- [X] Large-Loss-Varianten verworfen
- [X] Holdout Mean Gamma Deviance 1,567498
- [X] Gamma-D² −0,0155
- [X] Portfolioabweichung +3,99 %
- [X] Severity-Gini 0,0033
- [X] Severity-v2-Limitierung gegenüber Baseline dokumentiert
- [X] Severity v2 als finale monetäre Severity-Komponente festgelegt
- [X] Holdout-v2-Artefakt gespeichert
- [X] Full-Data-v2-Artefakt gespeichert

### Pure Premium und Modellvergleich

- [X] `notebooks/06_model_comparison.ipynb` erstellt
- [X] Frequency und Severity kombiniert
- [X] Predicted Pure Premium berechnet
- [X] Expected Claim Count exposure-korrekt berechnet
- [X] Expected Claim Amount exposure-korrekt berechnet
- [X] ursprüngliche +37,79-%-Auswertung als selection-biased identifiziert
- [X] Frequency- und Severity-Kalibrierung getrennt berichtet
- [X] Pure-Premium-Diagnostik methodisch korrigiert
- [X] Frequency-Lorenzkurve erstellt
- [X] Severity-Lorenzkurve erstellt
- [X] Pure-Premium-Lorenzkurve erstellt
- [X] Frequency-Gini berechnet
- [X] Severity-Gini berechnet
- [X] Pure-Premium-Loss-Gini berechnet
- [X] Frequency-only Loss Gini 0,2372
- [X] Pure-Premium-v2 Loss Gini 0,2358
- [X] finale Modellentscheidung dokumentiert

### Finaler Full-Data-Refit und Artefakte

- [X] Frequency v2 auf allen 678.013 Policen neu trainiert
- [X] Severity v2 auf allen 24.943 geeigneten Policen neu trainiert
- [X] Frequency Full Refit erfolgreich abgeschlossen
- [X] Severity Full Refit erfolgreich abgeschlossen
- [X] finale v2-Modellartefakte gespeichert
- [X] v1-Artefakte separat erhalten
- [X] Full-Data-v2-Artefakte erneut geladen
- [X] Frequency-Prognosen exakt reproduziert
- [X] Severity-Prognosen exakt reproduziert
- [X] maximale absolute Differenz jeweils 0

### Finale Prediction-Schicht

- [X] neuen Prediction Run erzeugt
- [X] Frequency-v2-Modellversion dokumentiert
- [X] Severity-v2-Modellversion dokumentiert
- [X] 678.013 Policy-Level-Predictions erzeugt
- [X] `model_predictions.pq` gespeichert
- [X] 0 doppelte `IDpol`
- [X] 0 Missing Values
- [X] `model_predictions` in PostgreSQL geladen
- [X] 678.013 Prediction-Zeilen in PostgreSQL validiert
- [X] eindeutige `IDpol` in PostgreSQL validiert
- [X] Prediction Run ID in DBeaver geprüft
- [X] finale v2-Modellversionen in PostgreSQL geprüft

### Dokumentation

- [X] `docs/statusbericht_woche_5.md` nach Post-Audit-Review vollständig aktualisiert
- [X] Frequency-v2-Ergebnisse dokumentiert
- [X] Severity-v2-Ergebnisse dokumentiert
- [X] Severity-Limitierung transparent dokumentiert
- [X] Pure-Premium-Selektionseffekt dokumentiert
- [X] Lorenz-/Gini-Ergebnisse dokumentiert
- [X] finale Modellentscheidung dokumentiert
- [X] PostgreSQL-v2-Integration dokumentiert

## 3. Aktueller technischer Kontrollpunkt

Der aktuelle technische Stand:

```text
OpenML / Raw Data
        ↓
Python Ingestion
        ↓
Data Quality
        ↓
Reproduzierbarer Curated Layer
        ↓
PostgreSQL Analytics Layer
        ↓
Kanonischer Policy-Level Train/Test Split
        ↓
Frequency v2 + Severity v2
        ↓
Holdout Evaluation
        ↓
Lorenz / Gini / Calibration
        ↓
Predicted Pure Premium
        ↓
Finaler Full-Data-Refit
        ↓
Versionierte v2-Modellartefakte
        ↓
Artifact Reload Validation
        ↓
Policy-Level Scoring
        ↓
model_predictions.pq
        ↓
PostgreSQL model_predictions
        ↓
vw_model_prediction_analysis
        ↓
Power BI / Challenger / Decision Support
```
