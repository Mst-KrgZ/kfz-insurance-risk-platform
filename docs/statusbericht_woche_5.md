
# Statusbericht – Woche 5

**Projekt:** Kfz Insurance Risk & Pure Premium Intelligence Platform
**Berichtszeitraum:** Technisches Arbeitspaket Woche 5, vorgezogen bearbeitet vom 20.08.2026 bis 24.08.2026
**Stand:** 24.08.2026
**Gesamtarbeitszeit:** Wird nach Abschluss der Zeiterfassung ergänzt

## 1. Aktueller Projektstand

In der fünften Projektphase wurde die Hauptmodellierung für Schadenhäufigkeit,
Schadenhöhe und Pure Premium vollständig umgesetzt.

Zunächst wurde ein einmaliger und reproduzierbarer Policy-Level-Train/Test-
Split erstellt. Dieser Split wurde anschließend für Frequency und Severity
gemeinsam verwendet, sodass keine voneinander abweichenden Datenaufteilungen
zwischen den Modellkomponenten entstanden.

Für die Schadenhäufigkeit wurde ein Exposure-gewichtetes Poisson-Modell
entwickelt. Verschiedene Feature-Spezifikationen und Regularisierungsstärken
wurden ausschließlich innerhalb der Trainingsdaten über eine 5-Fold-
Cross-Validation verglichen.

Die beste Frequency-Spezifikation verwendet Spline-Transformationen für
kontinuierliche Risikomerkmale mit sechs Knoten, Grad 3 und ohne zusätzliche
Regularisierung.

Auf dem unabhängigen Holdout-Datensatz erreicht das finale Frequency-Modell
eine Mean Poisson Deviance von 0,601319. Gegenüber der konstanten Baseline
entspricht dies einer Verbesserung von rund 3,90 %.

Für die Schadenhöhe wurde ein Gamma-Regressionsmodell entwickelt. Hierfür
wurden ausschließlich Policen mit vollständig und konsistent beobachteter
Severity verwendet.

Auch für Severity wurden verschiedene Feature-Spezifikationen und
Hyperparameter per Cross-Validation verglichen. Die beste Spezifikation
verwendet ebenfalls sechs Spline-Knoten, Grad 3 und `alpha=0`.

Die Severity-Modellierung zeigt jedoch eine deutlich geringere
Generalisierungsstabilität als die Frequency-Modellierung. Obwohl die
Spline-Spezifikation innerhalb der Cross-Validation die konstante Baseline
übertrifft, liegt ihre Holdout Mean Gamma Deviance mit 1,615760 über der
Holdout-Baseline von 1,543630.

Diese eingeschränkte Generalisierungsfähigkeit wurde nicht durch nachträgliche
Anpassung an den Testdatensatz korrigiert, sondern ausdrücklich als
Modelllimitierung dokumentiert.

Anschließend wurden Frequency und Severity zur prognostizierten Pure Premium
zusammengeführt.

Nach Abschluss der unabhängigen Modellbewertung wurden die festgelegten
Frequency- und Severity-Spezifikationen auf den vollständig verfügbaren
Daten neu geschätzt und für alle 678.013 Policen finale Policy-Level-
Prognosen erzeugt.

Die finalen Predictions wurden sowohl als reproduzierbarer Parquet-Output als
auch in PostgreSQL gespeichert. Zusätzlich wurde eine finale analytische View
für nachgelagerte Auswertungen und Power BI erstellt.

## 2. Abgeschlossene Arbeiten

### Gemeinsamer Train-/Test-Split

- Einheitlichen Policy-Level-Train/Test-Split erstellt
- 80/20-Aufteilung mit `random_state=42` verwendet
- Schadenstatus zur stabilen Aufteilung stratifiziert
- 542.410 Trainingspolicen erstellt
- 135.603 Holdout-Testpolicen erstellt
- Überschneidung zwischen Train und Test ausgeschlossen
- Claim-Policy-Rate zwischen Train und Test abgeglichen
- Exposure-Verteilungen zwischen Train und Test geprüft
- Split dauerhaft als `policy_train_test_split.pq` gespeichert
- Gespeicherten Split erneut geladen und reproduzierbar validiert
- Zweiten unabhängigen Split für Severity bewusst vermieden

### Frequency-Modell

