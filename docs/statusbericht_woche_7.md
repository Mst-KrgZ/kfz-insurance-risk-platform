
# Statusbericht – Woche 7

**Projekt:** Kfz Insurance Risk & Pure Premium Intelligence Platform
**Berichtszeitraum:** Technisches Arbeitspaket Woche 7, vorgezogen bearbeitet vom 01.09.2026 bis 07.09.2026
**Stand:** 07.09.2026
**Gesamtarbeitszeit:** Wird nach Abschluss der Zeiterfassung ergänzt

## 1. Aktueller Projektstand

Im siebten technischen Arbeitspaket lag der Schwerpunkt auf der Überführung der finalen Modell- und Datenqualitätslogik in eine managementorientierte Power-BI-Lösung sowie auf der abschließenden fachlichen und technischen Projektdokumentation.

Ausgangspunkt waren die im vorherigen Arbeitspaket finalisierten Modellrollen:

- Frequency:
  `frequency_poisson_quantile_spline_full_v2`
- Severity:
  `severity_gamma_spline_scaled_full_v2`
- Two-Stage Pure Premium:
  `Predicted Frequency × Predicted Severity`
- Direct Tweedie:
  `tweedie_direct_pure_premium_full_v1`

Die Modellrollen wurden unverändert beibehalten:

- Frequency für Schadenhäufigkeit und Portfolio-Kalibrierung
- Severity als monetäre Schadenhöhenkomponente
- Two-Stage für fachliche Frequency-/Severity-Dekomposition
- Tweedie als direkter Pure-Premium-Risikoscore für Ranking und Segmentierung

Es wurde kein neues Modell trainiert und kein neuer Train-/Test-Split erzeugt.

Im Power-BI-Teil wurden zunächst Datenquellen, Datenmodell und KPI-Logik geprüft und anschließend vier analytische Dashboard-Seiten aufgebaut.

Ergänzend wurde eine systematische Subgruppen-Diagnostik für Frequency, Severity und Tweedie durchgeführt.

Zum Abschluss wurden README, Model Card, Data Dictionary, Data Quality Report und eine eigene Architecture-Dokumentation auf den finalen Projektstand gebracht und anschließend projektweit auf Konsistenz geprüft.

Damit sind die analytischen Inhalte des Power-BI-Dashboards, die Subgruppen-Diagnostik sowie die zentrale technische und fachliche Dokumentation abgeschlossen.

## 2. Power-BI-Datenquellen

Vor dem Aufbau der finalen Dashboard-Seiten wurden die vorhandenen Datenquellen erneut geprüft.

Die finale Power-BI-Lösung verwendet folgende Hauptquellen:

### Policy- und Modellanalyse

PostgreSQL:

`vw_model_prediction_analysis`

Diese View stellt den jeweils aktuellsten Prediction-Run auf Policy-Level bereit und enthält unter anderem:

- Policy-Merkmale
- Exposure
- beobachtete Schadenkennzahlen
- Data-Quality-Flags
- Frequency-Predictions
- Severity-Predictions
- Two-Stage Pure Premium
- Expected Claim Count
- Expected Claim Amount

### Risk Segmentation und Decision Support

Parquet:

`data/output/policy_action_priorities.pq`

Enthalten sind unter anderem:

- Tweedie Pure Premium
- Expected Loss
- Risk Segment
- Risk Decile
- Priority
- Recommended Action
- Decision Rule

### Data Quality

PostgreSQL:

`vw_dq_summary`

Die View liefert je Data-Quality-Check und Dataset den jeweils aktuellsten dokumentierten Prüfstatus.

### Pipeline-Monitoring

PostgreSQL:

`pipeline_runs`

Damit werden Pipeline-Status, Laufzeitpunkt und verwendete Datenquelle im Dashboard sichtbar gemacht.

Die ursprünglich vorhandene Management-KPI-Parquet-Datei wird nicht als zentrale KPI-Quelle verwendet.

Die finalen Management-Kennzahlen werden überwiegend direkt aus Policy-Level-Daten über DAX berechnet.

## 3. Power-BI-Datenmodell

Im finalen Power-BI-Modell stehen folgende analytische Tabellen zur Verfügung:

- `Policy`
- `RiskActions`
- `DataQuality`
- `ModelValidation`
- `PipelineRuns`
- `_Measures`

