# Statusbericht – Woche 5

**Projekt:** Kfz Insurance Risk & Pure Premium Intelligence Platform
**Berichtszeitraum:** Technisches Arbeitspaket Woche 5, vorgezogen bearbeitet vom 20.08.2026 bis 25.08.2026
**Stand:** 25.08.2026
**Gesamtarbeitszeit:** Wird nach Abschluss der Zeiterfassung ergänzt

## 1. Aktueller Projektstand

Im fünften technischen Arbeitspaket wurde die Hauptmodellierungsphase des
Projekts abgeschlossen.

Auf Basis eines einmalig erzeugten, gemeinsamen Train-/Test-Splits auf
Policenebene wurden ein Exposure-gewichtetes Poisson-Modell für die
Schadenfrequenz und ein ClaimNb-gewichtetes Gamma-Modell für die
Schadenhöhe entwickelt und validiert.

Die beiden Modellkomponenten wurden anschließend zu einer annualisierten
Pure Premium kombiniert:

`Predicted Pure Premium = Predicted Frequency × Predicted Severity`

Dabei wird die Pure Premium ausschließlich als statistisch erwarteter,
annualisierter Schadenaufwand interpretiert. Sie stellt weder einen
Endkundenpreis noch einen Versicherungstarif dar.

Nach der ersten Modellversion wurde zusätzlich ein unabhängiger technischer
Review durchgeführt. Die daraus abgeleiteten sinnvollen Prüfungen wurden
systematisch umgesetzt. Dazu gehörten insbesondere eine erneute
Reproduzierbarkeitsprüfung des Curated Layers, robustere
Cross-Validation-Verfahren, alternative Spline-Spezifikationen,
Regularisierung, Large-Loss-Sensitivitätsanalysen sowie Lorenz- und
Gini-Auswertungen.

Auf dieser Grundlage wurden eine finale Frequency-v2- und eine
Severity-v2-Spezifikation festgelegt.

Die finalen Modelle wurden anschließend auf dem vollständigen verfügbaren
Datenbestand neu trainiert, als versionierte Modellartefakte gespeichert,
erneut geladen und auf exakte Reproduzierbarkeit geprüft.

Die finalen Policy-Level-Prognosen für 678.013 Policen wurden als Parquet
gespeichert und erfolgreich in die PostgreSQL-Tabelle
`model_predictions` übertragen.

Damit ist die geplante Hauptmodellierung einschließlich
Frequency, Severity, Pure Premium, Modellvalidierung,
Model-Versioning und PostgreSQL-Integration abgeschlossen.

## 2. Gemeinsamer Train-/Test-Split

Für Frequency und Severity wurde genau ein gemeinsamer Split auf
Policenebene verwendet.

Der Split wurde nicht separat für die beiden Modellkomponenten erzeugt.

Ergebnis:

- Gesamtes Portfolio: 678.013 Policen
- Training: 542.410 Policen
- Test: 135.603 Policen
- Überschneidung der `IDpol` zwischen Train und Test: 0
- Train Exposure: 286.776,50
- Test Exposure: 71.583,60
- Train Claims: 28.866
- Test Claims: 7.236
- Train Portfolio Frequency: 0,100657
- Test Portfolio Frequency: 0,101085
- Severity-geeignete Policen im Training: 19.944
- Severity-geeignete Policen im Test: 4.999
- Severity-geeignete Policen insgesamt: 24.943

Damit ist sichergestellt, dass dieselbe Police nicht gleichzeitig für das
Training und die Holdout-Bewertung verwendet wird.

## 3. Frequency-Modell

Das Frequency-Modell prognostiziert die annualisierte Schadenfrequenz.

Die fachlich festgelegte Modellformel lautet:

`y = ClaimNb / Exposure`

mit

`sample_weight = Exposure`

Als Modell wird ein `PoissonRegressor` innerhalb einer
Preprocessing-Pipeline verwendet.

### 3.1 Erste Modellversion

Die erste Spline-Version verwendete uniforme Spline-Knoten.

Holdout-Ergebnisse:

- Baseline Mean Poisson Deviance: 0,625748
- Frequency v1 Mean Poisson Deviance: 0,601319
- Poisson D²: 0,0390
- Tatsächliche Claims: 7.236
- Prognostizierte Claims: 7.211,98
- Portfolioabweichung: −0,33 %
- Gini: 0,2683

