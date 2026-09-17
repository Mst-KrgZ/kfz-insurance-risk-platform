# Model Card – Kfz Insurance Risk & Pure Premium Intelligence Platform

## 1. Zweck

Diese Model Card dokumentiert die final eingesetzten statistischen Modelle des Projekts **Kfz Insurance Risk & Pure Premium Intelligence Platform**.

Die Plattform unterstützt die datenbasierte Analyse von Kfz-Versicherungsrisiken durch drei komplementäre Modellperspektiven:

- Schadenfrequenz (Frequency),
- Schadenhöhe (Severity),
- annualisierte erwartete Schadenkosten (Pure Premium).

Zusätzlich werden Frequency und Severity im Two-Stage-Ansatz kombiniert.

Die Modelle dienen ausschließlich der **analytischen Entscheidungsunterstützung** und ersetzen keine fachliche Underwriting-, Pricing- oder regulatorische Entscheidung.

---

## 2. Intended Use

Die Modelloutputs können insbesondere verwendet werden für:

- Portfolioanalyse,
- Analyse von Risikokonzentrationen,
- Risk Deciles und Risikosegmentierung,
- Vergleich von beobachteter und prognostizierter Portfolio-Performance,
- Frequency-Severity-Dekomposition,
- Priorisierung manueller fachlicher Prüfungen,
- Data- und Model-Monitoring,
- analytische Entscheidungsunterstützung für Underwriting und Portfoliosteuerung.

Die Modelle wurden als prototypische Analytics-Komponenten entwickelt und nicht als produktives vollautomatisches Versicherungssystem.

---

## 3. Nicht vorgesehene Nutzung

Die Modelloutputs dürfen nicht unmittelbar verwendet oder interpretiert werden als:

- automatische Annahme- oder Ablehnungsentscheidung,
- automatische Kündigungsentscheidung,
- finale Kundenprämie,
- vollständiger Versicherungstarif,
- Aussage über Gewinn oder Verlust einer einzelnen Police,
- kausale Aussage über Schadenursachen,
- vollständiger Fairness- oder Nichtdiskriminierungsnachweis,
- Ersatz menschlicher fachlicher Prüfung.

Ein **HIGH-Risk-Segment bedeutet insbesondere keine automatische Ablehnung**.

---

## 4. Datenbasis

Das Projekt verwendet die öffentlich verfügbaren OpenML-Datensätze:

- `freMTPL2freq`
- `freMTPL2sev`

Die finale Policy-Level-Datenbasis umfasst:

**678.013 Policen**

Die Daten stammen aus OpenML. Der ursprünglich geplante automatisierte Abruf über die OpenML-API wurde aufgrund wiederholter HTTP-504-Fehler nicht als alleiniger Bezugsweg verwendet.

Die Datensätze wurden deshalb direkt vom OpenML Static Data Server heruntergeladen und unverändert in der lokalen Raw-Data-Schicht gespeichert. Die Ingestion-Pipeline validiert diese Quelldateien anschließend anhand von Manifestinformationen, Dateigröße, SHA256-Checksummen, Metadaten und Schema-Prüfungen.

Eine Policy entspricht dabei einer eindeutigen `IDpol`.

Weitere Details:

- [Business Understanding](business_understanding.md)
- [Data Dictionary](data_dictionary.md)
- [Data Quality Report](data_quality_report.md)

---

## 5. Train-/Test-Split

Für das Projekt wird ein fest definierter und projektweit wiederverwendeter canonical Split verwendet.

| Split   | Policen |
| ------- | ------: |
| Train   | 542.410 |
| Holdout | 135.603 |
| Gesamt  | 678.013 |

Zwischen Train- und Holdout-Split besteht keine Überschneidung der Policy-IDs.

Der Split wird nach seiner Festlegung nicht neu erzeugt.

### Holdout-Historie

Der Holdout wurde im Projektverlauf bereits für frühere Diagnose- und Vergleichsschritte betrachtet.

Er wird deshalb transparent **nicht als vollständig unberührter Blind-Test** dargestellt.

Finale Weiterentwicklungen und Modellentscheidungen wurden anschließend auf Train-Daten und Cross-Validation beschränkt.

Die finalen Holdout-Ergebnisse dienen der Abschlussdiagnostik und nicht dem nachträglichen Hyperparameter-Tuning.

---

## 6. Unterschiedliche Evaluationspopulationen

Aufgrund fehlender beobachtbarer Schadenhöhen können nicht alle Modelle auf derselben Population bewertet werden.