Zwischen:

`Policy[idpol]`

und:

`RiskActions[idpol]`

besteht eine aktive One-to-One-Beziehung.

Beide Tabellen besitzen eine eindeutige Policy-Grain.

Damit können:

- beobachtete Portfolioinformationen,
- Two-Stage-Predictions,
- Tweedie-Risikowerte,
- Risikosegmente,
- und Business Actions

gemeinsam analysiert werden.

Die Measures werden zentral in `_Measures` verwaltet.

## 4. KPI- und Exposure-Logik

Die zentrale fachliche Regel der Plattform wurde auch in Power BI konsequent beibehalten:

Annualisierte Raten werden nicht direkt als absolute Beträge aufsummiert.

Es gilt:

`Expected Claims = Predicted Frequency × Exposure`

und:

`Expected Loss = Predicted Pure Premium × Exposure`

Die Portfolio-Frequency wird deshalb als:

`SUM(Expected Claims) / SUM(Exposure)`

berechnet.

Analog wird die Portfolio-Pure-Premium aus:

`SUM(Expected Loss) / SUM(Exposure)`

abgeleitet.

Auch die beobachtete Severity wird nicht als einfacher Durchschnitt einzelner Policy-Werte berechnet, sondern claim-gewichtet auf der dafür zulässigen beobachtbaren Population.

Zusätzlich wird die Severity Coverage transparent ausgewiesen.

## 5. Power BI – Portfolio Overview

Die erste Dashboard-Seite bildet die grundlegende Struktur und beobachtete Performance des Portfolios ab.

Zentrale KPI:

- Policy Count: 678.013
- Total Exposure: ca. 358.360
- Observed Claims: 36.102
- Observed Frequency: ca. 0,101
- Observed Claim Amount: ca. 59,91 Mio. EUR
- Observed Severity: ca. 2.265 EUR
- Observed Pure Premium: ca. 169 EUR
- Severity Coverage: ca. 73,25 %

Zusätzlich wurden unter anderem folgende Analysen umgesetzt:

- Observed Frequency nach Fahrer-Altersgruppe
- Observed Frequency nach Fahrzeug-Altersgruppe
- Observed Frequency nach Bonus-Malus-Segment
- Exposure nach Region
- Claim-Free vs. With-Claim-Struktur

Die Claim-Status-Analyse zeigt:

- ca. 94,98 % Claim-Free
- ca. 5,02 % With Claim

Damit wird die starke Zero-Claim-Struktur des Portfolios auch im Management-Dashboard sichtbar.

## 6. Power BI – Risk Segmentation

Die zweite Dashboard-Seite fokussiert die modellierte Risikokonzentration.

Die finale Risikosegmentierung basiert auf:

`predicted_pure_premium_tweedie`

Verwendete Segmente:

- LOW
- STANDARD
- ELEVATED
- HIGH

Portfolioverteilung:

- LOW: 50 %
- STANDARD: 25 %
- ELEVATED: 15 %
- HIGH: 10 %

Das HIGH-Segment umfasst:

- 67.802 Policen
- ca. 10 % des Portfolios
- ca. 32,1 % des modellierten Tweedie Expected Loss

Damit zeigt sich eine deutliche Risikokonzentration im oberen Portfoliobereich.

Zusätzlich wurden umgesetzt:

- Policy Share vs. Expected Loss Share nach Segment
- Risk Segment Distribution
- Tweedie Pure Premium nach Risk Decile
- Risk Heatmap:
  Fahrer-Altersgruppe × Bonus-Malus-Segment

Die Heatmap zeigt die durchschnittliche Tweedie Pure Premium innerhalb kombinierter Fahrer- und Bonus-Malus-Risikoprofile.

## 7. Power BI – Expected Loss & Pure Premium

Die dritte Dashboard-Seite stellt die monetären Modelloutputs gegenüber.

Zentrale KPI:

- Predicted Claim Count: ca. 36.096
- Predicted Portfolio Frequency: ca. 0,101
- Two-Stage Expected Loss: ca. 77,03 Mio. EUR
- Two-Stage Portfolio Pure Premium: ca. 214,94 EUR
- Tweedie Expected Loss: ca. 59,63 Mio. EUR
- Tweedie Portfolio Pure Premium: ca. 166,40 EUR

Zusätzlich wurden folgende Analysen umgesetzt:

