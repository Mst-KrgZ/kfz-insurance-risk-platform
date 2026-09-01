
# Statusbericht – Woche 6

**Projekt:** Kfz Insurance Risk & Pure Premium Intelligence Platform
**Berichtszeitraum:** Technisches Arbeitspaket Woche 6, vorgezogen bearbeitet vom 25.08.2026 bis 01.09.2026
**Stand:** 01.09.2026
**Gesamtarbeitszeit:** Wird nach Abschluss der Zeiterfassung ergänzt

## 1. Aktueller Projektstand

Im sechsten technischen Arbeitspaket wurde die bestehende
Two-Stage-Modellierung um einen direkten Tweedie-Challenger,
eine systematische Modell-Erklärbarkeit, eine portfolioorientierte
Risikosegmentierung sowie eine FastAPI-Schnittstelle erweitert.

Ausgangspunkt waren die im vorherigen Arbeitspaket finalisierten Modelle:

- Frequency v2:
  `frequency_poisson_quantile_spline_full_v2`
- Severity v2:
  `severity_gamma_spline_scaled_full_v2`

Die daraus abgeleitete Two-Stage-Pure-Premium bleibt definiert als:

`Predicted Pure Premium = Predicted Frequency × Predicted Severity`

Als Challenger wurde zusätzlich ein direkter `TweedieRegressor`
entwickelt, der den annualisierten Schadenaufwand ohne separate
Frequency- und Severity-Komponente modelliert.

Die Zieldefinition lautet:

`y = total_claim_amount / Exposure`

mit:

`sample_weight = Exposure`

Die Modellauswahl wurde weiterhin ausschließlich auf der Trainingsseite
des bereits bestehenden kanonischen Policy-Level-Splits durchgeführt.

Es wurde kein neuer Train-/Test-Split erzeugt.

Nach Abschluss des Tweedie-Modells wurden Two-Stage und Tweedie auf
einer möglichst identischen Bewertungsbasis anhand von Mean Tweedie
Deviance, Portfolio-Kalibrierung, Lorenz-Kurve und Gini verglichen.

Anschließend wurden die finalen Modelle hinsichtlich ihrer Struktur und
ihrer wichtigsten Einflussfaktoren interpretiert.

Auf Grundlage der Tweedie-Pure-Premium wurden danach vier
portfolioabhängige Risikosegmente sowie zehn Risikodezile definiert.

Die Ergebnisse wurden in eine Decision-Support-Schicht überführt und mit
fachlichen Handlungsempfehlungen verbunden.

Zum Abschluss des Arbeitspakets wurde die bestehende FastAPI-Schicht
überarbeitet und gegen die finale Modell- und Segmentierungslogik
validiert.

Damit sind Challenger-Modell, Explainability, Risk Segmentation,
Business Actions und API technisch abgeschlossen.

## 2. Datenbasis des Tweedie-Modells

Das direkte Tweedie-Modell benötigt pro Police einen tatsächlich
beobachtbaren Gesamtschaden.

Aufgrund der bereits dokumentierten fehlenden Schadenhöhen steht dieser
Zielwert nicht für alle 678.013 Policen zur Verfügung.

Für die Tweedie-Modellierung wurden deshalb ausschließlich Policen mit
gültigem beobachtbarem Schadenbetrag verwendet.

Ergebnis:

- Gesamtportfolio: 678.013 Policen
- Tweedie-geeignete Policen: 668.896
- nicht vollständig beobachtbare Policen: 9.117
- Tweedie-Training: 535.106 Policen
- Tweedie-Holdout: 133.790 Policen
- Train Exposure: 283.089,32
- Test Exposure: 70.664,51
- tatsächlicher Schaden im Training: 48.852.982,50 EUR
- tatsächlicher Schaden im Holdout: 11.055.690,67 EUR
- beobachtete Exposure-gewichtete Holdout-Pure-Premium: 156,45 EUR

Die nicht beobachtbaren Policen bestehen überwiegend aus Schadenpolicen
mit fehlender Severity-Information.

Dadurch unterscheidet sich die Tweedie-Bewertungsbasis strukturell vom
vollständigen Frequency-Portfolio.