Die Risk-Decile-Kalibrierung zeigte bereits eine stabile und weitgehend
monotone Trennung der Frequency-Risikogruppen.

### 3.2 Post-Audit-Validierung

Im Rahmen der zusätzlichen Modellprüfung wurden uniforme und
quantilbasierte Spline-Knoten mit wiederholter Cross-Validation verglichen.

Die quantilbasierte Variante war über alle fünf untersuchten
Random-Seeds stabil besser als die uniforme Variante.

Anschließend wurden Knotenzahl, Polynomgrad und Regularisierung
ausschließlich auf den Trainingsdaten verglichen.

Als finale Frequency-v2-Spezifikation wurde festgelegt:

- `SplineTransformer`
- `knots = "quantile"`
- `n_knots = 8`
- `degree = 2`
- `alpha = 0.0`
- `log_density` weiterhin linear
- kategoriale Merkmale über One-Hot-Encoding

Eine zusätzliche Spline-Transformation von `log_density` brachte keinen
relevanten Vorteil und wurde deshalb nicht übernommen.

### 3.3 Finale Frequency-v2-Ergebnisse

Holdout-Ergebnisse:

- Baseline Mean Poisson Deviance: 0,625748
- Frequency v1 Mean Poisson Deviance: 0,601319
- Frequency v2 Mean Poisson Deviance: 0,592685
- Verbesserung gegenüber Baseline: 5,28 %
- Verbesserung gegenüber v1: 1,44 %
- Poisson D²: 0,0528
- Tatsächliche Claims: 7.236
- Prognostizierte Claims: 7.217,91
- Portfolioabweichung: −0,25 %
- Tatsächliche Portfoliofrequenz: 0,101085
- Prognostizierte Portfoliofrequenz: 0,100832
- Frequency-v2-Gini: 0,2903

Der Gini verbesserte sich gegenüber v1 von 0,2683 auf 0,2903.

Frequency v2 wird deshalb als finales Frequency-Modell verwendet.

## 4. Severity-Modell

Das Severity-Modell prognostiziert die durchschnittliche Schadenhöhe je
Schaden.

Die fachlich festgelegte Modellformel lautet:

`y = total_claim_amount / ClaimNb`

mit

`sample_weight = ClaimNb`

Für das Modell werden ausschließlich Policen verwendet, für die eine
fachlich konsistente und positive Schadenhöhe verfügbar ist.

Die Severity-Basis ist mit 24.943 geeigneten Policen deutlich kleiner als
die Frequency-Basis. Die Ergebnisse müssen deshalb vorsichtiger
interpretiert werden.

### 4.1 Erste Modellversion

Die erste Severity-Spline-Version zeigte in der ursprünglichen
Cross-Validation einen Vorteil gegenüber der konstanten Baseline.

Auf dem Holdout zeigte sich dieses Ergebnis jedoch nicht.

Holdout-Ergebnisse der ersten Version:

- Konstante Baseline Mean Gamma Deviance: 1,543630
- Severity v1 Mean Gamma Deviance: 1,615760
- Gamma D²: −0,0540
- Tatsächliche Claim-gewichtete Severity: 2.081,27
- Prognostizierte Claim-gewichtete Severity: 2.231,01
- Abweichung der beobachtbaren Schadenhöhe: +7,19 %
- Severity-v1-Gini: 0,0333

Damit war die erste Severity-Version auf dem Holdout schwächer als die
konstante Baseline.

## 5. Erweiterte Severity-Validierung

Wegen der starken Rechtsschiefe und einzelner sehr großer Schäden wurde
die Severity-Modellwahl nach dem technischen Review erneut untersucht.

### 5.1 Wiederholte Cross-Validation

Die ursprüngliche Cross-Validation wurde durch eine wiederholte
stratifizierte 5-Fold-Cross-Validation mit fünf unterschiedlichen
Random-Seeds ergänzt.

Die Bewertung erfolgte über gepoolte Out-of-Fold-Prognosen.

Ergebnisse:

- Baseline pooled Mean Gamma Deviance: 1,770221
- ursprüngliche Spline-Spezifikation: 1,644741
- Spline besser als Baseline: 5 von 5 Seeds

Damit konnte ausgeschlossen werden, dass der ursprüngliche
Cross-Validation-Vorteil ausschließlich durch einen einzelnen günstigen
Fold verursacht wurde.

### 5.2 Skalierung und Regularisierung

