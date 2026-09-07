# Data Dictionary

## 1. Purpose

Dieses Data Dictionary beschreibt die in diesem Projekt verwendeten Variablen aus den OpenML-Datensätzen `freMTPL2freq` und `freMTPL2sev`.

Für jede Variable werden folgende Informationen dokumentiert:

- fachliche Bedeutung,
- erwarteter Datentyp,
- Rolle im Projekt,
- sowie zentrale Prüfungen oder Hinweise für die spätere Datenverarbeitung.

Die Raw-Daten werden unverändert gespeichert. Änderungen von Datentypen, Kategorien oder Werten erfolgen ausschließlich in nachgelagerten Verarbeitungsstufen und werden dokumentiert.

## 2. Dataset Overview

| Dataset          | OpenML ID | Beobachtungsebene                  | Anzahl Spalten | Hauptzweck                                   |
| ---------------- | --------: | ---------------------------------- | -------------: | -------------------------------------------- |
| `freMTPL2freq` |     41214 | Eine Zeile pro Versicherungspolice |             12 | Analyse und Modellierung der Schadenfrequenz |
| `freMTPL2sev`  |     41215 | Eine Zeile pro Schadenereignis     |              2 | Analyse und Modellierung der Schadenhöhe    |

## 3. Data Dictionary — freMTPL2freq

| Variable       | Fachliche Bedeutung                                                         | Erwarteter Datentyp        | Rolle im Projekt                                                                                   | Zentrale Prüfungen / Hinweise                                                                                                                               |
| -------------- | --------------------------------------------------------------------------- | -------------------------- | -------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `IDpol`      | Eindeutige Identifikationsnummer einer Versicherungspolice                  | Integer / Identifier       | Primärschlüssel auf Policenebene; Verbindung mit`freMTPL2sev`; Grundlage für Train-Test-Split | Auf fehlende Werte und doppelte IDs prüfen. Obwohl die Raw-Datei den Wert als Float darstellen kann, besitzt die Variable keine fachliche Dezimalbedeutung. |
| `ClaimNb`    | Anzahl der während der Exposure-Periode beobachteten Schadenereignisse     | Integer                    | Zielinformation für die Modellierung der Schadenfrequenz                                          | Auf negative, fehlende oder auffällig hohe Werte prüfen. Später mit`claim_record_count` aus der aggregierten Severity-Tabelle vergleichen.              |
| `Exposure`   | Beobachtungs- beziehungsweise Versicherungsdauer als Anteil eines Jahres    | Float                      | Offset beziehungsweise Gewichtung für die Schadenfrequenz; Grundlage der Annualisierung           | Werte müssen größer als 0 sein. Werte über 1 werden als mögliche Datenqualitätsprobleme geprüft.                                                      |
| `Area`       | Kategorisierte Siedlungs- beziehungsweise Urbanisierungsdichte des Wohnorts | Category / String          | Erklärende regionale Variable                                                                     | Auf fehlende oder unbekannte Kategorien prüfen. Beziehung zu`Density` untersuchen.                                                                        |
| `VehPower`   | Geordnete Leistungskategorie des Fahrzeugs                                  | Integer / Ordered Category | Erklärende Fahrzeugvariable                                                                       | Nicht als direkte PS- oder kW-Angabe interpretieren. Wertebereich und seltene Kategorien prüfen.                                                            |
| `VehAge`     | Alter des Fahrzeugs in Jahren                                               | Integer                    | Erklärende Fahrzeugvariable                                                                       | Auf negative, fehlende oder unplausibel hohe Werte prüfen. Später mögliche Altersgruppen bilden.                                                          |
| `DrivAge`    | Alter der versicherten beziehungsweise fahrenden Person in Jahren           | Integer                    | Erklärende Fahrervariable                                                                         | Auf negative, fehlende oder fachlich unplausible Werte prüfen. Später mögliche Altersgruppen bilden.                                                      |
| `BonusMalus` | Bonus-Malus-Kennzahl zur Abbildung der bisherigen Schadenhistorie           | Integer / Numeric          | Erklärende Risikovariable                                                                         | Auf fehlende, extreme oder unplausible Werte prüfen. Nicht mit einer Kundenprämie verwechseln.                                                             |
| `VehBrand`   | Anonymisierte Fahrzeugmarken- oder Fahrzeugherstellergruppe                 | Category / String          | Erklärende Fahrzeugvariable                                                                       | Kategorien nicht ohne Quelle konkreten Marken zuordnen. Seltene Kategorien gegebenenfalls zu`Other` zusammenfassen.                                        |
| `VehGas`     | Kraftstoffart des Fahrzeugs                                                 | Category / String          | Erklärende Fahrzeugvariable                                                                       | Erwartete Kategorien und fehlende Werte prüfen.                                                                                                             |
| `Density`    | Bevölkerungsdichte am Wohnort, in der Regel Einwohner pro Quadratkilometer | Float / Numeric            | Erklärende regionale Variable                                                                     | Auf negative, fehlende und extreme Werte prüfen. Wegen möglicher Schiefe später`log(Density)` untersuchen.                                              |
| `Region`     | Anonymisierter beziehungsweise codierter französischer Regionsschlüssel   | Category / String          | Erklärende regionale Variable                                                                     | Auf fehlende, unbekannte und seltene Kategorien prüfen. Nicht als Postleitzahl interpretieren.                                                              |