Dieser Selektionsaspekt wird bei allen Modellvergleichen ausdrücklich
berücksichtigt.

## 3. Tweedie-Modell

Der Tweedie-Challenger modelliert die annualisierte Pure Premium direkt.

Die fachliche Modellformel lautet:

`y = total_claim_amount / Exposure`

mit:

`sample_weight = Exposure`

Verwendet wird ein `TweedieRegressor` mit Log-Link innerhalb derselben
grundsätzlichen Feature-Logik wie beim finalen Frequency-Modell.

Kategoriale Merkmale:

- `VehPower`
- `VehBrand`
- `VehGas`
- `Region`

Numerische Spline-Merkmale:

- `DrivAge`
- `VehAge`
- `BonusMalus`

Zusätzlich wird

- `log_density`

linear verwendet.

Damit bleibt der Challenger trotz direkter Loss-Modellierung ein
erklärbares GLM-basiertes Modell.

## 4. Train-Side-Modellwahl

Die Tweedie-Spezifikation wurde ausschließlich auf Trainingsdaten
ausgewählt.

Der Holdout wurde erst nach Festlegung der finalen Challenger-
Spezifikation für die Bewertung verwendet.

Als Startpunkt wurde entsprechend dem Projektfahrplan eine Tweedie-Power
von 1,9 verwendet.

Ausgewählte Power- und Regularisierungsspezifikationen wurden auf der
Trainingsseite verglichen.

Die finale Spezifikation wurde vor der Holdout-Bewertung festgelegt als:

- `TweedieRegressor`
- `power = 1.9`
- `alpha = 0.0`
- Log-Link
- Quantile-Splines
- `n_knots = 8`
- `degree = 2`

Damit wurde nach der Modellwahl keine weitere nachträgliche
Holdout-Optimierung vorgenommen.

## 5. Tweedie-Holdout-Ergebnisse

Für das finale direkte Tweedie-Modell wurden folgende Ergebnisse auf der
beobachtbaren Holdout-Basis ermittelt:

- konstante Baseline Mean Tweedie Deviance: 34,602470
- Tweedie Mean Tweedie Deviance: 34,364453
- Verbesserung gegenüber Baseline: ca. 0,69 %
- tatsächlicher Holdout-Schaden: 11.055.690,67 EUR
- prognostizierter Holdout-Schaden: ca. 11.762.870 EUR
- Portfolioabweichung: +6,40 %
- tatsächliche Exposure-gewichtete Pure Premium: 156,45 EUR
- prognostizierte Exposure-gewichtete Pure Premium: 166,46 EUR
- Gini: 0,2677
- Modelliterationen: 373

Damit schlägt der direkte Tweedie-Challenger die konstante Baseline
hinsichtlich der Mean Tweedie Deviance.

Die Portfolio-Kalibrierung ist deutlich näher am beobachteten
Gesamtschaden als beim Two-Stage-Modell auf derselben Bewertungsbasis.

## 6. Two-Stage vs. Tweedie

Für einen faireren Modellvergleich wurden Tweedie und das bestehende
Two-Stage-Modell auf derselben beobachtbaren Holdout-Basis bewertet.

### 6.1 Mean Tweedie Deviance

- Tweedie: 34,364453
- Two-Stage: 34,356826

Das Two-Stage-Modell erreicht damit eine geringfügig niedrigere
Tweedie-Deviance.

Der Unterschied ist jedoch sehr klein.

### 6.2 Portfolio-Kalibrierung

Tweedie:

- prognostizierter Schaden: ca. 11,76 Mio. EUR
- tatsächlicher Schaden: ca. 11,06 Mio. EUR
- Abweichung: +6,40 %

Two-Stage:

- prognostizierter Schaden: ca. 15,07 Mio. EUR
- tatsächlicher Schaden: ca. 11,06 Mio. EUR
- Abweichung: +36,29 %

Damit besitzt das direkte Tweedie-Modell auf dieser Bewertungsbasis eine
deutlich bessere Portfolio-Kalibrierung.

### 6.3 Ranking-Fähigkeit

- Tweedie Gini: 0,2677
- Two-Stage Loss Gini: ca. 0,2358