Für numerische Spline-Merkmale wurde anschließend eine selektive
Standardisierung getestet.

Kategoriale One-Hot-Merkmale wurden nicht skaliert.

Die Regularisierung wurde ausschließlich auf Trainingsdaten verglichen.

Die niedrigste mittlere Cross-Validation-Deviance wurde mit
`alpha = 0.1` erreicht.

Nach Anwendung der 1-SE-Regel wurde jedoch `alpha = 1.0` als stärker
regularisierte und robustere Spezifikation ausgewählt.

Diese Entscheidung wurde getroffen, bevor die finale v2-Spezifikation auf
dem Holdout bewertet wurde.

### 5.3 Large-Loss-Sensitivitätsanalyse

Zusätzlich wurde untersucht, ob eine Begrenzung sehr großer Schäden im
Training mit anschließendem Large-Loss-Loading die Modellstabilität
verbessert.

Getestet wurden unter anderem:

- 95. Perzentil
- 99. Perzentil
- 99,5. Perzentil
- 50.000 EUR
- 100.000 EUR

Die Bewertung erfolgte weiterhin auf dem nicht begrenzten Originalziel.

Keine der getesteten Varianten war gegenüber der ungekürzten
Severity-v2-Spezifikation überlegen.

Die Large-Loss-Variante wurde deshalb verworfen.

## 6. Finale Severity-v2-Ergebnisse

Die finale Severity-v2-Pipeline verwendet:

- One-Hot-Encoding für kategoriale Merkmale
- Spline-Transformation für numerische Risikomerkmale
- selektive Standardisierung der numerischen Modellblöcke
- `GammaRegressor`
- `alpha = 1.0`

Holdout-Ergebnisse:

- Konstante Baseline Mean Gamma Deviance: 1,543630
- Severity v1 Mean Gamma Deviance: 1,615760
- Severity v2 Mean Gamma Deviance: 1,567498
- Gamma D²: −0,0155
- Tatsächliche Claim-gewichtete Severity: 2.081,27
- Prognostizierte Claim-gewichtete Severity: 2.164,21
- Abweichung der beobachtbaren Schadenhöhe: +3,99 %
- Severity-v2-Gini: 0,0033

Severity v2 verbessert damit sowohl die Holdout-Deviance als auch die
Portfolioabweichung gegenüber Severity v1.

Die konstante Holdout-Baseline bleibt jedoch mit einer Mean Gamma Deviance
von 1,543630 weiterhin besser.

Dieser Befund wird ausdrücklich als Modellgrenze dokumentiert.

Severity v2 wird im Prototypen deshalb nicht als starker
Risikodifferenzierer interpretiert. Die Komponente wird primär zur
profilspezifischen monetären Quantifizierung der erwarteten Schadenhöhe
verwendet.

Die wichtigste Risikodifferenzierung des Two-Stage-Modells stammt aus der
Frequency-Komponente.

## 7. Pure Premium und Portfolio-Validierung

Frequency und Severity werden zu einer annualisierten Pure Premium
kombiniert:

`Predicted Pure Premium = Predicted Frequency × Predicted Severity`

Die Exposure-korrigierten Erwartungswerte werden anschließend berechnet als:

`Expected Claim Count = Predicted Frequency × Exposure`

`Expected Claim Amount = Predicted Pure Premium × Exposure`

Die annualisierte Pure Premium wird nicht direkt über Policen mit
unterschiedlicher Exposure aufsummiert.

### 7.1 Korrektur der ursprünglichen Pure-Premium-Diagnose

Bei der ersten Auswertung ergab sich auf dem Teilbestand mit vollständig
beobachtbarer Schadenhöhe eine Abweichung von +37,79 %.

Diese Zahl wird nicht als unbiased Modellkalibrierung interpretiert.

Der Grund ist, dass Policen mit fehlender Schadenhöhe aus diesem Vergleich
entfernt werden, obwohl ihre Claims im Frequency-Modell weiterhin
vorhanden sind.

Damit beschreibt die Kennzahl sowohl einen Missing-Severity-
Selektionseffekt als auch Modellabweichungen.

Die primären Kalibrierungsaussagen werden deshalb getrennt auf den jeweils
korrekten Bewertungsbasen berichtet:

- Frequency v2 auf allen 135.603 Holdout-Policen:
  Portfolioabweichung −0,25 %
