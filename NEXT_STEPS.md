# NEXT STEPS

**Stand:** 01.09.2026

## 1. Aktueller Projektstatus

Die technischen Arbeitspakete Woche 1 bis Woche 6 wurden erfolgreich
abgeschlossen beziehungsweise vorgezogen umgesetzt.

Die Datenbeschaffung, Ingestion, Data-Quality-Prüfungen, Curated-Schicht,
PostgreSQL-Analytics-Layer, explorative Datenanalyse, Hauptmodellierung,
Challenger-Modellierung, Explainability, Risikosegmentierung,
Decision-Support-Logik und FastAPI sind technisch umgesetzt.

Der policenbasierte Curated-Datensatz umfasst 678.013 Policen und 25 Spalten.

Die Curated-Schicht wurde im Rahmen eines zusätzlichen technischen Reviews
erneut aus dem versionierten Source Code aufgebaut. Der rekonstruierte
Datensatz ist wertidentisch mit dem bestehenden `policy_curated.pq`.
Damit ist die Curated-Pipeline reproduzierbar ausführbar.

Für Frequency, Severity und den Tweedie-Challenger wird derselbe einmalig
definierte Policy-Level-Train/Test-Split verwendet.

Es wurde kein neuer Split erzeugt.

Als finale Hauptmodelle wurden festgelegt:

- Frequency:
  `frequency_poisson_quantile_spline_full_v2`
- Severity:
  `severity_gamma_spline_scaled_full_v2`

Frequency v2 verbessert die Holdout Mean Poisson Deviance auf 0,592685,
erreicht ein Poisson-D² von 0,0528 und eine Portfolioabweichung von nur
−0,25 %. Der Frequency-Gini beträgt 0,2903.

Severity v2 verbessert die erste Severity-Version, bleibt auf dem Holdout
jedoch leicht schlechter als die konstante Gamma-Baseline. Die finale
Holdout Mean Gamma Deviance beträgt 1,567498 gegenüber 1,543630 für die
Baseline. Die Portfolioabweichung beträgt +3,99 %.

Die Severity-Komponente besitzt nur eine sehr geringe Ranking-Fähigkeit
(Gini 0,0033). Sie wird deshalb primär zur monetären Quantifizierung der
erwarteten Schadenhöhe eingesetzt. Frequency v2 bleibt der wichtigste
Risikodifferenzierer des Two-Stage-Modells.

Die finale Two-Stage-Pure-Premium wird berechnet als:

`Predicted Pure Premium = Predicted Frequency × Predicted Severity`

Die zuvor beobachtete Abweichung von +37,79 % auf dem Teilbestand mit
vollständig beobachtbarer Schadenhöhe wird nicht als unbiased
Modellkalibrierung verwendet, da dieser Vergleich durch fehlende
Severity-Informationen selektionsverzerrt ist.

Die primären Kalibrierungsaussagen bleiben:

- Frequency v2 auf vollständigem Holdout: −0,25 %
- Severity v2 auf Severity-geeignetem Holdout: +3,99 %

Der direkte Tweedie-Challenger wurde anschließend auf derselben kanonischen
Split-Logik entwickelt.

Tweedie-Ziel:

`y = total_claim_amount / Exposure`

mit:

`sample_weight = Exposure`

Finale Challenger-Spezifikation:

- `TweedieRegressor`
- `power = 1.9`
- `alpha = 0.0`
- Quantile-Splines
- `n_knots = 8`
- `degree = 2`
- `log_density` linear

Die Modellauswahl erfolgte ausschließlich auf Trainingsdaten.

Auf der gemeinsamen beobachtbaren Holdout-Basis ergaben sich:

- konstante Baseline Mean Tweedie Deviance: 34,602470
- Tweedie Mean Tweedie Deviance: 34,364453
- Two-Stage Mean Tweedie Deviance: 34,356826
- Tweedie Portfolioabweichung: +6,40 %
- Two-Stage Portfolioabweichung: +36,29 %
- Tweedie Gini: 0,2677
- Two-Stage Loss Gini: ca. 0,2358