Auch bei der Ranking-Fähigkeit liegt der direkte Tweedie-Challenger
vor dem Two-Stage-Pure-Premium-Modell.

## 7. Modellentscheidung

Der Modellvergleich ergibt kein eindeutiges Ergebnis zugunsten nur eines
Ansatzes.

Das Two-Stage-Modell besitzt den Vorteil einer fachlich klaren
Dekomposition:

`Frequency × Severity`

Dadurch kann getrennt analysiert werden,

- wie häufig Schäden erwartet werden und
- wie hoch ein Schaden im Mittel erwartet wird.

Diese Zerlegung ist insbesondere für fachliche Interpretation und
Modell-Diagnostik wertvoll.

Der direkte Tweedie-Challenger besitzt dagegen auf der vergleichbaren
Holdout-Basis:

- deutlich bessere Portfolio-Kalibrierung
- höhere Ranking-Fähigkeit
- eine direkte Modellierung der annualisierten Risikokosten

Die Mean Tweedie Deviance ist beim Two-Stage-Modell lediglich minimal
besser.

Deshalb werden beide Ansätze weitergeführt.

Das Two-Stage-Modell bleibt für die fachliche Frequency-/Severity-
Dekomposition erhalten.

Das direkte Tweedie-Modell wird als kanonischer Risikoscore für die
Portfolio-Segmentierung verwendet.

## 8. Finale Tweedie-Artefakte

Nach Abschluss der Modellauswahl wurde die finale Tweedie-Spezifikation
auf dem vollständigen geeigneten Datenbestand neu trainiert.

Full-Data-Refit:

- geeignete Policen: 668.896
- Exposure: 353.753,83
- Modelliterationen: 224

Finale Modellartefakte:

`models/tweedie_direct_pure_premium_holdout_v1.joblib`

`models/tweedie_direct_pure_premium_full_v1.joblib`

Die Policy-Level-Prognosen wurden zusätzlich gespeichert unter:

`data/output/tweedie_predictions.pq`

Validierung:

- Zeilen: 678.013
- Spalten: 5
- doppelte `IDpol`: 0
- fehlende Modellprognosen: 0

Spalten:

- `IDpol`
- `tweedie_model_version`
- `predicted_pure_premium_tweedie`
- `exposure_used`
- `expected_loss_tweedie`

Der über das gesamte Portfolio aggregierte erwartete Tweedie-Schaden
beträgt ca. 59,63 Mio. EUR.

Dieser Full-Portfolio-Wert ist eine Scoring-Ausgabe und darf nicht als
Kalibrierungskennzahl interpretiert werden, da für einen Teil der Policen
kein vollständiger beobachteter tatsächlicher Schaden verfügbar ist.

## 9. Modell-Erklärbarkeit

Nach Abschluss der Modellselektion wurden die finalen Modelle
systematisch interpretiert.

Untersucht wurden:

- GLM-Koeffizienten
- Permutation Feature Importance
- Partial Dependence Plots
- ICE-Analysen

Die Explainability-Auswertungen wurden erst nach Abschluss der
Modellselektion durchgeführt.

Sie verändern die ausgewählten Modelle nicht.

Die Interpretation ist ebenfalls nicht kausal.

## 10. GLM-Koeffizienten

Alle drei finalen Modellkomponenten basieren auf Generalized Linear
Models mit Log-Link.

Die Modellkoeffizienten wurden deshalb direkt aus den gespeicherten
Pipelines extrahiert.

### 10.1 Frequency v2

Größere Koeffizienten traten insbesondere bei Spline-Komponenten von

- `VehAge`
- `BonusMalus`
- `DrivAge`

auf.

Zusätzlich zeigten einzelne Kategorien von

- `Region`
- `VehPower`

Abweichungen gegenüber ihren jeweiligen Referenzkategorien.

### 10.2 Severity v2

Die Koeffizienten waren insgesamt deutlich kleiner.

Dies passt zur bereits im vorherigen Arbeitspaket festgestellten schwachen
Risikodifferenzierung des Severity-Modells.

### 10.3 Tweedie

Beim direkten Tweedie-Modell waren insbesondere Spline-Komponenten von

- `DrivAge`
- `VehAge`
- `BonusMalus`