- Severity v2 auf 4.999 vollständig beobachtbaren Severity-Policen:
  Schadenbetragsabweichung +3,99 %

Zusätzliche Imputationsszenarien für fehlende Schadenhöhen werden nur als
Sensitivitätsanalyse betrachtet und nicht als primäre Modellkennzahl
verwendet.

## 8. Lorenz- und Gini-Analyse

Lorenz- und Gini-Auswertungen wurden als zusätzliche Ranking-Diagnostik
bereits in dieses Arbeitspaket vorgezogen.

### Frequency

- Frequency v1 Gini: 0,2683
- Frequency v2 Gini: 0,2903
- Verbesserung: ca. +0,022

Frequency v2 besitzt damit die stärkste Ranking-Fähigkeit der aktuell
entwickelten Modellkomponenten.

### Severity

- Severity v1 Gini: 0,0333
- Severity v2 Gini: 0,0033

Die Severity-Komponente weist auf dem Holdout nur eine sehr geringe
Ranking-Fähigkeit auf.

### Pure Premium

Auf dem Teilbestand mit beobachtbarer Schadenhöhe wurde zusätzlich geprüft,
ob die Severity-Komponente die Loss-Rangfolge gegenüber der Frequency
verbessert.

Ergebnis:

- Frequency-only Loss Gini: 0,2372
- Pure-Premium-v2 Loss Gini: 0,2358
- Differenz: −0,0014

Die Severity-Komponente verbessert die Ranking-Leistung damit nicht.

Dieses Ergebnis bestätigt die Entscheidung, Frequency v2 als primären
Risikodifferenzierer zu verwenden und Severity v2 hauptsächlich zur
monetären Quantifizierung des erwarteten Schadenaufwands einzusetzen.

Die Pure-Premium-Gini-Auswertung ist aufgrund der fehlenden Schadenhöhen
als diagnostische Auswertung auf dem beobachtbaren Teilbestand zu
interpretieren.

## 9. Reproduzierbarkeit des Curated Layers

Im Rahmen des technischen Reviews wurde zusätzlich geprüft, ob der
Curated Layer vollständig aus dem versionierten Source Code erzeugt werden
kann.

Die Curated-Pipeline wurde über einen expliziten Einstiegspunkt in
`src/preprocessing/build_curated.py` ausführbar gemacht.

Die erneute Erzeugung ergab:

- 678.013 Policen
- 25 Spalten
- 0 doppelte `IDpol`
- 1.224 Policen mit gecappter Exposure
- 9 Policen mit auffällig hoher Claim-Anzahl
- 9.116 Policen mit fehlender Severity
- 1 Policy mit Claim-Count-Mismatch
- 6 orphan Severity-Policen

Der neu erzeugte Datensatz war wertidentisch mit dem bestehenden
`policy_curated.pq`.

Damit ist die Curated-Schicht aus dem versionierten Projektcode
reproduzierbar.

## 10. Finale Full-Data-Modelle

Nach Abschluss der Modellauswahl wurden die finalen Spezifikationen auf
dem vollständigen jeweils geeigneten Datenbestand neu trainiert.

### Frequency Full Refit

- Policen: 678.013
- Exposure: 358.360,11
- Claims: 36.102
- Portfolio Frequency: 0,100742
- Nicht-positive Exposure: 0
- Iterationen: 80

Finales Artefakt:

`models/frequency_poisson_quantile_spline_full_v2.joblib`

### Severity Full Refit

- geeignete Policen: 24.943
- repräsentierte Claims: 26.443
- fehlende Zielwerte: 0
- nicht-positive Zielwerte: 0
- Iterationen: 11

Finales Artefakt:

`models/severity_gamma_spline_scaled_full_v2.joblib`

Zusätzlich werden die zugehörigen Holdout-Artefakte separat versioniert:

- `models/frequency_poisson_quantile_spline_holdout_v2.joblib`
- `models/severity_gamma_spline_scaled_holdout_v2.joblib`

Die vorherigen v1-Artefakte bleiben zur Nachvollziehbarkeit der
Modellentwicklung erhalten.

## 11. Validierung der Modellartefakte

Die gespeicherten Full-Data-v2-Modelle wurden erneut geladen und auf dem
gesamten Portfolio ausgeführt.

Ergebnis:

### Frequency v2

- Artefakt vorhanden: Ja
- Prognosen exakt identisch: Ja
- maximale absolute Abweichung: 0,000000000000

### Severity v2