## 4. Data Dictionary — freMTPL2sev

| Variable        | Fachliche Bedeutung                                                               | Erwarteter Datentyp  | Rolle im Projekt                                                                                                       | Zentrale Prüfungen / Hinweise                                                                                                                  |
| --------------- | --------------------------------------------------------------------------------- | -------------------- | ---------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| `IDpol`       | Identifikationsnummer der Versicherungspolice, zu der das Schadenereignis gehört | Integer / Identifier | Verbindungsschlüssel zur Policentabelle`freMTPL2freq`                                                               | Wiederholte`IDpol`-Werte sind erlaubt, da eine Police mehrere Schadenereignisse aufweisen kann. Auf fehlende Werte und Orphan Claims prüfen. |
| `ClaimAmount` | Betrag eines einzelnen Schadenereignisses                                         | Float / Numeric      | Zielinformation für die Modellierung der Schadenhöhe; Grundlage für`total_claim_amount` und `observed_severity` | Auf fehlende, negative, nullwertige und extreme Beträge prüfen. Für das Gamma-Modell müssen die verwendeten Zielwerte strikt positiv sein.  |

## 5. Cross-Dataset Relationships and Processing Rules

Die beiden Datensätze werden über die gemeinsame Variable `IDpol` miteinander verbunden. Da `freMTPL2sev` eine Zeile pro Schadenereignis enthält, darf die Tabelle nicht direkt mit `freMTPL2freq` verbunden werden.

Vor dem Join werden die Schadenereignisse auf Policenebene aggregiert:

| Neue Variable          | Berechnung                             | Bedeutung                                                        |
| ---------------------- | -------------------------------------- | ---------------------------------------------------------------- |
| `total_claim_amount` | Summe von`ClaimAmount` pro `IDpol` | Gesamter beobachteter Schadenbetrag einer Police                 |
| `claim_record_count` | Anzahl der Schadenzeilen pro`IDpol`  | Anzahl der in der Severity-Tabelle vorhandenen Schadenereignisse |

Anschließend wird die aggregierte Severity-Tabelle über einen Left Join mit `freMTPL2freq` verbunden. Dadurch bleiben auch Policen ohne Schadenereignis im analytischen Datenbestand erhalten.

Eine zentrale Cross-Table-Prüfung ist der Vergleich von:

- `ClaimNb` aus `freMTPL2freq`
- `claim_record_count` aus der aggregierten Severity-Tabelle

Abweichungen zwischen diesen beiden Werten werden als Datenqualitätsbefund dokumentiert und nicht automatisch korrigiert.

## 6. Curated Policy-Level Dataset

Der finale Curated-Datensatz wird unter:

`data/processed/policy_curated.pq`

gespeichert und umfasst **678.013 Policen** mit **einer Zeile pro `IDpol`**.

Neben den ursprünglichen Frequency-Merkmalen enthält die Curated-Schicht zusätzliche aggregierte, diagnostische und analytische Variablen.