Damit besitzt das Two-Stage-Modell eine minimal bessere Tweedie-Deviance,
während der direkte Tweedie-Challenger deutlich besser kalibriert ist und
eine stärkere Ranking-Fähigkeit zeigt.

Es wurde deshalb keine Winner-takes-all-Entscheidung getroffen.

Weiterverwendung:

- Two-Stage:
  Frequency-/Severity-Dekomposition und monetäre Modellinterpretation
- Tweedie:
  direkter Pure-Premium-Risikoscore, Portfolio-Ranking und
  Risikosegmentierung

Die finalen Modelle wurden zusätzlich über GLM-Koeffizienten,
Permutation Feature Importance sowie PDP-/ICE-Analysen interpretiert.

Auf Basis der Tweedie-Pure-Premium wurden vier Risikosegmente aus der
Portfolioverteilung abgeleitet:

- `LOW`
- `STANDARD`
- `ELEVATED`
- `HIGH`

Grenzen:

- P50: 119,35
- P75: 187,90
- P90: 328,24

Segmentgrößen:

- LOW: 339.008 Policen
- STANDARD: 169.508 Policen
- ELEVATED: 101.695 Policen
- HIGH: 67.802 Policen

Zusätzlich wurden Risk Deciles 1–10 erzeugt.

Das HIGH-Segment umfasst ungefähr 10 % der Policen und konzentriert rund
32,1 % des modellierten erwarteten Schadenaufwands.

Für die Segmente wurde eine Decision-Support-Logik definiert:

- `Standard process`
- `Additional review recommended`
- `Manual underwriting review recommended`

Die FastAPI-Schicht wurde auf die finale Modell- und Segmentierungslogik
ausgerichtet.

Implementierte Endpunkte:

- `GET /health`
- `POST /risk-score`
- `POST /pure-premium`
- `GET /data-quality-summary`

Zusätzlich umgesetzt:

- Pydantic-Validierung
- Ablehnung unbekannter Request-Felder
- Wertebereichsvalidierung
- HTTP-Statuscodes
- Logging
- strukturierte Response-Schemas
- Swagger/OpenAPI

Der vollständige Testlauf wurde erfolgreich abgeschlossen:

`6 passed`

Swagger wurde zusätzlich manuell geprüft. Alle vier geplanten Endpunkte
sind unter `/docs` sichtbar und ausführbar.

Die finalen Änderungen wurden versioniert und nach GitHub übertragen.

Finaler Git-Status des Arbeitspakets:

`nothing to commit, working tree clean`

Damit sind die technischen Arbeitspakete Woche 1 bis Woche 6 abgeschlossen.

Der nächste technische Schwerpunkt ist:

**Power BI & Dokumentation**

---

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
- [X] Tweedie verwendet denselben kanonischen Split
- [X] Split wird nicht neu erzeugt

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

### Pure Premium und Two-Stage-Modellvergleich

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
- [X] finale Two-Stage-Modellentscheidung dokumentiert

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

### Tweedie Challenger

- [X] `notebooks/07_tweedie_model.ipynb` entwickelt
- [X] Tweedie-Ziel als `total_claim_amount / Exposure` definiert
- [X] Exposure als `sample_weight` verwendet
- [X] kanonischen Policy-Level-Split weiterverwendet
- [X] keinen neuen Split erzeugt
- [X] Tweedie-Modellwahl ausschließlich auf Trainingsdaten durchgeführt
- [X] konstante Tweedie-Baseline berechnet
- [X] `power = 1.9` und `alpha = 0.0` als finale Spezifikation festgelegt
- [X] finale Spezifikation vor Holdout-Bewertung festgelegt
- [X] Mean Tweedie Deviance berechnet
- [X] Portfolio-Kalibrierung berechnet
- [X] Exposure-korrekten erwarteten Schaden berechnet
- [X] Two-Stage und Tweedie auf identischer beobachtbarer Holdout-Basis verglichen
- [X] Lorenz-/Gini-Auswertung durchgeführt
- [X] Tweedie Gini 0,2677 berechnet
- [X] Tweedie Portfolioabweichung +6,40 % dokumentiert
- [X] Two-Stage Portfolioabweichung +36,29 % auf derselben Basis dokumentiert
- [X] Holdout-Artefakt gespeichert
- [X] Full-Data-Artefakt gespeichert
- [X] `tweedie_predictions.pq` erzeugt und validiert