- Artefakt vorhanden: Ja
- Prognosen exakt identisch: Ja
- maximale absolute Abweichung: 0,000000000000

Damit reproduzieren die gespeicherten Modellartefakte die zuvor
berechneten Portfolio-Prognosen exakt.

## 12. Finale `model_predictions`-Schicht

Für das vollständige Portfolio wurde ein neuer versionierter Prediction Run
erzeugt.

Validierung der Parquet-Ausgabe:

- Zeilen: 678.013
- Spalten: 11
- eindeutige `IDpol`: 678.013
- doppelte `IDpol`: 0
- fehlende Werte: 0
- Prediction Runs innerhalb der Datei: 1
- nicht-positive Frequency-Prognosen: 0
- nicht-positive Severity-Prognosen: 0
- nicht-positive Pure-Premium-Prognosen: 0

Prediction Run:

`3e79d43b-d9e2-4edf-9056-be0827aa22f0`

Modellversionen:

- Frequency:
  `frequency_poisson_quantile_spline_full_v2`
- Severity:
  `severity_gamma_spline_scaled_full_v2`

Die Ausgabe wurde unter

`data/output/model_predictions.pq`

gespeichert.

## 13. PostgreSQL-Integration

Die finale Prediction-Datei wurde über die bestehende
PostgreSQL-Ladepipeline in die Tabelle `model_predictions` übertragen.

Geladene Datenmengen:

- `stg_policy`: 678.013
- `stg_claim`: 26.639
- `fact_policy_exposure`: 678.013
- `fact_claim`: 26.444
- `pipeline_runs`: 3
- `dq_check_results`: 27
- `model_predictions`: 678.013

Die finale Prediction-Run-ID wurde anschließend direkt in PostgreSQL über
DBeaver geprüft.

Ergebnis:

- Prediction Run ID:
  `3e79d43b-d9e2-4edf-9056-be0827aa22f0`
- Zeilen: 678.013
- eindeutige `IDpol`: 678.013
- Frequency-Modellversion:
  `frequency_poisson_quantile_spline_full_v2`
- Severity-Modellversion:
  `severity_gamma_spline_scaled_full_v2`

Damit ist der vollständige Pfad

`Modell → Parquet → PostgreSQL`

für die finalen v2-Modelle erfolgreich validiert.

## 14. Technische Probleme und Erkenntnisse

### Heavy-Tail-Effekt im Severity-Modell

Die Schadenhöhen weisen eine stark rechtsschiefe Verteilung mit einzelnen
sehr großen Schäden auf.

Dadurch reagiert die Gamma-Modellbewertung deutlich empfindlicher auf die
Zusammensetzung einzelner Validierungsfolds als die Frequency-Modellierung.

**Maßnahme:**

Die ursprüngliche Validierung wurde durch wiederholte,
stratifizierte Cross-Validation, gepoolte Out-of-Fold-Metriken,
Regularisierung und eine Large-Loss-Sensitivitätsanalyse ergänzt.

### Severity verbessert die Risikorangfolge kaum

Trotz besserer Calibration gegenüber v1 zeigt Severity v2 nahezu keine
zusätzliche Ranking-Fähigkeit.

**Konsequenz:**

Diese Schwäche wird nicht verborgen. Frequency v2 bleibt der primäre
Risikodifferenzierer. Severity v2 wird hauptsächlich für die monetäre
Quantifizierung eingesetzt.

### Fehlende Schadenhöhen

Für einen relevanten Teil der Schadenpolicen liegt keine vollständige
Severity-Beobachtung vor.

Dadurch ist ein direkter Vergleich von vorhergesagtem und tatsächlichem
Gesamtschaden auf einem reduzierten Teilbestand selektionsverzerrt.

**Konsequenz:**

Frequency- und Severity-Kalibrierung werden getrennt auf ihren jeweils
korrekten Bewertungsbasen berichtet. Analysen auf dem beobachtbaren
Teilbestand werden ausdrücklich als diagnostisch gekennzeichnet.

### Rechenzeit der erweiterten Cross-Validation

Die zusätzlichen Post-Audit-Experimente mit wiederholter Cross-Validation
und umfangreicheren Parameterkombinationen waren auf dem lokalen System
rechenintensiv.

**Konsequenz:**

Nach eindeutigen Ergebnissen wurde die Modelloptimierung bewusst beendet.
Weitere Tuning-Schleifen werden nicht durchgeführt.