| Modell / Analyse          |           Evaluation Population |
| ------------------------- | ------------------------------: |
| Frequency                 |                 135.603 Policen |
| Severity                  | 4.999 Severity-eligible Policen |
| Tweedie / Loss Evaluation |                 133.790 Policen |

### Missing Severity

Eine Police mit beobachtetem Schaden, aber fehlender beobachtbarer Schadenhöhe wird **nicht als Schadenhöhe null interpretiert**.

Im Holdout bestehen:

- 6.812 Policen mit `ClaimNb > 0`,
- davon 4.999 mit beobachtbarer positiver Severity,
- und 1.813 mit fehlender beobachtbarer Schadenhöhe.

Diese Trennung verhindert eine systematische Verzerrung der Severity- und Pure-Premium-Evaluation.

---

# 7. Frequency-Modell

## Modellversion

`frequency_poisson_quantile_spline_full_v2`

## Modelltyp

Poisson GLM mit nichtlinearen Feature-Transformationen.

## Ziel

Schätzung der annualisierten erwarteten Schadenfrequenz.

Die Exposure wird explizit berücksichtigt, damit Policen mit unterschiedlichen Beobachtungszeiträumen fachlich korrekt gewichtet werden.

## Finale Holdout-Ergebnisse

| Kennzahl                       |           Ergebnis |
| ------------------------------ | -----------------: |
| Baseline Mean Poisson Deviance |           0.625748 |
| Modell Mean Poisson Deviance   |           0.592685 |
| Verbesserung ggü. Baseline    |             5,28 % |
| D²                            |             0.0528 |
| Gini                           |             0.2903 |
| Beobachtete Schäden           |              7.236 |
| Prognostizierte Schäden       |           7.217,91 |
| Portfolio-Abweichung           | **−0,25 %** |

## Interpretation

Das Frequency-Modell zeigt:

- gute Portfolio-Kalibrierung,
- Verbesserung gegenüber der Constant Baseline,
- und eine nützliche Risikorangfolge.

Unter den finalen Modellkomponenten besitzt Frequency außerdem die stabilste Subgruppen-Kalibrierung.

---

# 8. Severity-Modell

## Modellversion

`severity_gamma_spline_scaled_full_v2`

## Modelltyp

Gamma GLM.

## Ziel

Schätzung der erwarteten Schadenhöhe für Policen mit beobachtbarer positiver Schadenhöhe.

Die Modellbewertung erfolgt **ClaimNb-gewichtet**.

Gamma-Modellierung wird ausschließlich auf positiven Zielwerten durchgeführt.

Die Data-Quality-Schicht prüft deshalb bereits vor der Modellierung, dass die verwendeten Schadenhöhen größer als null sind.

## Finale Holdout-Ergebnisse

| Kennzahl                                  |          Ergebnis |
| ----------------------------------------- | ----------------: |
| Baseline Gamma Deviance                   |          1.543630 |
| Modell Gamma Deviance                     |          1.567498 |
| D²                                       |          −0.0155 |
| Gini                                      |            0.0033 |
| Beobachtete claim-gewichtete Severity     |       2.081,27 € |
| Prognostizierte claim-gewichtete Severity |       2.164,21 € |
| Portfolio-Abweichung                      | **+3,99 %** |

## Bekannte Einschränkung

Das finale Severity-Modell liegt bei der Gamma-Deviance leicht über der Constant Baseline.

Auch der Gini von `0.0033` zeigt nur eine sehr geringe eigenständige Ranking-Fähigkeit.

Das Modell wird deshalb **nicht als starker eigenständiger Risikoscore** interpretiert.

Seine primäre Rolle besteht in der monetären Dekomposition innerhalb des Two-Stage-Ansatzes.

---

# 9. Two-Stage Pure Premium

Der Two-Stage-Ansatz kombiniert Frequency und Severity:

`Predicted Pure Premium = Predicted Frequency × Predicted Severity`

Damit kann der erwartete Schadenaufwand fachlich zerlegt werden in:

1. erwartete Schadenhäufigkeit,
2. erwartete Schadenhöhe,
3. daraus resultierende annualisierte erwartete Schadenkosten.

Der Two-Stage-Ansatz wird im Projekt primär verwendet für:

- monetäre Interpretation,
- Frequency-Severity-Dekomposition,
- Diagnostik,
- und fachliche Erklärung der erwarteten Schadenkosten.

Aufgrund der bekannten Severity-Limitation wird der Two-Stage-Output nicht als alleiniger finaler Ranking-Score verwendet.