- `notebooks/04_frequency_model.ipynb` erstellt
- Annualisierte Frequency als `ClaimNb / Exposure` modelliert
- `Exposure` als Sample Weight verwendet
- Leakage- und Feature-Audit durchgeführt
- Baseline Mean Poisson Deviance von 0,625748 bestimmt
- Grouped-, Raw-Linear- und Spline-Spezifikationen verglichen
- 5-Fold-Cross-Validation ausschließlich auf Trainingsdaten durchgeführt
- Regularisierungsstärken per Cross-Validation verglichen
- Spline-Hyperparameter systematisch optimiert
- Sechs Spline-Knoten, Grad 3 und `alpha=0` ausgewählt
- Finales Poisson-Modell auf vollständigem Trainingsdatensatz geschätzt
- Holdout Mean Poisson Deviance von 0,601319 erreicht
- Verbesserung gegenüber der Baseline von rund 3,90 % erreicht
- Poisson-D² von 0,0390 dokumentiert
- 7.236 tatsächlich beobachtete Holdout-Schäden bestätigt
- 7.211,98 erwartete Holdout-Schäden prognostiziert
- Abweichung der erwarteten Schadenanzahl von nur ca. -0,33 % bestätigt
- Risk-Decile-Kalibrierung durchgeführt
- Monotone Risikodifferenzierung der Frequency-Prognosen bestätigt
- Frequency-Modellartefakt gespeichert
- Modellartefakt erneut geladen und Predictions exakt reproduziert

### Severity-Modell

- `notebooks/05_severity_model.ipynb` erstellt
- Gemeinsamen Policy-Level-Split aus der Frequency-Modellierung übernommen
- Severity-Eligibility-Regeln explizit umgesetzt
- Policen mit fehlender Severity ausgeschlossen
- Inkonsistente Frequency-Severity-Fälle ausgeschlossen
- 24.943 vollständig konsistente Severity-Policen bestätigt
- 19.944 Severity-Trainingspolicen verwendet
- 4.999 Severity-Holdout-Policen verwendet
- Severity als `total_claim_amount / ClaimNb` definiert
- `ClaimNb` als Sample Weight verwendet
- Stark rechtsschiefe Heavy-Tail-Verteilung dokumentiert
- Grouped-, Raw-Linear- und Spline-Spezifikationen verglichen
- Convergence-Probleme der Raw-Linear-Spezifikation erkannt
- Numerische Raw-Features standardisiert und Convergence stabilisiert
- 5-Fold-Cross-Validation durchgeführt
- Spline-Hyperparameter systematisch optimiert
- Sechs Spline-Knoten, Grad 3 und `alpha=0` ausgewählt
- CV Mean Gamma Deviance von 1,637578 erreicht
- CV-Baseline von 1,770462 bestimmt
- Spline-Modell innerhalb der CV gegenüber der Baseline verbessert
- Finales Gamma-Modell auf vollständigem Severity-Trainingsdatensatz geschätzt
- Holdout Mean Gamma Deviance von 1,615760 dokumentiert
- Holdout-Baseline von 1,543630 dokumentiert
- Gamma-D² von -0,0540 dokumentiert
- Eingeschränkte Holdout-Generalisation ausdrücklich als Modelllimitierung dokumentiert
- Keine nachträgliche Hyperparameter-Anpassung auf Basis des Testdatensatzes durchgeführt
- Severity-Kalibrierung nach prognostizierten Risikogruppen untersucht
- Überprognose im höchsten Severity-Dezil dokumentiert
- Severity-Modellartefakt gespeichert
- Gespeichertes Modell erneut geladen und Predictions exakt reproduziert
- Notebook mit Restart Kernel + Run All erfolgreich validiert

### Pure Premium und Modellzusammenführung

- `notebooks/06_model_comparison.ipynb` erstellt
- Frequency- und Severity-Modellartefakte gemeinsam geladen
- Einheitlichen Holdout-Datensatz verwendet
- `predicted_pure_premium = predicted_frequency × predicted_severity` berechnet
- `expected_claim_count = predicted_frequency × Exposure` berechnet
- `expected_claim_amount = predicted_pure_premium × Exposure` berechnet
- Predictions für alle 135.603 Holdout-Policen technisch validiert
- Fehlende und nicht-positive Modellprognosen ausgeschlossen
- Pure-Premium-Verteilung untersucht
- Pure-Premium-Risikodezile erstellt
- Beobachtete und prognostizierte Pure Premium nach Risikodezil verglichen
- Erkennbare Risikodifferenzierung im höchsten Risikodezil bestätigt
- Überprognose in den höchsten Pure-Premium-Risikogruppen dokumentiert