## 15. Methodische Einschränkungen

Die finale Modellbewertung wird bewusst mit ihren Grenzen dokumentiert.

- Das Frequency-Modell zeigt eine gute Portfolio-Kalibrierung und eine
  messbare Ranking-Fähigkeit, erklärt jedoch nur einen begrenzten Anteil
  der individuellen Schadenvariabilität.
- Das Severity-Modell basiert auf einem wesentlich kleineren Datenbestand.
- Severity v2 verbessert v1, bleibt auf dem Holdout jedoch leicht schlechter
  als die konstante Severity-Baseline.
- Die Severity-Ranking-Fähigkeit ist sehr gering.
- Die Kombination mit Severity verbessert den Loss-Gini gegenüber
  Frequency allein nicht.
- Fehlende Schadenhöhen begrenzen die direkte Pure-Premium-Kalibrierung.
- Die ursprünglichen v1-Holdout-Ergebnisse waren bereits vor dem
  Post-Audit-Review bekannt. Die neuen v2-Spezifikationen wurden zwar auf
  Basis von Trainings-Cross-Validation ausgewählt, der Holdout kann deshalb
  nicht als vollständig unangetasteter einmaliger Blindtest bezeichnet
  werden.
- Die Modelle liefern statistische Erwartungswerte und keine kausalen
  Aussagen.
- Das System berechnet annualisierte Risikokosten und keinen
  Zeitreihen-Forecast.
- Die Ergebnisse dienen als Decision Support und nicht als automatische
  Annahme-, Ablehnungs- oder Tarifentscheidung.

## 16. Finale Modellentscheidung

Nach Abschluss der zusätzlichen Validierung wird folgende
Modellkonfiguration weiterverwendet:

### Frequency

**Frequency v2**

`frequency_poisson_quantile_spline_full_v2`

Begründung:

- beste Poisson-Deviance
- bessere Holdout-Kalibrierung als v1
- höherer Gini als v1
- stabile Ergebnisse über wiederholte Cross-Validation
- sehr geringe Portfolioabweichung

Frequency v2 ist der primäre Risikodifferenzierer des Two-Stage-Modells.

### Severity

**Severity v2**

`severity_gamma_spline_scaled_full_v2`

Begründung:

- bessere Holdout-Deviance als Severity v1
- deutlich geringere Portfolioabweichung als v1
- stabilere regularisierte Spezifikation
- Large-Loss-Alternativen brachten keinen zusätzlichen Vorteil

Die eingeschränkte Holdout- und Ranking-Leistung wird ausdrücklich
dokumentiert.

Severity v2 wird deshalb hauptsächlich zur erwarteten monetären
Schadenquantifizierung eingesetzt.

### Pure Premium

Die finale Two-Stage-Pure-Premium wird berechnet als:

`Frequency v2 × Severity v2`

Frequency trägt dabei den überwiegenden Anteil der empirisch messbaren
Risikodifferenzierung.

## 17. Abgeschlossene Arbeiten

- Gemeinsamen Policy-Level-Train-/Test-Split erstellt und validiert
- Split-Leakage über `IDpol` ausgeschlossen
- `notebooks/04_frequency_model.ipynb` entwickelt und erweitert
- Exposure-gewichtetes Poisson-Frequency-Modell aufgebaut
- Frequency-Baseline berechnet
- Cross-Validation und Hyperparametervergleich durchgeführt
- Uniforme und quantilbasierte Spline-Knoten verglichen
- Frequency v2 mit Quantile-Splines entwickelt
- Frequency Holdout-Deviance und D² berechnet
- Frequency Risk-Decile-Kalibrierung analysiert
- Frequency Lorenz Curve und Gini berechnet
- `notebooks/05_severity_model.ipynb` entwickelt und erweitert
- Geeignete Severity-Teilmenge fachlich definiert
- ClaimNb-gewichtetes Gamma-Severity-Modell aufgebaut
- Severity-Baseline berechnet
- Wiederholte stratifizierte Cross-Validation durchgeführt
- gepoolte OOF-Deviance verwendet
- selektive Skalierung getestet
- Regularisierung mit 1-SE-Regel ausgewählt
- Large-Loss-Sensitivitätsanalyse durchgeführt und verworfen
- Severity v2 entwickelt und bewertet
- Severity Lorenz Curve und Gini berechnet
- `notebooks/06_model_comparison.ipynb` erweitert
- Frequency und Severity zu Pure Premium kombiniert
- Exposure-korrekte erwartete Claim-Anzahl berechnet
- Exposure-korrekten erwarteten Schadenbetrag berechnet
- ursprüngliche selektionsverzerrte Pure-Premium-Auswertung korrigiert
- Frequency- und Severity-Kalibrierung getrennt ausgewiesen
- Pure-Premium-Lorenzkurve und Loss-Gini berechnet
- finale Modellentscheidung dokumentiert
- Curated-Pipeline reproduzierbar ausführbar gemacht
- Curated-Datensatz wertidentisch rekonstruiert
- Frequency v2 auf vollständigem Portfolio neu trainiert
- Severity v2 auf vollständigem geeigneten Datenbestand neu trainiert
- vier v2-Modellartefakte versioniert gespeichert
- Full-Data-Artefakte erneut geladen und exakt validiert
- `model_predictions.pq` mit 678.013 Policen erstellt
- eindeutige Prediction Run ID erzeugt
- finale Modellversionen in den Predictions dokumentiert
- `model_predictions` erfolgreich in PostgreSQL geladen
- PostgreSQL-Zeilenanzahl, `IDpol` und Modellversionen mit DBeaver geprüft