relevant.

Auch einzelne regionale Kategorien tragen zur Modellstruktur bei.

Die absoluten Koeffizientenwerte werden jedoch nicht direkt als
Feature Importance interpretiert.

Da numerische Merkmale über Spline-Basisfunktionen dargestellt werden,
beschreibt ein einzelner Spline-Koeffizient nicht den vollständigen
Effekt des ursprünglichen Merkmals.

## 11. Permutation Feature Importance

Zur ergänzenden globalen Interpretation wurde für die finalen Modelle eine
Permutation Importance auf der jeweils passenden Modellmetrik berechnet.

### 11.1 Frequency v2

Die stärksten globalen Einflussfaktoren waren:

1. `BonusMalus`
2. `VehAge`
3. `DrivAge`

Danach folgten unter anderem:

- `VehPower`
- `log_density`
- `Region`
- `VehBrand`
- `VehGas`

Das Ergebnis bestätigt, dass die Frequency-Komponente eine klar
strukturierte Risikodifferenzierung besitzt.

### 11.2 Severity v2

Die Permutation-Importance-Werte waren insgesamt klein und teilweise
instabil.

Dies bestätigt erneut die bereits dokumentierte begrenzte
Prognosestruktur der Severity-Komponente.

### 11.3 Tweedie

Die stärksten globalen Einflussfaktoren waren:

1. `BonusMalus`
2. `DrivAge`
3. `VehAge`

Danach folgten:

- `VehGas`
- `VehPower`
- `log_density`

Die Rohwerte der Permutation Importance werden nicht direkt zwischen den
verschiedenen Modellen verglichen, da unterschiedliche Zielgrößen und
Deviance-Skalen verwendet werden.

## 12. PDP- und ICE-Analyse

Für die wichtigsten numerischen Risikomerkmale wurden zusätzlich Partial
Dependence und ICE ausgewertet.

Untersucht wurden insbesondere:

- `BonusMalus`
- `VehAge`
- `DrivAge`

für:

- Frequency v2
- Tweedie

Die Analysen zeigen, dass die Modellbeziehungen nicht rein linear
verlaufen.

Die Verwendung von Spline-Transformationen ist deshalb fachlich
nachvollziehbar.

PDP beschreibt dabei den durchschnittlichen modellierten Effekt eines
Merkmals.

ICE zeigt ergänzend, wie sich dieser Effekt auf einzelne
Beobachtungen verteilt.

Die Ergebnisse werden ausschließlich als Modellverhalten interpretiert.

Es werden keine kausalen Aussagen abgeleitet.

## 13. Risikosegmentierung

Auf Basis der finalen Tweedie-Pure-Premium wurde eine
portfolioorientierte Risikosegmentierung entwickelt.

Die Grenzen wurden nicht als willkürliche feste Eurobeträge definiert.

Stattdessen wurden Quantile der tatsächlichen Portfolioverteilung
verwendet.

Die vier Segmente sind:

- `LOW`
- `STANDARD`
- `ELEVATED`
- `HIGH`

Verwendete Grenzen:

- 50. Perzentil: 119,35
- 75. Perzentil: 187,90
- 90. Perzentil: 328,24

Segmentdefinition:

- `LOW`: bis einschließlich 50. Perzentil
- `STANDARD`: 50.–75. Perzentil
- `ELEVATED`: 75.–90. Perzentil
- `HIGH`: oberste 10 %

Ergebnis:

- LOW: 339.008 Policen
- STANDARD: 169.508 Policen
- ELEVATED: 101.695 Policen
- HIGH: 67.802 Policen

Damit basiert die Segmentierung direkt auf der relativen
Risikoverteilung des Portfolios.

## 14. Risk Deciles

Zusätzlich zu den vier Business-Segmenten wurden zehn
nahezu gleich große Risikodezile erzeugt.

Dabei gilt:

- Decile 1 = niedrigste prognostizierte Pure Premium
- Decile 10 = höchste prognostizierte Pure Premium

Die zentralen Decile-Grenzen der Tweedie-Pure-Premium liegen bei:

- P10: 64,80
- P20: 79,66
- P30: 92,07
- P40: 104,72
- P50: 119,35
- P60: 138,35
- P70: 166,78
- P80: 217,22
- P90: 328,24

Die Decile-Information wird sowohl in den gespeicherten
Portfolioartefakten als auch im API-Scoring bereitgestellt.

## 15. Business-Handlungsempfehlungen

Die Risikosegmente wurden anschließend in eine fachliche
Decision-Support-Logik übersetzt.

### 15.1 LOW

Priorität:

`Standard`

Empfehlung:

`Standard process`

Entscheidungsregel:

`Decision support only`

### 15.2 STANDARD

Priorität:

`Moderate`

Empfehlung:

`Standard process`

Entscheidungsregel:

`Decision support only`

### 15.3 ELEVATED

Priorität:

`High`

Empfehlung:

`Additional review recommended`

Entscheidungsregel:

`Model-supported additional review`

### 15.4 HIGH

Priorität:

`Very High`

Empfehlung:

`Manual underwriting review recommended`

Entscheidungsregel:

`Manual review supported by model`

Diese Handlungsempfehlungen stellen ausdrücklich keine automatische
Annahme-, Ablehnungs- oder Preisentscheidung dar.

Das Modell liefert ausschließlich Entscheidungsunterstützung.

## 16. Portfolio-Konzentration

Zusätzlich wurde untersucht, wie stark sich der erwartete Schaden auf die
vier Risikosegmente konzentriert.

Der Konzentrationsindex steigt deutlich über die Segmente:

- LOW: 0,55
- STANDARD: 0,86
- ELEVATED: 1,26
- HIGH: 3,21

Besonders relevant ist das HIGH-Segment:

- Anteil der Policen: ca. 10 %
- Anteil am prognostizierten erwarteten Schaden: ca. 32,1 %

Damit konzentriert sich ein überproportional großer Teil des modellierten
erwarteten Schadenaufwands auf die obersten 10 % des Portfolios.

Auch hierbei handelt es sich um modellbasierte Erwartungswerte und nicht
um tatsächlich zukünftige Schäden.

## 17. Finale Decision-Support-Artefakte

Für die weitere Nutzung in Power BI und API wurden mehrere
Policy- und Management-Layer erzeugt.

### 17.1 Risk Segmentation

`data/output/risk_segments.pq`

- Zeilen: 678.013
- Spalten: 7
- doppelte `IDpol`: 0
- fehlende Risk Segments: 0
- fehlende Risk Deciles: 0
- Decile-Bereich: 1–10

### 17.2 Management KPIs

`data/output/management_kpi.pq`

Enthält aggregierte Kennzahlen für die vier Risikosegmente.

### 17.3 Policy Action Priorities

`data/output/policy_action_priorities.pq`

- Zeilen: 678.013
- eindeutige Policy-Level-Zuordnung
- Risk Segment
- Risk Decile
- Priorität
- Handlungsempfehlung
- Decision Rule

Damit steht eine direkt nutzbare Business-Schicht für das spätere
Power-BI-Dashboard zur Verfügung.

## 18. FastAPI

Die API-Schicht wurde auf die finale Modell- und Segmentierungslogik
ausgerichtet.

Implementierte Endpunkte:

### 18.1 Health

`GET /health`

liefert den technischen API- und Modellstatus.

### 18.2 Risk Score

`POST /risk-score`

liefert unter anderem:

- Tweedie Pure Premium
- Expected Loss
- Risk Segment
- Risk Decile
- Priority
- Recommended Action
- Decision Rule

### 18.3 Pure Premium

`POST /pure-premium`

liefert:

- Predicted Frequency
- Expected Claim Count
- Predicted Severity
- Two-Stage Pure Premium
- Two-Stage Expected Loss
- Tweedie Pure Premium
- Tweedie Expected Loss

### 18.4 Data Quality Summary

`GET /data-quality-summary`

liest die vorhandenen Ergebnisse aus:

`data/output/dq_check_results.jsonl`

und stellt den jeweils letzten Data-Quality-Run zusammengefasst zur
Verfügung.

Zusätzlich wurden integriert:

- Pydantic-Validierung
- Ablehnung unbekannter Request-Felder
- Wertebereichsvalidierung
- HTTP-Statuscodes
- Logging
- strukturierte Response-Schemas
- Swagger/OpenAPI-Dokumentation

## 19. API-Validierung und Tests

Für die API wurden sechs Kerntests umgesetzt.

Getestet werden:

- `/health`
- gültiger `/risk-score` Request
- gültiger `/pure-premium` Request
- `/data-quality-summary`
- ungültige Exposure
- unbekanntes Eingabefeld

Ergebnis des vollständigen Testlaufs:

`6 passed`

Die API wurde zusätzlich manuell über Swagger gestartet und geprüft.

Alle vier geplanten Endpunkte waren unter

`/docs`

sichtbar und ausführbar.

Damit sind Pydantic-Validierung, Modellinferenz, Risk-Segment-Zuordnung,
Risk-Decile-Zuordnung sowie Data-Quality-Ausgabe technisch validiert.

## 20. Technische Probleme und Erkenntnisse

### Unvollständige Tweedie-Zielvariable

Für 9.117 Policen steht kein vollständig beobachtbarer
Tweedie-Zielwert zur Verfügung.

Dadurch umfasst die Modellbewertung nicht das vollständige Portfolio.

**Konsequenz:**

Tweedie und Two-Stage wurden für den direkten Vergleich auf derselben
beobachtbaren Basis bewertet.

Full-Portfolio-Prognosen werden dagegen als Scoring-Ausgabe und nicht als
direkte Kalibrierungskennzahl interpretiert.

### Two-Stage-Deviance vs. Portfolio-Kalibrierung

Das Two-Stage-Modell besitzt auf der gemeinsamen Bewertungsbasis eine
minimal bessere Mean Tweedie Deviance.

Gleichzeitig ist die Portfolioabweichung deutlich größer als beim
direkten Tweedie-Modell.

**Konsequenz:**

Die Modellentscheidung wird nicht anhand nur einer einzelnen Kennzahl
getroffen.

Two-Stage bleibt für die fachliche Dekomposition erhalten.

Tweedie wird für das Risk Scoring und die Portfolio-Segmentierung
verwendet.

### Severity bleibt die schwächste Modellkomponente

Auch die Explainability-Analyse bestätigt die bereits im vorherigen
Arbeitspaket beobachtete geringe Risikodifferenzierung der
Severity-Komponente.

**Konsequenz:**

Diese Schwäche wird weiterhin transparent dokumentiert.

Es werden keine zusätzlichen Tuning-Schleifen gestartet.

### Interpretation von Spline-Koeffizienten

Einzelne GLM-Spline-Koeffizienten können nicht wie klassische lineare
Koeffizienten als vollständiger Effekt eines Merkmals interpretiert
werden.

**Konsequenz:**

GLM-Koeffizienten werden gemeinsam mit Permutation Importance sowie
PDP-/ICE-Analysen interpretiert.

### Pytest-Importpfad

Beim direkten Aufruf von

`pytest tests/test_api.py -v`

konnte das lokale `api`-Package unter Windows zunächst nicht aufgelöst
werden.

Der Testlauf wurde anschließend über den aktiven Projektinterpreter
gestartet:

`python -m pytest`

Damit wurden alle sechs Tests erfolgreich ausgeführt.

Die verbleibenden Warnungen stammen aus externen
Starlette/httpx- bzw. joblib/NumPy-Abhängigkeiten und beeinflussen den
Teststatus nicht.

## 21. Methodische Einschränkungen

Auch nach Abschluss dieses Arbeitspakets werden die Grenzen des Systems
bewusst dokumentiert.

- Der direkte Tweedie-Holdout umfasst wegen fehlender Schadenhöhen nicht
  das vollständige Portfolio.
- Full-Portfolio-Tweedie-Prognosen können deshalb nicht direkt gegen einen
  vollständig beobachteten Gesamtschaden kalibriert werden.
- Die Mean Tweedie Deviance unterscheidet sich zwischen Tweedie und
  Two-Stage nur geringfügig.
- Die Severity-Komponente besitzt weiterhin eine sehr geringe
  Ranking-Fähigkeit.
- Modellkoeffizienten und Feature-Importance-Werte sind keine kausalen
  Effekte.