- Tweedie Expected Loss nach Risk Decile
- Two-Stage vs. Tweedie Pure Premium nach Risk Segment
- Top Risk Profiles nach gesamtem Expected Loss
- Expected Loss nach Risk Segment
- kumulierter Expected-Loss-Anteil nach Risk Decile
- Frequency-Severity-Dekomposition nach Risk Segment

Die Profilanalyse zeigt, dass ein hoher Gesamt-Expected-Loss nicht ausschließlich durch hohe Risikointensität entsteht.

Ein großes Profil kann auch aufgrund hoher Portfolio-Exposure beziehungsweise hoher Policy-Anzahl einen großen Anteil am gesamten erwarteten Schaden tragen.

Daher wird unterschieden zwischen:

- individueller Risikointensität
- und Portfolio-Konzentration.

## 8. Power BI – Data Quality & Model Validation

Die vierte analytische Seite verbindet Data Quality, Modellvalidierung und Pipeline-Monitoring.

### Data Quality

Der aktuell dargestellte DQ-Lauf enthält:

- 9 Checks
- 4 PASS
- 2 WARN
- 3 FAIL

Wichtige Befunde:

- 1.224 Exposure-Auffälligkeiten
- 9 auffällig hohe Schadenanzahlen
- 255 potenziell doppelte Severity-Records
- 9.117 Frequency-/Severity-Konsistenzbefunde
- 195 Orphan-Severity-Records

Die DQ-Status werden ausdrücklich als Befunde der Quelldatenprüfung interpretiert.

Ein `FAIL` bedeutet nicht automatisch, dass der finale Curated-Datensatz technisch unbrauchbar ist.

Die fachliche Behandlung der jeweiligen Befunde erfolgt in Curated- und Modeling-Layer.

### Model Validation

Für die drei zentralen Modellkomponenten wurden die finalen Holdout-Metriken gegenübergestellt.

Frequency:

- Baseline Deviance: 0,625748
- Model Deviance: 0,592685
- Portfolio-Abweichung: −0,25 %
- Gini: 0,2903

Severity:

- Baseline Deviance: 1,543630
- Model Deviance: 1,567498
- Portfolio-Abweichung: +3,99 %
- Gini: 0,0033

Tweedie:

- Baseline Deviance: 34,602470
- Model Deviance: 34,364453
- Portfolio-Abweichung: +6,40 %
- Gini: 0,2677

Die absoluten Deviance-Werte werden nicht direkt zwischen den Modellen verglichen, da unterschiedliche Zielgrößen und Evaluationspopulationen verwendet werden.

Es wird weiterhin keine Winner-takes-all-Interpretation vorgenommen.

### Pipeline Monitoring

Der letzte dokumentierte Datenpipeline-Lauf besitzt den Status:

`PASS`

Die im Dashboard dargestellte Pipeline-Information bezieht sich auf die Datenpipeline und nicht auf einen Modell-Scoring-Run.

## 9. Subgruppen-Performance

Nach Abschluss der globalen Modellbewertung wurde eine zusätzliche Holdout-Diagnostik auf Subgruppenebene durchgeführt.

Neues Notebook:

`notebooks/11_subgroup_performance.ipynb`

Untersucht wurden:

- Fahrer-Altersgruppe
- Region
- Area
- quantilbasierte Density-Gruppen

Die Analyse wurde für drei Modellperspektiven durchgeführt:

- Frequency
- Severity
- Tweedie Pure Premium

Die Modelle wurden dabei nicht neu trainiert oder angepasst.

Es erfolgte kein nachträgliches Hyperparameter-Tuning.

## 10. Frequency-Subgruppen

Die Frequency-Diagnostik verwendet den vollständigen canonical Holdout:

**135.603 Policen**

Das Frequency-Modell zeigt insgesamt die stabilste Subgruppen-Kalibrierung.

### Fahrer-Alter

Die meisten Altersgruppen zeigen nur moderate Abweichungen.

Die auffälligste Gruppe ist:

`75+`

mit einer Unterschätzung der beobachteten Frequency von rund:

**−11,6 %**

Die übrigen großen Altersgruppen liegen deutlich näher am beobachteten Niveau.

### Region

Die regionale Kalibrierung ist heterogener.

Sehr hohe relative Abweichungen kleiner Regionen werden nicht überinterpretiert.