| Variable                     | Bedeutung                                                                                  | Verwendung / Hinweis                                                                                                     |
| ---------------------------- | ------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------ |
| `exposure_capped`          | Technisch begrenzte Exposure-Variante                                                      | Wird ausschließlich dort verwendet, wo die entsprechende Modellierungslogik dies vorsieht; Raw Exposure bleibt erhalten |
| `high_claim_count`         | Kennzeichnung auffällig hoher Schadenanzahl                                               | Data-Quality- und Diagnosemerkmal                                                                                        |
| `total_claim_amount`       | Summe der beobachteten`ClaimAmount` je Police                                            | Grundlage für beobachtete Severity und Pure Premium                                                                     |
| `claim_record_count`       | Anzahl vorhandener Severity-Schadenrecords je Police                                       | Vergleich mit`ClaimNb`                                                                                                 |
| `claim_count_mismatch`     | Kennzeichnung einer Abweichung zwischen`ClaimNb` und verfügbaren Schadenrecords         | Data-Quality-Flag; nicht automatisch korrigiert                                                                          |
| `missing_severity`         | Kennzeichnet Policen mit Schaden, aber fehlender beobachtbarer vollständiger Schadenhöhe | Wichtig für Severity- und Loss-Evaluationspopulationen                                                                  |
| `observed_claim_frequency` | Beobachtete annualisierte Schadenfrequenz auf Policenebene                                 | Diagnostische Kennzahl                                                                                                   |
| `observed_severity`        | Beobachtete durchschnittliche Schadenhöhe einer Police, soweit verfügbar                 | Nur für geeignete Schadenpolicen interpretierbar                                                                        |
| `observed_pure_premium`    | Beobachteter Schadenaufwand relativ zur Exposure, soweit beobachtbar                       | Nicht mit Kundenprämie gleichsetzen                                                                                     |
| `driver_age_group`         | Gruppierung des Fahreralters                                                               | EDA, Power BI und Subgruppen-Diagnostik                                                                                  |
| `vehicle_age_group`        | Gruppierung des Fahrzeugalters                                                             | EDA und Power BI                                                                                                         |
| `bonus_malus_segment`      | Gruppierung der Bonus-Malus-Kennzahl                                                       | EDA, Risikoanalyse und Power BI                                                                                          |
| `log_density`              | Logarithmisch transformierte Bevölkerungsdichte                                           | Modellierungs- und Analysefeature                                                                                        |

### Missing-Severity-Regel

Eine fehlende beobachtbare Severity wird **nicht als Schadenhöhe `0` interpretiert**.

Dadurch ergeben sich für die finale Evaluation unterschiedliche Populationen:

- Frequency: vollständiger canonical Holdout,
- Severity: ausschließlich Severity-eligible Schadenpolicen,
- Tweedie / Loss Evaluation: common observable Holdout.

Diese Trennung ist methodisch notwendig, damit fehlende Schadenhöhen die Modellbewertung nicht verzerren.

---

## 7. Canonical Train-/Test-Split

Der festgelegte Split wird gespeichert unter:

`data/processed/policy_train_test_split.pq`

| Variable  | Bedeutung                                |
| --------- | ---------------------------------------- |
| `IDpol` | Eindeutige Policy-ID                     |
| `split` | Zugehörigkeit zu`train` oder `test` |

Finale Aufteilung:

| Split          | Policen |
| -------------- | ------: |
| Train          | 542.410 |
| Test / Holdout | 135.603 |

Der Split wird nach seiner Festlegung projektweit wiederverwendet und nicht erneut zufällig erzeugt.

---

## 8. Finale Modellvorhersagen

Die kombinierten Frequency-, Severity- und Two-Stage-Predictions werden unter:

`data/output/model_predictions.pq`

gespeichert.