## 18. Nächste Schritte

Die Hauptmodelle werden ab diesem Punkt nicht weiter nachoptimiert.

Im nächsten technischen Arbeitspaket wird entsprechend dem Projektfahrplan
der direkte Tweedie-Challenger entwickelt.

Dafür wird weiterhin derselbe kanonische Policy-Level-Split verwendet.

Geplante nächste Schritte:

- Verfügbarkeit des Tweedie-Ziels prüfen
- Tweedie-Ziel als
  `total_claim_amount / Exposure` definieren
- Exposure als `sample_weight` verwenden
- ausschließlich Trainingsdaten für die Modellauswahl nutzen
- geeignete Tweedie-Power-Werte vergleichen
- Two-Stage-Modell und Tweedie auf identischer Bewertungsbasis vergleichen
- Mean Tweedie Deviance berechnen
- Decile-Kalibrierung vergleichen
- Lorenz- und Gini-Ergebnisse vergleichen
- Erklärbarkeit der finalen GLM-Modelle dokumentieren
- Risk Segments aus der Portfolioverteilung ableiten
- fachliche Handlungsempfehlungen formulieren
- anschließend die FastAPI-Schicht vorbereiten

LightGBM bleibt optional und wird nur untersucht, wenn nach Abschluss der
priorisierten Aufgaben ausreichend Zeit vorhanden ist.

## 19. Zusammenfassung

Das fünfte technische Arbeitspaket wurde erfolgreich abgeschlossen.

Der gemeinsame Train-/Test-Split wurde umgesetzt und sowohl das
Frequency- als auch das Severity-Modell wurden auf einer konsistenten
Datenbasis entwickelt.

Durch die zusätzliche Post-Audit-Validierung konnte insbesondere das
Frequency-Modell deutlich verbessert werden.

Frequency v2 erreicht auf dem Holdout eine Mean Poisson Deviance von
0,592685, eine Portfolioabweichung von nur −0,25 % und einen Gini von
0,2903.

Beim Severity-Modell konnten Deviance und Portfolioabweichung gegenüber
der ersten Version verbessert werden. Gleichzeitig zeigt die Validierung
klar, dass die verfügbaren Merkmale die individuelle Schadenhöhe nur sehr
begrenzt differenzieren können.

Diese Einschränkung wird bewusst als fachliches Ergebnis dokumentiert und
nicht durch weiteres Tuning verdeckt.

Die finalen Frequency-v2- und Severity-v2-Modelle wurden auf dem
vollständigen Datenbestand neu trainiert, versioniert gespeichert und
erfolgreich auf exakte Reproduzierbarkeit geprüft.

Für alle 678.013 Policen wurden finale Frequency-, Severity- und
Pure-Premium-Prognosen erzeugt und anschließend erfolgreich in PostgreSQL
übertragen.

Damit stehen nun ein reproduzierbarer Curated Layer, versionierte
Hauptmodelle, validierte Policy-Level-Prognosen und eine vollständig
befüllte `model_predictions`-Schicht als Grundlage für den folgenden
Tweedie-Challenger und die weitere Decision-Support-Schicht zur Verfügung.