### Umgang mit fehlenden Severity-Informationen

- 1.813 Holdout-Schadenpolicen mit fehlendem Schadenbetrag identifiziert
- 1.924 Claims mit fehlender Severity-Information im Holdout bestätigt
- Fehlende Schadenbeträge nicht als null interpretiert
- Full-Portfolio-Frequency weiterhin auf allen Holdout-Policen bewertet
- Schadenbetrags- und Pure-Premium-Vergleiche auf beobachtbare Fälle begrenzt
- Selektionsverzerrung der Observable-Amount-Teilmenge dokumentiert
- Abweichungen dieser Teilmenge bewusst nicht als unverzerrte Portfolio-
  Fehlkalibrierung interpretiert
- Zunehmenden Anteil fehlender Severity-Werte in hohen Risikodezilen dokumentiert

### Full-Data-Refit und Portfolio-Scoring

- Final festgelegtes Frequency-Modell auf allen 678.013 Policen neu geschätzt
- Full-Data-Frequency-Modell erfolgreich konvergiert
- Final festgelegtes Severity-Modell auf allen 24.943 geeigneten Severity-
  Policen neu geschätzt
- Full-Data-Severity-Modell erfolgreich konvergiert
- Evaluation-Modelle und Full-Data-Inferenzmodelle bewusst getrennt gehalten
- Full-Data-Frequency-Artefakt gespeichert
- Full-Data-Severity-Artefakt gespeichert
- Beide Full-Data-Artefakte erneut geladen und exakt reproduziert
- Finale Predictions für alle 678.013 Policen erzeugt
- 36.093,70 erwartete Schäden für das gesamte Portfolio berechnet
- 36.102 tatsächlich beobachtete Schäden als Portfolio-Sanity-Check bestätigt
- 78.428.858,76 erwarteten Schadenbetrag prognostiziert
- Erwarteten Schadenbetrag aufgrund fehlender Severity-Werte nicht als
  unabhängige Modellgütebewertung interpretiert

### PostgreSQL Prediction Layer

- Finalen Prediction-Datensatz mit 678.013 Policen erstellt
- Eindeutige `prediction_run_id` implementiert
- Frequency- und Severity-Modellversionen gespeichert
- `predicted_frequency` gespeichert
- `predicted_severity` gespeichert
- `predicted_pure_premium` gespeichert
- `exposure_used` gespeichert
- `expected_claim_count` gespeichert
- `expected_claim_amount` gespeichert
- `scored_at` gespeichert
- Prediction-Datensatz als `data/output/model_predictions.pq` gespeichert
- PostgreSQL-Tabelle `model_predictions` erstellt
- Zusammengesetzten Primärschlüssel `(prediction_run_id, idpol)` eingerichtet
- Constraints für gültige Prognosewerte implementiert
- 678.013 Prediction-Zeilen über PostgreSQL `COPY` geladen
- `src/database/load_postgres.py` um Prediction-Loader erweitert
- Reload desselben Prediction-Runs ohne Duplikate ermöglicht
- Historisierung zukünftiger Prediction-Runs vorbereitet
- `vw_model_prediction_analysis` erstellt
- View automatisch auf den aktuellsten Scoring-Lauf ausgerichtet
- Claim-Count-Residuals bereitgestellt
- Claim-Amount-Residuals für beobachtbare Schadenbeträge bereitgestellt
- 678.013 eindeutige View-Zeilen auf PostgreSQL-Ebene bestätigt
- SQL-seitige Expected Claims von 36.093,70 validiert
- SQL-seitigen Expected Claim Amount von 78.428.858,76 validiert
- Python- und PostgreSQL-Ergebnisse vollständig abgeglichen

## 3. Technische Probleme und Lösungen

### Einheitlicher Split für Frequency und Severity

Frequency und Severity benötigen unterschiedliche Zielvariablen und
unterschiedliche gültige Datenmengen. Separate Train-/Test-Splits hätten
jedoch dazu geführt, dass die beiden Modellkomponenten auf unterschiedlichen
Policy-Gruppen bewertet werden.

**Lösung:**