### Explainability

- [X] `notebooks/08_model_explainability.ipynb` finalisiert
- [X] GLM-Koeffizienten für Frequency v2 extrahiert
- [X] GLM-Koeffizienten für Severity v2 extrahiert
- [X] GLM-Koeffizienten für Tweedie extrahiert
- [X] Grenzen der Interpretation von Spline-Koeffizienten dokumentiert
- [X] Permutation Feature Importance für Frequency berechnet
- [X] Permutation Feature Importance für Severity berechnet
- [X] Permutation Feature Importance für Tweedie berechnet
- [X] PDP-Analysen durchgeführt
- [X] ICE-Analysen durchgeführt
- [X] Explainability als nicht-kausale Modellinterpretation dokumentiert

### Risk Segmentation

- [X] `notebooks/09_risk_segmentation.ipynb` finalisiert
- [X] Tweedie als kanonischen Risk Score für die Segmentierung verwendet
- [X] Segmentgrenzen aus der Portfolioverteilung abgeleitet
- [X] `LOW` definiert
- [X] `STANDARD` definiert
- [X] `ELEVATED` definiert
- [X] `HIGH` definiert
- [X] P50 = 119,35 dokumentiert
- [X] P75 = 187,90 dokumentiert
- [X] P90 = 328,24 dokumentiert
- [X] zehn Risk Deciles erzeugt
- [X] Decile-Grenzen dokumentiert
- [X] `risk_segments.pq` erzeugt
- [X] 678.013 Policy-Zeilen validiert
- [X] 0 doppelte `IDpol`
- [X] 0 fehlende Segmente
- [X] 0 fehlende Deciles

### Business Recommendations

- [X] `notebooks/10_business_recommendations.ipynb` finalisiert
- [X] fachliche Action Matrix erstellt
- [X] `Standard process` integriert
- [X] `Additional review recommended` integriert
- [X] `Manual underwriting review recommended` integriert
- [X] Prioritäten für alle vier Segmente definiert
- [X] Decision Rules definiert
- [X] HIGH-Segment als manuelle Review-Empfehlung und nicht als Auto-Reject dokumentiert
- [X] Loss-Konzentration nach Segment analysiert
- [X] HIGH-Segment: ca. 10 % der Policen / ca. 32,1 % des erwarteten Schadens
- [X] `management_kpi.pq` erzeugt
- [X] `policy_action_priorities.pq` erzeugt

### FastAPI

- [X] `api/schemas.py` an finale Modelllogik angepasst
- [X] `api/predictor.py` an finale Segment- und Decile-Logik angepasst
- [X] `api/main.py` auf finale Endpunkte ausgerichtet
- [X] `GET /health` implementiert
- [X] `POST /risk-score` implementiert
- [X] `POST /pure-premium` implementiert
- [X] `GET /data-quality-summary` implementiert
- [X] Pydantic-Validierung umgesetzt
- [X] unbekannte Request-Felder verboten
- [X] Exposure-Bereich validiert
- [X] Risk Decile 1–10 in API integriert
- [X] Business-Actions in API integriert
- [X] HTTP-Statuscodes umgesetzt
- [X] Logging integriert
- [X] Swagger/OpenAPI validiert
- [X] `/docs` manuell geprüft

### Tests