| Variable                    | Bedeutung                                                             |
| --------------------------- | --------------------------------------------------------------------- |
| `idpol`                   | Eindeutige Policy-ID                                                  |
| `prediction_run_id`       | Identifikator des Prediction-Laufs                                    |
| `frequency_model_version` | Version des verwendeten Frequency-Modells                             |
| `severity_model_version`  | Version des verwendeten Severity-Modells                              |
| `predicted_frequency`     | Prognostizierte annualisierte Schadenfrequenz                         |
| `predicted_severity`      | Prognostizierte erwartete Schadenhöhe                                |
| `predicted_pure_premium`  | Two-Stage Pure Premium aus Frequency × Severity                      |
| `exposure_used`           | Für die Berechnung verwendete Exposure                               |
| `expected_claim_count`    | Erwartete Schadenanzahl:`predicted_frequency × exposure_used`      |
| `expected_claim_amount`   | Erwarteter Schadenaufwand:`predicted_pure_premium × exposure_used` |
| `scored_at`               | Zeitpunkt des Prediction-Laufs                                        |

### Wichtige Aggregationsregel

`predicted_frequency` und `predicted_pure_premium` sind annualisierte Raten und dürfen auf Portfolioebene nicht einfach summiert werden.

Für Portfolioaggregation gilt:

`Expected Claims = predicted_frequency × Exposure`

und:

`Expected Loss = predicted_pure_premium × Exposure`

---

## 9. Tweedie Predictions

Die direkten Tweedie-Pure-Premium-Prognosen werden unter:

`data/output/tweedie_predictions.pq`

gespeichert.

| Variable                           | Bedeutung                                                                     |
| ---------------------------------- | ----------------------------------------------------------------------------- |
| `idpol`                          | Eindeutige Policy-ID                                                          |
| `tweedie_model_version`          | Version des finalen Tweedie-Modells                                           |
| `predicted_pure_premium_tweedie` | Direkt prognostiziertes annualisiertes Pure Premium                           |
| `exposure_used`                  | Für die Berechnung verwendete Exposure                                       |
| `expected_loss_tweedie`          | Erwarteter Schadenaufwand:`predicted_pure_premium_tweedie × exposure_used` |

Das Tweedie Pure Premium wird als zentraler direkter Risikoscore für Ranking, Risk Deciles und Risikosegmentierung verwendet.

---

## 10. Risk Segmentation und Decision-Support-Outputs

Zusätzliche Policy-Level-Ergebnisse werden unter anderem in:

- `data/output/risk_segments.pq`
- `data/output/policy_action_priorities.pq`

gespeichert.

Zentrale fachliche Felder umfassen:

| Feld / Konzept                                      | Bedeutung                                                                             |
| --------------------------------------------------- | ------------------------------------------------------------------------------------- |
| `risk_decile`                                     | Relative Risikoposition von 1 bis 10; 10 entspricht dem höchsten modellierten Risiko |
| `risk_segment`                                    | Finale Segmentierung: LOW, STANDARD, ELEVATED oder HIGH                               |
| `priority`                                        | Operative Priorisierung für Decision Support                                         |
| `predicted_pure_premium_tweedie` / `tweedie_pp` | Direkter Tweedie-Pure-Premium-Risikoscore                                             |
| `expected_loss_tweedie`                           | Exposure-gewichteter erwarteter Schadenaufwand                                        |

Die finale Risikosegmentierung basiert auf der Verteilung des Tweedie-Pure-Premium-Scores:

| Segment  | Definition |
| -------- | ---------- |
| LOW      | bis P50    |
| STANDARD | P50–P75   |
| ELEVATED | P75–P90   |
| HIGH     | über P90  |

Ein HIGH-Segment bedeutet **keine automatische Ablehnung**. Es kennzeichnet lediglich eine erhöhte modellierte Risikoposition und kann eine manuelle fachliche Prüfung priorisieren.

---

## 11. Fachliche Begriffsabgrenzung

### Pure Premium

Das Pure Premium beschreibt den statistisch erwarteten annualisierten Schadenaufwand.

Es ist **keine Endkundenprämie** und enthält insbesondere keine:

- Verwaltungskosten,
- Vertriebskosten,
- Steuern,
- Gewinnmargen,
- Sicherheitszuschläge,
- Rückversicherungskosten.

### Expected Loss

Expected Loss berücksichtigt zusätzlich die tatsächliche Exposure:

`Expected Loss = Pure Premium × Exposure`

### Risk Segment

Ein Risk Segment beschreibt eine relative Position innerhalb des analysierten Portfolios.

Es ist weder eine regulatorische Risikoklasse noch eine automatische Annahme- oder Ablehnungsentscheidung.