Ein gemeinsamer Policy-Level-Split wurde einmalig auf dem vollständigen
Portfolio erstellt und dauerhaft gespeichert.

Severity verwendet ausschließlich die für das Modell geeigneten Policen aus
diesem bereits definierten Split.

Dadurch bleibt die spätere Pure-Premium-Bewertung methodisch konsistent.

### Heavy-Tail-Struktur der Schadenhöhe

Die Severity-Zielvariable weist einen ausgeprägten rechten Tail mit wenigen
sehr hohen Großschäden auf.

Dadurch schwanken die durchschnittlichen Schadenhöhen zwischen einzelnen
Cross-Validation-Folds deutlich stärker als bei der Frequency-Modellierung.

**Lösung:**

Die Großschäden wurden nicht allein zur Verbesserung der Modellmetriken
entfernt.

Stattdessen wurde eine Gamma-Regressionsstruktur mit `ClaimNb` als Sample
Weight verwendet und die Variabilität der Cross-Validation ausdrücklich
dokumentiert.

### Severity-Modell übertrifft Holdout-Baseline nicht

Die beste Severity-Spline-Spezifikation verbessert die durchschnittliche
Cross-Validation-Leistung gegenüber der fold-spezifischen Baseline.

Auf dem unabhängigen Holdout-Testdatensatz liegt die Mean Gamma Deviance des
Modells jedoch über der konstanten Baseline.

**Lösung:**

Die Holdout-Ergebnisse wurden nicht für eine nachträgliche Modellselektion
oder erneutes Hyperparameter-Tuning verwendet.

Die per Cross-Validation ausgewählte Spezifikation wurde beibehalten und die
schwächere Generalisierungsfähigkeit als transparente Modelllimitierung
dokumentiert.

### Fehlende Schadenbeträge bei Schadenpolicen

Für einen relevanten Teil der Schadenpolicen liegt kein beobachteter
Schadenbetrag vor.

Würden diese Fälle als Schadenbetrag null interpretiert, wäre die
Pure-Premium-Bewertung systematisch verzerrt.

**Lösung:**

Fehlende Schadenbeträge wurden weiterhin als unbekannt behandelt.

Frequency wird auf dem vollständigen Holdout bewertet. Schadenbetrags- und
Pure-Premium-Vergleiche werden nur für beobachtbare Fälle durchgeführt und
explizit als diagnostische Analysen gekennzeichnet.

### Trennung von Evaluation und finaler Inferenz

Ein auf dem vollständigen Datenbestand trainiertes Modell darf nicht zur
unabhängigen Bewertung der Modellgüte verwendet werden.

**Lösung:**

Holdout-trainierte Modellartefakte und Full-Data-Inferenzmodelle werden
getrennt gespeichert.

Alle berichteten unabhängigen Modellmetriken stammen weiterhin aus der
Holdout-Bewertung.

Der Full-Data-Refit dient ausschließlich der finalen Portfolio-Inferenz.

### Versionierung der finalen Predictions

Eine Tabelle mit `idpol` als alleiniger Primärschlüssel würde zukünftige
Scoring-Läufe überschreiben.

**Lösung:**

Jeder Scoring-Lauf erhält eine eindeutige `prediction_run_id`.

Die Kombination aus `prediction_run_id` und `idpol` bildet den Primärschlüssel.
Dadurch können spätere Modellversionen und Scoring-Läufe historisiert werden.

## 4. Ergebnisse und fachliche Erkenntnisse

Das finale Frequency-Modell zeigt eine stabile und fachlich plausible
Risikodifferenzierung.

Auf dem Holdout-Datensatz beträgt die Mean Poisson Deviance 0,601319 gegenüber
0,625748 bei der konstanten Baseline.

Die erwartete Holdout-Schadenanzahl von 7.211,98 liegt sehr nahe an den
7.236 tatsächlich beobachteten Schäden.

Die Risk-Decile-Analyse bestätigt eine klare und weitgehend monotone
Differenzierung zwischen niedrigen und hohen Frequency-Risiken.

Die Severity-Modellierung ist deutlich anspruchsvoller.

Obwohl die Spline-Spezifikation innerhalb der Cross-Validation zusätzliche
Prognoseinformation gegenüber einer konstanten Baseline zeigt, lässt sich
dieser Vorteil auf dem Holdout-Datensatz nicht stabil reproduzieren.