- [X] Health-Endpunkt getestet
- [X] Risk-Score-Endpunkt getestet
- [X] Pure-Premium-Endpunkt getestet
- [X] Data-Quality-Summary-Endpunkt getestet
- [X] Exposure = 0 wird mit 422 abgelehnt
- [X] unbekanntes Eingabefeld wird mit 422 abgelehnt
- [X] vollständigen Testlauf mit `python -m pytest -q` durchgeführt
- [X] Ergebnis: `6 passed`
- [X] externe Dependency-Warnungen als nicht testblockierend bewertet

### Dokumentation

- [X] `docs/statusbericht_woche_5.md` nach Post-Audit-Review vollständig aktualisiert
- [X] Frequency-v2-Ergebnisse dokumentiert
- [X] Severity-v2-Ergebnisse dokumentiert
- [X] Severity-Limitierung transparent dokumentiert
- [X] Pure-Premium-Selektionseffekt dokumentiert
- [X] Lorenz-/Gini-Ergebnisse dokumentiert
- [X] finale Two-Stage-Modellentscheidung dokumentiert
- [X] PostgreSQL-v2-Integration dokumentiert
- [X] Statusbericht Woche 6 inhaltlich vorbereitet
- [X] Tweedie-Ergebnisse dokumentiert
- [X] Explainability-Ergebnisse dokumentiert
- [X] Risk-Segmentation-Logik dokumentiert
- [X] Business-Action-Logik dokumentiert
- [X] API-Endpunkte und Tests dokumentiert

### Git / technischer Abschluss Woche 6

- [X] API-Änderungen versioniert
- [X] Änderungen nach GitHub übertragen
- [X] vollständigen Regression-Test vor Abschluss durchgeführt
- [X] Git Working Tree geprüft
- [X] finaler Status:
  `nothing to commit, working tree clean`

---

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
Two-Stage Pure Premium
        ↓
Holdout Evaluation
        ↓
Lorenz / Gini / Calibration
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
Tweedie Challenger
        ↓
Two-Stage vs. Tweedie
        ↓
Explainability
        ↓
Risk Segmentation + Deciles
        ↓
Business Recommendations
        ↓
Decision-Support-Artefakte
        ↓
FastAPI
        ↓
Pydantic / Logging / Swagger
        ↓
6 API-Tests
        ↓