---

# 10. Direktes Tweedie-Modell

## Modellversion

`tweedie_direct_pure_premium_full_v1`

## Modelltyp

Tweedie Regressor.

## Ziel

Direkte Schätzung des annualisierten Pure Premium auf Policenebene.

Das Tweedie-Modell ermöglicht die gemeinsame Modellierung einer Zielverteilung mit:

- vielen Nullwerten,
- positiven kontinuierlichen Schadenbeträgen,
- und stark rechtsschiefer Verteilung.

## Finale Konfiguration

- Tweedie Power: `1.9`
- Alpha: `0.0`

## Finale Holdout-Ergebnisse

| Kennzahl                  |          Ergebnis |
| ------------------------- | ----------------: |
| Baseline Tweedie Deviance |         34.602470 |
| Modell Tweedie Deviance   |         34.364453 |
| Gini                      |            0.2677 |
| Portfolio-Abweichung      | **+6,40 %** |

## Rolle

Das finale Tweedie-Modell wird als zentraler direkter Pure-Premium-Risikoscore verwendet für:

- Ranking,
- Risk Deciles,
- Risikosegmentierung,
- Portfolioanalyse,
- Decision Support.

Die direkte Tweedie-Schätzung und der Two-Stage-Ansatz erfüllen unterschiedliche Funktionen und werden nicht als reiner Winner-takes-all-Vergleich interpretiert.

---

# 11. Finale Modellrollen

| Modell    | Primäre Funktion                                                |
| --------- | ---------------------------------------------------------------- |
| Frequency | Schadenhäufigkeit und Portfolio-Kalibrierung                    |
| Severity  | Monetäre Schadenhöhenkomponente                                |
| Two-Stage | Dekomposition und fachliche Interpretation                       |
| Tweedie   | Direkter Pure-Premium-Risikoscore für Ranking und Segmentierung |

Die Plattform verwendet damit bewusst mehrere komplementäre Modellperspektiven.

---

# 12. Risikosegmentierung

Die finale Risikosegmentierung basiert auf:

`predicted_pure_premium_tweedie`

Verwendete Grenzen:

| Segment  |   Grenze |
| -------- | -------: |
| LOW      |   ≤ P50 |
| STANDARD | P50–P75 |
| ELEVATED | P75–P90 |
| HIGH     |    > P90 |

Quantile:

| Quantil | Tweedie Pure Premium |
| ------- | -------------------: |
| P50     |            119,35 € |
| P75     |            187,90 € |
| P90     |            328,24 € |

Portfolioverteilung:

| Segment  | Policen | Anteil |
| -------- | ------: | -----: |
| LOW      | 339.008 |   50 % |
| STANDARD | 169.508 |   25 % |
| ELEVATED | 101.695 |   15 % |
| HIGH     |  67.802 |   10 % |

Das HIGH-Segment umfasst rund **10 % der Policen**, trägt jedoch rund **32,1 % des modellierten Tweedie Expected Loss**.

Diese Segmentierung beschreibt eine relative Risikoposition innerhalb des analysierten Portfolios.

---

# 13. Subgruppen-Performance

Die finalen Modelle wurden auf dem canonical Holdout nach folgenden Dimensionen untersucht:

- Fahrer-Altersgruppe,
- Region,
- Area,
- Density-Quantile.

Die Analyse wurde ausschließlich als finale Diagnostik durchgeführt.

Es erfolgten:

- keine erneute Modellauswahl,
- kein Hyperparameter-Tuning,
- keine Änderung des canonical Splits.

## Frequency

Frequency zeigt insgesamt die stabilste Subgruppen-Kalibrierung.

Die meisten untersuchten Gruppen liegen vergleichsweise nahe an der beobachteten Schadenfrequenz.

Eine relevante Auffälligkeit besteht beispielsweise in der Altersgruppe **75+**, in der die Schadenfrequenz um rund **11,6 % unterschätzt** wird.

## Severity

Severity zeigt deutlich stärkere Unterschiede zwischen Subgruppen.

Besonders ausgeprägte Abweichungen treten unter anderem in einzelnen Alters-, Region- und Area-Gruppen auf.

Diese Beobachtung ist konsistent mit:

- der schwachen Ranking-Fähigkeit,
- der Gamma-Deviance gegenüber der Baseline,
- und der heavy-tailed Schadenhöhenverteilung.

## Tweedie Pure Premium

Auch die Tweedie-Pure-Premium-Kalibrierung ist nicht in allen Subgruppen homogen.