Die Schadenhöhe wird stärker durch wenige extreme Großschäden und vermutlich
durch Schadenmerkmale beeinflusst, die im vorhandenen Policy-Datensatz nicht
enthalten sind.

Die kombinierte Pure Premium zeigt dennoch eine erkennbare
Risikodifferenzierung.

Das höchste prognostizierte Pure-Premium-Dezil weist auch die höchste
beobachtete Pure Premium auf. Gleichzeitig überschätzt das Modell die
Schadenbelastung in den höchsten Risikogruppen deutlich.

Diese Überprognose steht insbesondere mit der eingeschränkten
Generalisierungsfähigkeit des Severity-Modells in Zusammenhang.

Die fehlenden Severity-Informationen treten zudem nicht gleichmäßig über die
Risikodezile auf. Ihr Anteil steigt in den höheren prognostizierten
Risikogruppen an.

Die finale Portfolio-Scoring-Pipeline produziert für alle 678.013 Policen
gültige und reproduzierbare Predictions.

Für den Full-Data-Refit werden aggregiert 36.093,70 Schäden erwartet, während
im Datenbestand 36.102 Schäden beobachtet werden.

Dieser Vergleich dient ausschließlich als technischer Portfolio-Sanity-Check
und nicht als unabhängige Modellgütebewertung.

## 5. Offene Aufgaben

- Tweedie-Regressionsmodell als Challenger entwickeln
- Mean Tweedie Deviance berechnen
- Lorenz-Kurve und Gini-Kennzahl ergänzen
- Poisson × Gamma und Tweedie auf identischer Testbasis vergleichen
- Finales Modell beziehungsweise finale Modellstrategie festlegen
- Vier operative Risikosegmente definieren
- Handlungsempfehlungen je Risikosegment ableiten
- FastAPI-Scoring-Schnittstelle entwickeln
- Finale Modelloutputs für Power BI vorbereiten
- Modellkarten und technische Dokumentation weiter vervollständigen

## 6. Nächste Schritte

Im nächsten technischen Arbeitspaket wird ein Tweedie-Regressionsmodell als
Challenger zur zweistufigen Poisson-Gamma-Modellstrategie entwickelt.

Das Challenger-Modell wird auf demselben Policy-Level-Split und derselben
unabhängigen Holdout-Basis bewertet.

Anschließend werden Poisson × Gamma und Tweedie mit geeigneten
Deviance-Metriken, Risk-Decile-Kalibrierung sowie Lorenz-/Gini-Analysen
verglichen.

Auf Basis der finalen Risikoprognosen werden vier operative Risikosegmente
abgeleitet und mit konkreten fachlichen Handlungsempfehlungen verknüpft.

Danach wird die Scoring-Logik über eine FastAPI-Schnittstelle für einzelne
Policen und Batch-Anfragen bereitgestellt.

## 7. Zusammenfassung

Die Hauptmodellierungsphase wurde erfolgreich abgeschlossen.

Ein gemeinsamer, reproduzierbarer Train-/Test-Split bildet die Grundlage für
die Frequency-, Severity- und Pure-Premium-Modellierung.

Das finale Poisson-Frequency-Modell zeigt auf dem unabhängigen Holdout eine
stabile Verbesserung gegenüber der Baseline und eine gute
Portfolio-Kalibrierung.

Das Gamma-Severity-Modell liefert innerhalb der Cross-Validation zusätzliche
Prognoseinformation, zeigt auf dem Holdout jedoch eine eingeschränkte
Generalisierungsfähigkeit. Diese Modellgrenze wurde transparent dokumentiert
und nicht durch nachträgliches Test-Tuning kaschiert.

Frequency und Severity wurden erfolgreich zu einer prognostizierten Pure
Premium zusammengeführt und über Risikodezile analysiert.

Nach Abschluss der Holdout-Bewertung wurden die final festgelegten Modelle auf
den vollständig verfügbaren Daten neu geschätzt und zur Erstellung von
Policy-Level-Predictions für alle 678.013 Policen verwendet.

Die finalen Prognosen wurden reproduzierbar gespeichert, in PostgreSQL geladen
und über `vw_model_prediction_analysis` für nachgelagerte Analysen
bereitgestellt.

Damit ist das technische Arbeitspaket Woche 5 abgeschlossen und die Grundlage
für Challenger-Modellierung, finale Risikosegmentierung und API-Scoring
geschaffen.