Power BI & Dokumentation
```

Der modellierungs- und API-seitige technische Kern ist damit abgeschlossen.

Ab jetzt wird nicht mehr in neue Frequency-, Severity- oder
Tweedie-Tuning-Schleifen eingestiegen, sofern kein technischer Fehler
entdeckt wird.

---

## 4. Nächster technischer Arbeitsschritt

### Power BI & Dokumentation

Der nächste technische Arbeitsschritt folgt dem Projektfahrplan.

### Power BI

#### Seite 1 · Portfolio Overview 🔴

Ziel:

> Wie sieht das Portfolio aus?

Geplante Inhalte:

- [ ] Policenzahl
- [ ] Exposure
- [ ] beobachtete Frequency
- [ ] Schadensumme
- [ ] beobachtete Severity
- [ ] Observed Pure Premium
- [ ] zentrale Filter
- [ ] saubere Management-KPIs

#### Seite 2 · Risk Segmentation 🔴

Ziel:

> Wo konzentriert sich Risiko?

Geplante Inhalte:

- [ ] Risk-Segment-Verteilung
- [ ] Risk-Decile-Verteilung
- [ ] Risiko nach Fahreralter
- [ ] Risiko nach Fahrzeugalter
- [ ] Risiko nach BonusMalus
- [ ] Risiko nach Region
- [ ] Observed vs. Predicted
- [ ] HIGH-Segment und Loss-Konzentration sichtbar machen

#### Seite 3 · Expected Loss & Pure Premium 🔴

Ziel:

> Wo sind die höchsten Risikokosten?

Geplante Inhalte:

- [ ] Predicted Frequency
- [ ] Predicted Severity
- [ ] Two-Stage Pure Premium
- [ ] Tweedie Pure Premium
- [ ] Expected Loss
- [ ] Verteilungen
- [ ] Top-Risikoprofile
- [ ] Kalibrierung
- [ ] fachlich klare Trennung zwischen annualisierter Pure Premium und
  Exposure-korrigiertem Expected Loss

#### Seite 4 · Data Quality & Model Validation 🟡

Ziel:

> Können wir Daten und Modell vertrauen?

Geplante Inhalte:

- [ ] Data-Quality-Ergebnisse
- [ ] Pipeline-Status
- [ ] Frequency-Modellmetriken
- [ ] Severity-Modellmetriken
- [ ] Tweedie-Modellmetriken
- [ ] Modellversionen
- [ ] dokumentierte Modellgrenzen

Diese vierte Seite ist SHOULD und wird umgesetzt, sofern die drei
Kernseiten sauber abgeschlossen sind.

### Dokumentation

- [ ] `README.md` finalisieren
  - Problem
  - Geschäftsfrage
  - Architektur
  - Setup
  - Ausführung
  - zentrale Ergebnisse
  - Grenzen
- [ ] `docs/model_card.md` erstellen/finalisieren
  - Zweck
  - Datenbasis
  - Zielgrößen
  - Features
  - Modellversionen
  - Metriken
  - Grenzen
  - wofür das Modell nicht verwendet werden darf
- [ ] `docs/data_dictionary.md` finalisieren
- [ ] Architekturdiagramm final einbinden
- [ ] `docs/data_quality_report.md` final prüfen
- [ ] bestehende Kerntests und Ausführung dokumentieren
- [ ] Abschnitt `Subgroup Performance & Responsible Use` erstellen
  - observed vs. predicted nach geeigneten Gruppen
  - Fahreralter
  - Region
  - Area / Density
  - kompakt halten: ein Abschnitt, später eine Präsentationsfolie
- [ ] Statusbericht #7 vorbereiten

---

## 5. Feste Entscheidungen für den Wiedereinstieg

Diese Punkte werden nicht erneut aufgerollt:

- Canonical Train/Test Split bleibt unverändert.
- Frequency v2 ist final.
- Severity v2 ist final.
- Tweedie v1 ist als direkter Challenger final.
- Kein neues Frequency-/Severity-Tuning.
- Kein Holdout-basiertes Nachoptimieren.
- Exposure-Logik bleibt zwingend erhalten.
- Pure Premium ist annualisiert.
- Expected Loss wird immer mit Exposure berechnet.
- Severity-Limitierung wird transparent beibehalten.
- +37,79 % ist keine Headline-Kalibrierungsmetrik.
- Tweedie wird für Risk Score und Segmentierung verwendet.
- Two-Stage bleibt für Frequency-/Severity-Dekomposition erhalten.
- Risk Segments bleiben:
  `LOW` · `STANDARD` · `ELEVATED` · `HIGH`
- Risk Deciles bleiben 1–10.
- Handlungsempfehlungen bleiben Decision Support.
- `HIGH` bedeutet keine automatische Ablehnung.
- LightGBM wird nicht zusätzlich untersucht.
- SHAP wird nicht zusätzlich benötigt.
- API-Endpunkte bleiben:
  `/health` · `/risk-score` · `/pure-premium` · `/data-quality-summary`
- Bestehende API-Tests sind grün: `6 passed`.
- Nächster Fokus ist Power BI und Dokumentation.

---

## 6. Direkter Startpunkt beim nächsten Arbeiten

Nicht erneut bei Modellierung anfangen.

Der direkte Wiedereinstieg lautet:

1. Power-BI-Datenbasis und vorhandene Output-/PostgreSQL-Quellen prüfen.
2. Benötigte Tabellen und Beziehungen für die vier Dashboard-Seiten festlegen.
3. Mit `Portfolio Overview` beginnen.
4. Danach `Risk Segmentation`.
5. Danach `Expected Loss & Pure Premium`.
6. Erst danach die optionale Seite `Data Quality & Model Validation`.
7. Parallel nur die unmittelbar benötigte Dokumentation aktualisieren.
8. Keine neuen Modellversuche starten, solange kein technischer Fehler vorliegt.