- Die Risk Segments basieren auf der aktuellen Portfolioverteilung und
  nicht auf regulatorisch oder tariflich vorgegebenen Grenzwerten.
- Die Risikosegmentierung beschreibt relative Modellrisiken innerhalb
  dieses Portfolios.
- `HIGH` bedeutet nicht automatische Ablehnung.
- Die berechnete Pure Premium ist keine Endkundenprämie und kein Tarif.
- Die Modelle prognostizieren kein zukünftiges Kalenderjahr.
- Die Ergebnisse stellen statistische annualisierte Erwartungswerte dar.
- Das System ist ein Decision-Support-Prototyp und kein autonomes
  Underwriting-System.

## 22. Finale Entscheidung des Arbeitspakets

Nach Abschluss des Challenger-Vergleichs werden folgende Komponenten
weiterverwendet.

### 22.1 Two-Stage-Modell

Frequency:

`frequency_poisson_quantile_spline_full_v2`

Severity:

`severity_gamma_spline_scaled_full_v2`

Verwendung:

- fachliche Frequency-/Severity-Dekomposition
- Expected Claim Count
- erwartete monetäre Schadenhöhe
- Vergleichsmodell zum direkten Tweedie-Ansatz

### 22.2 Direkter Tweedie-Challenger

`tweedie_direct_pure_premium_full_v1`

Verwendung:

- direkter Pure-Premium-Risikoscore
- Portfolio-Ranking
- Risk Segmentation
- Risk Deciles
- Business Decision Support

Damit werden die Stärken beider Modellansätze genutzt, anstatt einen
Ansatz ausschließlich anhand einer einzelnen Metrik zu verwerfen.

## 23. Abgeschlossene Arbeiten

- `notebooks/07_tweedie_model.ipynb` entwickelt
- Tweedie-Ziel fachlich definiert
- Exposure als `sample_weight` verwendet
- bestehenden kanonischen Policy-Level-Split weiterverwendet
- neuen Split bewusst vermieden
- Tweedie-Modellwahl ausschließlich auf Trainingsdaten durchgeführt
- Power- und Regularisierungsspezifikationen verglichen
- finale Tweedie-Spezifikation vor Holdout-Bewertung festgelegt
- konstante Tweedie-Baseline berechnet
- Mean Tweedie Deviance berechnet
- Portfolio-Kalibrierung geprüft
- Exposure-korrekten erwarteten Schaden berechnet
- Two-Stage und Tweedie auf gemeinsamer Holdout-Basis verglichen
- Lorenz- und Gini-Analysen durchgeführt
- direkten Tweedie-Challenger finalisiert
- Holdout- und Full-Data-Tweedie-Artefakte gespeichert
- `tweedie_predictions.pq` erzeugt und validiert
- `notebooks/08_model_explainability.ipynb` finalisiert
- GLM-Koeffizienten für Frequency, Severity und Tweedie extrahiert
- Permutation Feature Importance berechnet
- PDP- und ICE-Analysen durchgeführt
- Explainability-Ergebnisse fachlich und nicht-kausal dokumentiert
- `notebooks/09_risk_segmentation.ipynb` finalisiert
- LOW-, STANDARD-, ELEVATED- und HIGH-Segmente aus der
  Portfolioverteilung definiert
- zehn Risk Deciles erzeugt
- Quantilgrenzen dokumentiert
- `risk_segments.pq` erzeugt und validiert
- `notebooks/10_business_recommendations.ipynb` finalisiert
- fachliche Action Matrix erstellt
- Management KPIs erzeugt
- erwartete Loss-Konzentration nach Segment analysiert
- `management_kpi.pq` erzeugt
- `policy_action_priorities.pq` erzeugt
- FastAPI-Schemas an die finalen Segmentnamen angepasst
- Risk-Decile-Logik in die API integriert
- Business-Actions in das API-Scoring integriert
- `/health` implementiert
- `/risk-score` implementiert
- `/pure-premium` implementiert
- `/data-quality-summary` implementiert
- Pydantic-Validierung umgesetzt
- HTTP-Statuscodes umgesetzt
- Logging integriert
- Swagger/OpenAPI geprüft
- sechs API-Kerntests umgesetzt
- vollständigen Regression-Test durchgeführt
- alle sechs Tests erfolgreich abgeschlossen
- finale Änderungen versioniert und nach GitHub übertragen
- Git Working Tree nach Abschluss sauber validiert