In größeren Regionen liegt die Modellkalibrierung teilweise sehr nahe an den beobachteten Werten.

### Area

Die Frequency-Kalibrierung ist über die Area-Gruppen insgesamt stabil.

Die größte Abweichung zeigt sich in:

`Area F`

mit rund:

**+7,1 %**

Area F besitzt gleichzeitig die kleinste Policy-Anzahl.

### Density

Density wurde auf dem Holdout in fünf quantilbasierte Gruppen aufgeteilt.

Die Gruppen besitzen jeweils ungefähr dieselbe Policy-Anzahl.

Die deutlichste Abweichung zeigt:

`Q4 – High`

mit rund:

**−5,4 %**

Insgesamt bestätigt die Subgruppenanalyse eine vergleichsweise stabile Frequency-Komponente.

## 11. Severity-Subgruppen

Die Severity-Evaluation verwendet ausschließlich die dafür zulässige beobachtbare positive Holdout-Population.

Finale Severity-Population:

- 4.999 Policen
- 5.312 Claims
- 11.055.690,67 EUR beobachteter Schaden
- beobachtete claim-gewichtete Severity: 2.081,27 EUR

Die Subgruppen-Performance ist deutlich heterogener als bei Frequency.

### Fahrer-Alter

Beispielhafte relative Abweichungen:

- 18–24: ca. +74 %
- 55–64: ca. +32 %
- 75+: ca. −45 %

Die Ergebnisse werden wegen der heavy-tailed Schadenhöhen vorsichtig interpretiert.

### Region

Regionale Severity-Ergebnisse zeigen teilweise starke Unterschiede.

Kleine Regionen mit sehr wenigen Claims werden nicht isoliert bewertet.

Auch in mehreren größeren Regionen treten jedoch relevante Über- beziehungsweise Unterschätzungen auf.

### Area

Beispielhafte Abweichungen:

- Area A: ca. −23 %
- Area B: ca. +42 %
- Area F: ca. +66 %

### Density

Die quantilbasierten Density-Gruppen zeigen moderate bis relevante Unterschiede.

Beispielsweise:

- Q1 – Very Low: ca. −12,8 %
- Q2 – Low: ca. +19,5 %
- Q4 – High: ca. −3,2 %

Die Subgruppenanalyse bestätigt damit die bereits bekannte Einschränkung des Severity-Modells.

Severity bleibt primär eine monetäre Dekompositionskomponente und kein starker eigenständiger Ranking-Score.

## 12. Tweedie-Pure-Premium-Subgruppen

Für die Loss-/Tweedie-Diagnostik wurde der common observable Holdout verwendet.

Population:

**133.790 Policen**

Davon:

- 128.791 schadenfreie Policen
- 4.999 Policen mit beobachtbarer positiver Schadenhöhe

### Fahrer-Alter

Die Tweedie-Kalibrierung unterscheidet sich sichtbar nach Altersgruppe.

Beispiele:

- 25–34: ca. +4,1 %
- 35–44: ca. −1,3 %
- 18–24: ca. +114 %
- 75+: ca. −47,5 %

### Region

Einige große Regionen zeigen eine vergleichsweise gute Kalibrierung.

Andere größere Regionen weisen dagegen relevante Über- oder Unterschätzungen auf.

Sehr extreme Werte kleiner Regionen werden wegen geringer Schadenanzahl und Heavy-Tail-Effekten nicht überinterpretiert.

### Area

Beispiele:

- Area D: ca. +3,1 %
- Area C: ca. +9,5 %
- Area A: ca. −20 %
- Area B: ca. +50 %
- Area F: ca. +73 %

### Density

Die Density-Gruppen zeigen ebenfalls keine vollständig homogene Kalibrierung.

Beispiele:

- Q1 – Very Low: ca. −10,4 %
- Q2 – Low: ca. +19,3 %
- Q3 – Medium: ca. +17,3 %
- Q4 – High: ca. −4,0 %
- Q5 – Very High: ca. +17,0 %

Damit bestätigt sich:

Eine gute Performance auf Gesamtportfolio-Ebene garantiert keine gleichmäßige Performance in jeder Teilpopulation.

## 13. Responsible Use

Die Subgruppenanalyse wurde ausdrücklich mit Responsible-Use-Regeln verbunden.

Zentrale Regeln:

- HIGH Risk bedeutet keine automatische Ablehnung.
- Pure Premium ist keine Kundenprämie.
- Modelloutputs dienen der Entscheidungsunterstützung.
- Kleine Subgruppen werden nicht überinterpretiert.
- Heavy-tailed Severity erhöht die Unsicherheit.
- Fahrer-, Regional- und andere Segmentmerkmale müssen bei produktiver Nutzung zusätzlich fachlich und regulatorisch geprüft werden.
- Die Subgruppenanalyse erhöht Transparenz, stellt jedoch keinen vollständigen Fairness- oder Nichtdiskriminierungsnachweis dar.

Die Holdout-Diagnostik wurde ausschließlich zur finalen Bewertung genutzt.

Sie führte zu:

- keiner erneuten Modellauswahl,
- keinem Hyperparameter-Tuning,
- keinem neuen Train-/Test-Split.

## 14. README

Im Projekt-Root wurde erstmals ein vollständiges:

`README.md`

erstellt.

Dokumentiert werden unter anderem:

- Business Problem
- zentrale Fragestellung
- Scope und Responsible Use
- Architektur und Data Flow
- Datenbasis
- Data Quality
- finale Modelle
- Modellmetriken
- Risikosegmentierung
- Decision Support
- PostgreSQL
- FastAPI
- Power BI
- zentrale Projektergebnisse
- Subgruppen-Performance
- Setup und Reproduzierbarkeit
- Repository-Struktur
- Limitationen

Damit besitzt das Repository eine zentrale Einstiegs- und Übersichtsseite.

## 15. Model Card

Neu erstellt:

`docs/model_card.md`

Die Model Card dokumentiert:

- Intended Use
- nicht vorgesehene Nutzung
- Datenbasis
- canonical Split
- Holdout-Historie
- unterschiedliche Evaluationspopulationen
- Frequency-Modell
- Severity-Modell
- Two-Stage
- Tweedie
- finale Modellrollen
- Risikosegmentierung
- Subgruppen-Performance
- Responsible Use
- verbotene Interpretationen
- Monitoring-Anforderungen
- bekannte Limitationen

Insbesondere wird transparent dokumentiert, dass der Holdout im Projektverlauf bereits für frühere Diagnose- und Vergleichsschritte betrachtet wurde und deshalb nicht als vollständig unberührter Blind-Test dargestellt wird.

## 16. Data Dictionary

Das bestehende:

`docs/data_dictionary.md`

wurde auf den finalen Projektstand erweitert.

Zusätzlich dokumentiert werden nun:

- Curated Policy-Level Dataset
- DQ-Flags
- engineered Features
- canonical Train-/Test-Split
- finale Model Predictions
- Tweedie Predictions
- Risk Segmentation
- Decision-Support-Outputs
- fachliche Abgrenzung von Pure Premium, Expected Loss und Risk Segment

Damit beschreibt das Data Dictionary nicht mehr nur die beiden Raw-Datensätze, sondern auch zentrale abgeleitete Felder der finalen Analytics-Plattform.

## 17. Data Quality Report

Das bestehende:

`docs/data_quality_report.md`

wurde um den finalen Modellierungs- und Evaluationsstatus ergänzt.

Neu dokumentiert werden unter anderem:

- finale Frequency-Holdout-Population
- finale Severity-Holdout-Population
- common observable Tweedie-Holdout-Population
- Bedeutung der DQ-Status in Power BI
- Rolle der DQ-Schicht für die finale Modellierungslogik
- explizite Trennung von:
  - kein Schaden
  - beobachtbare Schadenhöhe
  - unbekannte Schadenhöhe

Die bereits dokumentierten ursprünglichen DQ-Befunde bleiben als historische und fachliche Grundlage erhalten.

## 18. Architecture-Dokumentation

Neu erstellt:

`docs/architecture.md`

Das Dokument beschreibt die technische End-to-End-Architektur:

`OpenML → Ingestion → Data Quality → Curated Layer → Features → Modelling → Predictions → PostgreSQL / FastAPI / Power BI`

Dokumentiert werden unter anderem:

- Ingestion Layer
- Data-Quality-Layer
- Curated Layer
- Feature Engineering
- canonical Split
- Modeling & Validation
- Prediction Layer
- PostgreSQL Staging
- Analytical Fact Tables
- Pipeline- und DQ-Metadaten
- Prediction Tables
- Analytical Views
- Power-BI-Datenquellen
- Power-BI-Datenmodell
- FastAPI
- Exposure-basierte Architekturregeln
- Observability
- Responsible Architecture
- bekannte Architekturgrenzen

Dabei wurden die tatsächlichen SQL-Definitionen aus:

- `sql/create_tables.sql`
- `sql/views.sql`

gegen die Dokumentation geprüft.

## 19. Cross-Project Consistency Check

Nach Abschluss der Dokumentation wurde ein projektweiter Konsistenzcheck durchgeführt.

Geprüft wurden insbesondere:

- finale Modellmetriken
- Portfolio-Abweichungen
- Gini-Werte
- Segmentnamen
- Risk-Segment-Logik
- Responsible-Use-Formulierungen
- frühere beziehungsweise deprecated Modellwerte

Finale zentrale Werte sind konsistent dokumentiert:

### Frequency

- Model Deviance: 0,592685
- Gini: 0,2903
- Portfolio-Abweichung: −0,25 %

### Severity

- Model Deviance: 1,567498
- Gini: 0,0033
- Portfolio-Abweichung: +3,99 %

### Tweedie

- Model Deviance: 34,364453
- Gini: 0,2677
- Portfolio-Abweichung: +6,40 %

### Risk Segmentation

Finale Segmente:

- LOW
- STANDARD
- ELEVATED
- HIGH

`Very High` wird ausschließlich als operative Priority verwendet und nicht als Risk Segment.

Historische Zwischenergebnisse in älteren Statusberichten wurden bewusst nicht rückwirkend verändert.

Beispielsweise bleiben frühere Severity-v1- und selection-biased Pure-Premium-Ergebnisse als nachvollziehbare Entwicklungsschritte dokumentiert, werden jedoch nicht als finale Headline-Metriken verwendet.

## 20. Technische und methodische Erkenntnisse

### Globale Performance reicht nicht aus

Die Subgruppen-Diagnostik zeigt, dass eine gute Gesamtportfolio-Kalibrierung nicht automatisch eine gleichmäßige Performance in allen Gruppen garantiert.

**Konsequenz:**

Subgruppen-Performance wird als Bestandteil einer verantwortungsvollen Modellbewertung dokumentiert.

### Frequency ist die stabilste Modellkomponente

Frequency zeigt sowohl global als auch auf Subgruppenebene die stabilste Kalibrierung.

**Konsequenz:**

Frequency bleibt die zentrale Komponente zur Analyse erwarteter Schadenhäufigkeit.

### Severity bleibt limitiert

Severity zeigt auch auf Subgruppenebene deutlich größere Schwankungen.

**Konsequenz:**

Die bekannte Limitation wird bestätigt und nicht durch zusätzliche Tuning-Schleifen verdeckt.

Severity bleibt primär Bestandteil der Two-Stage-Dekomposition.

### Tweedie bleibt für Ranking nützlich

Tweedie zeigt trotz einzelner Subgruppen-Abweichungen eine sinnvolle globale Ranking-Fähigkeit und bleibt der kanonische Score für Segmentierung und Portfolio-Ranking.

**Konsequenz:**

Der Score wird für Decision Support genutzt, aber nicht als automatischer Entscheidungsmechanismus.

### Data Quality muss im Reporting erklärt werden

PASS/WARN/FAIL-Werte können ohne Kontext falsch interpretiert werden.

**Konsequenz:**

Im Dashboard und in der Dokumentation wird klargestellt, dass die DQ-Status Befunde der Quelldatenprüfung darstellen und nicht automatisch den Zustand des finalen Curated-Datensatzes beschreiben.

## 21. Abgeschlossene Arbeiten