Während einige größere Gruppen eine gute Übereinstimmung zeigen, bestehen in anderen Alters-, Region-, Area- und Density-Gruppen relevante Abweichungen.

Die zentrale Schlussfolgerung lautet:

> **Eine gute Portfolio-Performance garantiert keine gleichmäßige Modellperformance in jeder Teilpopulation.**

---

# 14. Responsible Use

Die Modelloutputs dienen als **Decision Support**.

Für ihre Verwendung gelten folgende Regeln:

- HIGH Risk bedeutet keine automatische Ablehnung.
- Pure Premium ist kein Kundenpreis.
- Modelloutputs ersetzen keine menschliche fachliche Entscheidung.
- Kleine Subgruppen dürfen nicht überinterpretiert werden.
- Heavy-tailed Schadenhöhen erhöhen die Unsicherheit insbesondere bei Severity.
- Subgruppenanalysen erhöhen die Transparenz, stellen aber keinen vollständigen Fairness-Nachweis dar.
- Fahrer-, Regional- und andere Segmentmerkmale müssen bei einer produktiven Nutzung zusätzlich fachlich und regulatorisch geprüft werden.
- Ein produktiver Einsatz erfordert Monitoring von Datenqualität, Kalibrierung und Subgruppen-Performance.

---

# 15. Verbotene Interpretationen

Folgende Aussagen werden durch die Modelle **nicht** unterstützt:

> „HIGH-Risk-Kunden sollten automatisch abgelehnt werden.“

> „Das prognostizierte Pure Premium ist der Preis, den ein Kunde zahlen sollte.“

> „Eine höhere Modellprognose beweist, dass ein bestimmtes Merkmal den Schaden verursacht.“

> „Gute globale Modellmetriken beweisen, dass das Modell in jeder Subgruppe gleich gut funktioniert.“

> „Das Severity-Modell ist ein starker eigenständiger Ranking-Score.“

Diese Interpretationen widersprechen dem vorgesehenen Einsatz der Plattform.

---

# 16. Monitoring bei produktiver Nutzung

Bei einer möglichen produktiven Weiterentwicklung sollten regelmäßig überwacht werden:

- Datenqualität und Schemaänderungen,
- Exposure-Verteilung,
- Claim Frequency,
- Severity-Verteilung,
- Pure-Premium-Kalibrierung,
- Risk-Decile-Stabilität,
- Subgruppen-Performance,
- Portfolio-Mix,
- Prediction Drift,
- Änderungen regulatorischer oder fachlicher Rahmenbedingungen.

Ein produktiver Einsatz würde außerdem definierte Schwellenwerte für Warnungen, Re-Kalibrierung und gegebenenfalls Modellneuentwicklung benötigen.

---

# 17. Zentrale Limitationen

Die wichtigsten bekannten Limitationen sind:

- fehlende beobachtbare Severity für einen Teil der Schadenpolicen,
- stark heavy-tailed Schadenhöhen,
- begrenzte eigenständige Severity-Performance,
- heterogene Kalibrierung in einzelnen Subgruppen,
- bereits im Projektverlauf betrachteter Holdout,
- historische und prototypische Datenbasis,
- keine Kausalinterpretation,
- keine vollständige regulatorische Produktionsvalidierung,
- kein vollständiger Fairness- oder Nichtdiskriminierungsnachweis.

Diese Einschränkungen werden bewusst dokumentiert und bei der Interpretation der Modelloutputs berücksichtigt.

---

# 18. Schlussfolgerung

Die finale Modellarchitektur kombiniert mehrere statistische Perspektiven statt einen einzelnen Score für sämtliche Aufgaben zu verwenden.

Das Frequency-Modell liefert eine gut kalibrierte Schadenhäufigkeitskomponente.

Das Severity-Modell ergänzt die monetäre Dekomposition, wird aufgrund seiner begrenzten Ranking-Fähigkeit jedoch vorsichtig interpretiert.

Der Two-Stage-Ansatz ermöglicht eine fachlich nachvollziehbare Zerlegung der erwarteten Schadenkosten.

Das direkte Tweedie-Modell liefert den zentralen Risiko-Score für Ranking und Segmentierung.

Die Modelloutputs sind damit für transparente Portfolioanalyse und Entscheidungsunterstützung geeignet, müssen jedoch immer gemeinsam mit Datenqualität, Modellgrenzen, Subgruppen-Performance und fachlicher Beurteilung interpretiert werden.