## 24. Nächste Schritte

Der Challenger-, Explainability-, Segmentierungs- und API-Teil wird ab
diesem Punkt nicht weiter erweitert.

LightGBM wird nicht zusätzlich untersucht.

Es handelt sich im Projektfahrplan ausdrücklich um eine optionale
Erweiterung und für die weitere Projektqualität besteht aktuell kein
fachlicher Bedarf für eine zusätzliche Modellfamilie.

Im nächsten technischen Arbeitspaket liegt der Fokus auf Power BI und
Dokumentation.

Geplante nächste Schritte:

- Power-BI-Seite `Portfolio Overview` aufbauen
- Power-BI-Seite `Risk Segmentation` aufbauen
- Power-BI-Seite `Expected Loss & Pure Premium` aufbauen
- nach Möglichkeit vierte Seite
  `Data Quality & Model Validation` ergänzen
- zentrale Filter und Management-KPIs integrieren
- Observed- und Predicted-Kennzahlen korrekt gegenüberstellen
- Risk Deciles und Risk Segments visualisieren
- README finalisieren
- Model Card erstellen
- Data Dictionary finalisieren
- Architekturdiagramm einbinden
- Data-Quality-Dokumentation final prüfen
- Kerntests und technische Ausführung dokumentieren
- Abschnitt `Subgroup Performance & Responsible Use` erstellen

## 25. Zusammenfassung

Das sechste technische Arbeitspaket wurde erfolgreich abgeschlossen.

Mit dem direkten Tweedie-Modell wurde ein vollständiger Challenger zum
bestehenden Poisson-Gamma-Two-Stage-Ansatz entwickelt.

Der direkte Tweedie-Challenger erreicht auf der gemeinsamen beobachtbaren
Holdout-Basis eine Mean Tweedie Deviance von 34,364453 und verbessert
damit die konstante Baseline.

Während das Two-Stage-Modell eine geringfügig bessere Tweedie-Deviance
erzielt, zeigt der direkte Tweedie-Challenger mit einer
Portfolioabweichung von +6,40 % gegenüber +36,29 % eine deutlich bessere
Portfolio-Kalibrierung.

Auch die Ranking-Leistung ist mit einem Gini von 0,2677 höher als beim
Two-Stage-Pure-Premium-Modell.

Daraus wurde bewusst keine Winner-takes-all-Entscheidung abgeleitet.

Das Two-Stage-Modell bleibt wegen seiner fachlich wertvollen
Frequency-/Severity-Dekomposition erhalten.

Tweedie wird dagegen als direkter Risk Score für Portfolio-Ranking und
Risikosegmentierung verwendet.

Die finalen Modelle wurden anschließend über GLM-Koeffizienten,
Permutation Importance sowie PDP- und ICE-Analysen interpretiert.

Auf Basis der Tweedie-Pure-Premium wurden vier
portfolioabhängige Risikosegmente und zehn Risk Deciles erstellt.

Das HIGH-Segment umfasst ungefähr 10 % der Policen und konzentriert rund
32,1 % des modellierten erwarteten Schadenaufwands.

Die Risk Segments wurden anschließend in eine explizite
Decision-Support-Logik mit Standardprozess, zusätzlicher Prüfung und
manueller Underwriting-Prüfung überführt.

Zum Abschluss wurde die FastAPI-Schicht auf vier klar getrennte
Endpunkte erweitert.

Pydantic-Validierung, HTTP-Statuscodes, Logging und Swagger wurden
integriert.

Alle sechs implementierten API-Tests wurden erfolgreich abgeschlossen.

Damit stehen nun neben den finalen Hauptmodellen auch ein validierter
direkter Challenger, eine Explainability-Schicht, eine vollständige
Risk-Segmentation, Policy-Level-Handlungsempfehlungen sowie eine
funktionsfähige API als technische Grundlage für das folgende
Power-BI- und Dokumentationspaket zur Verfügung.