- Power-BI-Datenquellen geprüft
- Policy- und RiskActions-Grain validiert
- One-to-One-Beziehung im Power-BI-Modell aufgebaut
- zentrale DAX-Measures erstellt
- Exposure-basierte KPI-Logik validiert
- Portfolio-Overview-Seite analytisch aufgebaut
- Risk-Segmentation-Seite analytisch aufgebaut
- Expected-Loss-&-Pure-Premium-Seite analytisch aufgebaut
- Data-Quality-&-Model-Validation-Seite analytisch aufgebaut
- Risk-Heatmap erstellt
- Risk-Decile-Analysen integriert
- Two-Stage und Tweedie im Dashboard gegenübergestellt
- Data-Quality-Status integriert
- Pipeline-Status in Power BI integriert
- Modellmetriken in Power BI dokumentiert
- `notebooks/11_subgroup_performance.ipynb` erstellt
- Frequency-Subgruppen nach Alter, Region, Area und Density untersucht
- Severity-Subgruppen nach Alter, Region, Area und Density untersucht
- Tweedie-Pure-Premium-Subgruppen nach Alter, Region, Area und Density untersucht
- unterschiedliche Evaluationspopulationen erneut validiert
- Responsible-Use-Regeln dokumentiert
- README erstellt
- Model Card erstellt
- Data Dictionary final erweitert
- Data Quality Report final erweitert
- Architecture-Dokumentation erstellt
- PostgreSQL-Tabellen- und View-Struktur gegen die Dokumentation geprüft
- projektweiten Consistency Check durchgeführt
- finale Modellmetriken konsistent geprüft
- historische Zwischenergebnisse bewusst unverändert erhalten

## 22. Nächste Schritte

Die analytische und dokumentarische Kernarbeit von Woche 7 ist abgeschlossen.

Als nächste Schritte folgen:

- finaler visueller Power-BI-Polish
- einheitliche Farben, Typografie und Abstände im Dashboard
- Navigation und Seitentitel final abstimmen
- finale Dashboard-Interaktionen prüfen
- Repository final versionieren
- GitHub-Stand aktualisieren
- Präsentation für die Abschlussvorstellung vorbereiten
- zentrale Projektaussagen für eine 20–30-minütige Präsentation verdichten
- vollständigen Projekt-Recap zur fachlichen Wiederholung durchführen

Die Modelle selbst werden nicht weiter getunt oder um zusätzliche Modellfamilien erweitert.

## 23. Zusammenfassung

Das siebte technische Arbeitspaket wurde inhaltlich erfolgreich abgeschlossen.

Die finalen Modelloutputs wurden in eine strukturierte Power-BI-Lösung überführt und über vier analytische Dashboard-Seiten für Portfolio-, Risiko-, Pure-Premium-, Datenqualitäts- und Modellanalysen nutzbar gemacht.

Die KPI-Logik wurde konsequent exposure-basiert umgesetzt.

Dadurch werden annualisierte Modellraten nicht fälschlich als absolute Portfolio-Beträge aggregiert.

Zusätzlich wurde mit `11_subgroup_performance.ipynb` eine systematische finale Holdout-Diagnostik umgesetzt.

Die Analyse zeigt, dass das Frequency-Modell über die untersuchten Gruppen die stabilste Kalibrierung besitzt.

Severity zeigt dagegen deutlich größere Schwankungen und bestätigt damit die bereits bekannte begrenzte eigenständige Ranking-Fähigkeit.

Das direkte Tweedie-Modell bleibt trotz heterogener Subgruppen-Kalibrierung aufgrund seiner globalen Ranking-Leistung und seiner Rolle als direkter Pure-Premium-Score die Grundlage für Risk Deciles und Risikosegmentierung.

Die Modelloutputs wurden zusätzlich mit klaren Responsible-Use-Regeln verbunden.

HIGH Risk bedeutet keine automatische Ablehnung.

Pure Premium ist keine Endkundenprämie.

Subgruppenanalysen dienen der Transparenz und Diagnostik, stellen jedoch keinen vollständigen Fairness-Nachweis dar.

Parallel wurde die Projektdokumentation umfassend finalisiert.

README, Model Card, Data Dictionary, Data Quality Report und Architecture-Dokumentation bilden nun gemeinsam eine nachvollziehbare Dokumentationsschicht für Business Problem, Datenqualität, Modellierung, technische Architektur, Modellgrenzen und Responsible Use.

Ein abschließender Cross-Project Consistency Check bestätigte, dass die finalen Modellmetriken, Segmentnamen und Modellrollen in den zentralen Dokumenten konsistent verwendet werden.

Damit ist die fachlich-analytische Basis des Projekts abgeschlossen.

Die verbleibenden Arbeiten konzentrieren sich auf den visuellen Abschluss des Power-BI-Dashboards, die finale Versionierung des Repositories und die Vorbereitung der Abschlusspräsentation.
