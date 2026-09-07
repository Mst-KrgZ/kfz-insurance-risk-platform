# Datenqualitätsbericht

## Projekt

**Kfz Insurance Risk & Pure Premium Intelligence Platform**

## Zweck des Berichts

Dieser Bericht dokumentiert die Ergebnisse der automatisierten
Datenqualitätsprüfungen für die Frequency- und Severity-Datensätze von
freMTPL2.

Für jeden relevanten Befund werden folgende Punkte festgehalten:

- Was wurde festgestellt?
- Welche Entscheidung wurde getroffen?
- Warum wurde diese Entscheidung getroffen?
- Welche Auswirkungen hat der Befund auf die Modellierung?

Die Rohdaten werden nicht verändert. Bereinigungen und fachliche
Transformationen erfolgen ausschließlich in einer späteren Curated- oder
Modeling-Schicht.

## Datensatzübersicht

| Datensatz    |  Zeilen | Spalten | Zweck                                        |
| ------------ | ------: | ------: | -------------------------------------------- |
| freMTPL2freq | 678.013 |      12 | Policenbasierte Daten zur Schadenhäufigkeit |
| freMTPL2sev  |  26.639 |       2 | Schadenbasierte Daten zu Schadenhöhen       |

## Management Summary

Insgesamt wurden neun automatisierte Datenqualitätsprüfungen durchgeführt.

- 4 Prüfungen mit Status `PASS`
- 2 Prüfungen mit Status `WARN`
- 3 Prüfungen mit Status `FAIL`

Die wichtigste Einschränkung betrifft die unvollständige Abdeckung der
Schadenhöhen.

Im Frequency-Datensatz befinden sich 34.060 Policen mit mindestens einem
gemeldeten Schaden. Für 24.944 dieser Policen ist mindestens ein passender
Severity-Datensatz vorhanden.

Für 9.116 Policen mit gemeldetem Schaden fehlt dagegen vollständig die
Information zur Schadenhöhe. Das entspricht 26,7645 % aller Policen mit
mindestens einem Schaden.

Diese Policen können weiterhin für das Frequency-Modell verwendet werden.
Für ein policenbasiertes Severity-Modell und für ein direktes
Pure-Premium-Modell können sie jedoch nicht ohne Weiteres genutzt werden,
da die tatsächliche Schadenhöhe unbekannt ist.

Der Datensatz ist außerdem stark von Policen ohne Schaden geprägt:

- Policen ohne Schaden: 643.953
- Anteil der Policen ohne Schaden: 94,9765 %

Diese starke Klassenungleichheit muss bei der Modellierung der
Schadenhäufigkeit berücksichtigt werden.

## Definition der Prüfstatus

| Status | Bedeutung                                                                             |
| ------ | ------------------------------------------------------------------------------------- |
| PASS   | Es wurde kein relevanter Datenqualitätsfehler festgestellt                           |
| WARN   | Es liegt ein auffälliger Befund vor, aber kein eindeutig nachweisbarer Regelverstoß |
| FAIL   | Eine fachliche, technische oder referenzielle Datenregel wurde verletzt               |

## Übersicht der Datenqualitätsprüfungen

| Prüfung                       | Status | Fehlerhafte Zeilen | Warnungen |
| ------------------------------ | ------ | -----------------: | --------: |
| Fehlende Werte – Frequency    | PASS   |                  0 |         0 |
| Fehlende Werte – Severity     | PASS   |                  0 |         0 |
| Exposure-Grenzen               | FAIL   |              1.224 |         0 |
| Grenzen der Schadenanzahl      | WARN   |                  0 |         9 |
| Grenzen der Schadenhöhe       | PASS   |                  0 |         0 |
| Frequency-Severity-Konsistenz  | FAIL   |              9.117 |         0 |
| Verwaiste Severity-Datensätze | FAIL   |                195 |         0 |
| Doppelte Datensätze           | WARN   |                  0 |       255 |
| Join-Kardinalität             | PASS   |                  0 |         0 |

## Detaillierte Befunde und Entscheidungen

### 1. Exposure-Werte größer als eins

#### Befund

Im Frequency-Datensatz befinden sich 1.224 Policen mit einem `Exposure`-Wert
größer als 1.

- Minimaler Exposure-Wert: 0,002732
- Maximaler Exposure-Wert: 2,01
- Zeilen mit `Exposure <= 0`: 0
- Zeilen mit `Exposure > 1`: 1.224
- Anteil der betroffenen Frequency-Zeilen: 0,1805 %

#### Entscheidung

Die Rohdaten bleiben unverändert.

In der Curated-Schicht wurden `Exposure`-Werte größer als 1 auf maximal
1,0 begrenzt.

Zusätzlich wurde die boolesche Indikatorspalte `exposure_capped` erstellt.
Insgesamt sind 1.224 Policen entsprechend gekennzeichnet.

Dadurch bleibt nachvollziehbar, bei welchen Policen eine Begrenzung
durchgeführt wurde.

#### Begründung

`Exposure` beschreibt die Beobachtungsdauer einer Police in Jahren.

Für die geplanten Frequency- und Pure-Premium-Modelle wird eine maximale
jährliche Beobachtungsdauer von 1 erwartet. Werte größer als 1 könnten
ansonsten zu einer übermäßigen Gewichtung einzelner Policen führen.

Ein vollständiger Ausschluss der betroffenen Policen würde jedoch weitere
verwertbare Risikomerkmale dieser Datensätze entfernen.

Die Begrenzung auf 1,0 stellt daher einen nachvollziehbaren Kompromiss
zwischen Datenqualität und Informationsverlust dar.

#### Auswirkungen auf die Modellierung

Für das Frequency-Modell wird der begrenzte Exposure-Wert als
Beobachtungsdauer beziehungsweise als Grundlage für Gewichtung oder Offset
verwendet.

Betroffen sind 1.224 von insgesamt 678.013 Policen. Dies entspricht etwa
0,1805 % des Frequency-Datensatzes.

Die ursprünglichen Werte bleiben in der Raw-Schicht vollständig erhalten und
können jederzeit nachvollzogen werden.

### 2. Auffällig hohe Schadenanzahl

#### Befund

Im Frequency-Datensatz befinden sich neun Policen mit einem `ClaimNb`-Wert
größer als 4.

- Minimaler `ClaimNb`-Wert: 0
- Maximaler `ClaimNb`-Wert: 16
- Negative Werte: 0
- Nicht ganzzahlige Werte: 0
- Policen oberhalb des definierten Schwellenwertes von 4: 9
- Anteil der betroffenen Frequency-Zeilen: 0,0013 %

Der Schwellenwert von 4 stellt keine fachlich unmögliche Obergrenze dar.
Er dient ausschließlich dazu, außergewöhnlich hohe Schadenanzahlen für eine
weitere Prüfung zu kennzeichnen.

#### Entscheidung

Die neun betroffenen Policen wurden nicht entfernt und ihre ursprünglichen
`ClaimNb`-Werte wurden nicht verändert.

In der Curated-Schicht wurde die boolesche Indikatorspalte
`high_claim_count` erstellt.

Alle neun Policen mit `ClaimNb > 4` sind damit gekennzeichnet.

Die Prüfung behält den Status `WARN`, da hohe Schadenanzahlen auffällig,
aber nicht nachweislich fehlerhaft sind.

#### Begründung

Eine hohe Schadenanzahl kann ungewöhnlich sein, ist jedoch nicht grundsätzlich
unmöglich.

Ohne zusätzliche Informationen über Schadenart, Schadenzeitpunkt oder
mögliche Sammelschäden kann nicht nachgewiesen werden, dass diese Werte
fehlerhaft sind.

Ein Ausschluss oder eine Begrenzung der Werte würde daher auf einer
willkürlichen Annahme beruhen und könnte reale Hochrisiko-Policen aus dem
Datensatz entfernen.

#### Auswirkungen auf die Modellierung

Die Policen bleiben grundsätzlich im Frequency-Datensatz und können bei der
Modellierung der Schadenhäufigkeit berücksichtigt werden.

Ihr Einfluss wird während der explorativen Analyse und der
Modellvalidierung gesondert untersucht.

Insbesondere wird geprüft, ob die neun Policen einen unverhältnismäßig starken
Einfluss auf Modellparameter, Deviance und Kalibrierung ausüben.

Die Kennzeichnung durch `high_claim_count` ermöglicht außerdem eine getrennte
Auswertung dieser auffälligen Policen, ohne die Rohinformation zu verlieren.

### 3. Gültigkeit und Verteilung der Schadenhöhen

#### Befund

Im Severity-Datensatz wurden keine ungültigen Schadenhöhen festgestellt.

- Minimale Schadenhöhe: 1,00 €
- Maximale Schadenhöhe: 4.075.400,56 €
- Zeilen mit `ClaimAmount <= 0`: 0
- 99-%-Quantil: 16.793,70 €
- 99,9-%-Quantil: 162.784,44 €

Die Prüfung erhält den Status `PASS`, da alle vorhandenen Schadenhöhen
größer als null sind.

Die Verteilung ist jedoch stark rechtsschief und enthält einzelne sehr hohe
Schadenbeträge.

#### Entscheidung

Die positiven Schadenhöhen werden nicht entfernt, begrenzt oder verändert.

Insbesondere wird auch der maximale Schadenbetrag von 4.075.400,56 € zunächst
beibehalten.

Sehr hohe Schadenbeträge werden in der explorativen Analyse und während der
Modellvalidierung gesondert untersucht.

#### Begründung

Hohe Schadenbeträge sind im Versicherungskontext nicht automatisch
Datenfehler. Sie können reale Großschäden darstellen.

Da keine zusätzlichen Informationen vorhanden sind, die einen Erfassungsfehler
belegen, wäre eine automatische Entfernung oder Begrenzung fachlich nicht
ausreichend begründet.

Alle vorhandenen `ClaimAmount`-Werte sind positiv. Dadurch ist sichergestellt,
dass die für das Gamma-Severity-Modell verwendeten aggregierten
Schadenbeträge ebenfalls positiv sind.

#### Auswirkungen auf die Modellierung

Für das Gamma-Severity-Modell werden ausschließlich Policen mit vorhandenen
und positiven Schadenhöhen verwendet.

Die starke Rechtsschiefe und die einzelnen Großschäden können einen erheblichen
Einfluss auf Modellparameter und Gütemaße haben.

Deshalb werden während der Modellierung insbesondere folgende Punkte geprüft:

- Verteilung der Schadenhöhen auf logarithmischer Skala
- Einfluss besonders hoher Schäden auf die Gamma-Deviance
- Stabilität der Modellparameter
- Kalibrierung in hohen Risikobereichen

Großschäden bleiben im Hauptdatensatz erhalten. Zusätzliche
Sensitivitätsanalysen können später zeigen, wie stark die Modellergebnisse von
diesen Beobachtungen beeinflusst werden.

### 4. Konsistenz zwischen Schadenanzahl und Schadenhöhen

#### Befund

Die im Frequency-Datensatz angegebene Schadenanzahl `ClaimNb` wurde mit der
Anzahl der vorhandenen Severity-Zeilen je `IDpol` verglichen.

Dabei wurden insgesamt 9.117 inkonsistente Policen festgestellt.

- Policen mit `ClaimNb > 0`, aber ohne Severity-Datensatz: 9.116
- Policen mit `ClaimNb = 0`, aber mit Severity-Datensatz: 0
- Policen mit positiven, aber voneinander abweichenden Schadenanzahlen: 1

Der einzelne Fall mit abweichender positiver Schadenanzahl betrifft:

- `IDpol`: 4.158.255
- `ClaimNb` im Frequency-Datensatz: 2
- Anzahl der Severity-Zeilen: 1

Von insgesamt 678.013 Policen weisen 34.060 mindestens einen gemeldeten
Schaden auf.

Für 24.944 dieser Policen ist mindestens ein passender Severity-Datensatz
vorhanden. Nur 24.943 Policen weisen eine vollständig übereinstimmende
Schadenanzahl auf.

Für 9.116 Policen mit gemeldetem Schaden fehlt die Information zur
Schadenhöhe vollständig. Dies entspricht 26,7645 % aller Policen mit
mindestens einem Schaden.

#### Entscheidung

Die 9.116 Policen ohne Severity-Datensatz bleiben im Frequency-Datensatz
erhalten und können für die Modellierung der Schadenhäufigkeit verwendet
werden.

In der Curated-Schicht wurde für diese Policen die boolesche
Indikatorspalte `missing_severity` gesetzt.

Die unbekannten Schadenbeträge wurden ausdrücklich nicht mit null imputiert.
Für diese Policen bleiben `total_claim_amount` und die daraus abgeleiteten
Severity- beziehungsweise Pure-Premium-Werte NULL beziehungsweise NaN.

Die Police mit `IDpol` 4.158.255 bleibt ebenfalls im policenbasierten
Frequency-Datensatz erhalten.

Zusätzlich wurde die boolesche Indikatorspalte `claim_count_mismatch`
erstellt. Sie kennzeichnet genau diese eine Police, bei der `ClaimNb = 2`
angegeben ist, jedoch nur eine Severity-Zeile vorhanden ist.

Policen mit `missing_severity = TRUE` sowie die Police mit
`claim_count_mismatch = TRUE` werden für die policenbasierte
Severity-Modellierung und das direkte Pure-Premium-/Tweedie-Training
nicht als vollständig beobachtete Schadenhöhen behandelt.

#### Begründung

Das Frequency-Modell benötigt als Zielvariable ausschließlich die
Schadenanzahl und kann deshalb grundsätzlich mit allen 678.013 Policen
arbeiten.

Das Severity-Modell benötigt dagegen eine tatsächlich beobachtete positive
Schadenhöhe. Für Policen ohne Severity-Information kann keine verlässliche
Zielvariable gebildet werden.

Eine automatische Imputation mit null oder einem durchschnittlichen
Schadenbetrag würde eine nicht belegte Annahme darstellen und könnte das
Severity- und Pure-Premium-Modell systematisch verzerren.

Der Ausschluss erfolgt deshalb nur in der jeweiligen Modeling-Schicht.
Die ursprünglichen Datensätze bleiben in der Raw-Schicht unverändert.

#### Auswirkungen auf die Modellierung

Für die geplanten Modelle ergeben sich unterschiedliche Datenbasen:

- Frequency-Modell: bis zu 678.013 Policen
- Policen mit mindestens einem gemeldeten Schaden: 34.060
- Policen mit mindestens einem Severity-Datensatz: 24.944
- Vollständig konsistente Policen für die policenbasierte
  Severity-Modellierung: 24.943
- Claim-Level-Severity-Zeilen mit passender Frequency-Police: 26.444

Damit fehlen für 26,7645 % der Policen mit gemeldetem Schaden vollständige
Informationen zur Schadenhöhe.

Die Ergebnisse des Severity- und Pure-Premium-Modells müssen deshalb
vorsichtiger interpretiert werden. Insbesondere ist zu prüfen, ob die Policen
mit vorhandenen Schadenhöhen die Gesamtheit aller Schadenpolicen
repräsentativ abbilden.

Diese Einschränkung wird in der Modellbewertung, im Abschlussbericht und in
der Präsentation ausdrücklich dokumentiert.

### 5. Verwaiste Severity-Datensätze

#### Befund

Im Severity-Datensatz wurden 195 Zeilen festgestellt, deren `IDpol` im
Frequency-Datensatz nicht vorhanden ist.

Diese Zeilen gehören zu insgesamt sechs unterschiedlichen Policen.

|     IDpol | Severity-Zeilen | Gesamtschadenhöhe |
| --------: | --------------: | -----------------: |
| 2.262.511 |              66 |      151.800,59 € |
| 2.282.134 |              36 |      330.920,05 € |
| 2.227.533 |              25 |       64.093,76 € |
| 2.220.367 |              24 |       84.441,63 € |
| 2.277.846 |              23 |       73.440,72 € |
| 2.286.775 |              21 |       84.017,43 € |

Die gesamte Schadenhöhe dieser verwaisten Severity-Datensätze beträgt
788.714,18 €.

Die Prüfung erhält den Status `FAIL`, da die Severity-Datensätze keiner
vorhandenen Police im Frequency-Datensatz zugeordnet werden können.

#### Entscheidung

Die 195 verwaisten Severity-Zeilen bleiben in der Raw-Schicht unverändert
erhalten.

Sie wurden jedoch aus der Curated- und analytischen Claim-Schicht
ausgeschlossen, da keine passende Police im Frequency-Datensatz vorhanden ist.

Die sechs betroffenen `IDpol`-Werte wurden bei der Aufbereitung eindeutig
identifiziert und getrennt behandelt.

Für die analytische Claim-Tabelle `fact_claim` wurden ausschließlich
Severity-Zeilen übernommen, deren `IDpol` im Frequency-Datensatz vorhanden ist.

Dadurch wurden von insgesamt 26.639 Severity-Zeilen genau 26.444
verknüpfbare Claim-Level-Zeilen in die analytische Schicht übernommen.

#### Begründung

Der Frequency-Datensatz stellt die policenbasierte Haupttabelle dar.

Ohne eine passende Frequency-Police fehlen für die Severity-Datensätze unter
anderem die Risikomerkmale, die Exposure-Information und die im
Frequency-Datensatz gespeicherte Schadenanzahl.

Eine Aufnahme dieser Datensätze in den Modellierungsbestand würde deshalb zu
unvollständigen oder nicht nachvollziehbaren Beobachtungen führen.

Eine nachträgliche künstliche Erstellung der fehlenden Frequency-Policen wäre
nicht fachlich begründbar, da die benötigten Policenmerkmale nicht vorliegen.

#### Auswirkungen auf die Modellierung

Die 195 Severity-Zeilen werden weder für das Severity-Modell noch für ein
direktes Pure-Premium-Modell verwendet.

Dadurch werden 788.714,18 € beobachtete Schadenhöhe aus dem modellierbaren
Datenbestand ausgeschlossen.

Dieser Ausschluss ist notwendig, um sicherzustellen, dass jede verwendete
Schadenhöhe eindeutig einer Police mit vollständigen Risikomerkmalen
zugeordnet werden kann.

Die Anzahl der tatsächlich mit Frequency-Policen verknüpfbaren
Severity-Zeilen beträgt daher:

- Gesamte Severity-Zeilen: 26.639
- Verwaiste Severity-Zeilen: 195
- Verknüpfbare Severity-Zeilen: 26.444

### 6. Potenziell doppelte Severity-Datensätze

#### Befund

Im Frequency-Datensatz wurden weder vollständig identische Zeilen noch
mehrfach vorkommende `IDpol`-Werte festgestellt.

- Vollständig doppelte Frequency-Zeilen: 0
- Frequency-Zeilen mit mehrfach vorkommender `IDpol`: 0
- Betroffene unterschiedliche Frequency-Policen: 0

Damit ist die Eindeutigkeit des Policenschlüssels im Frequency-Datensatz
gewährleistet.

Im Severity-Datensatz wurden dagegen 255 zusätzliche Zeilen festgestellt,
bei denen sowohl `IDpol` als auch `ClaimAmount` mit einer vorherigen Zeile
übereinstimmen.

- Potenziell doppelte Severity-Zeilen: 255
- Betroffene `IDpol`-`ClaimAmount`-Gruppen: 241
- Gesamtzahl der Zeilen innerhalb dieser Gruppen: 496

Die Prüfung erhält den Status `WARN`.

#### Entscheidung

Die potenziell doppelten Severity-Zeilen wurden nicht automatisch entfernt.

Da im Severity-Datensatz weder eine eindeutige Schaden-ID noch ein
Schadendatum vorhanden ist, kann nicht zuverlässig entschieden werden,
ob identische Kombinationen aus `IDpol` und `ClaimAmount` tatsächliche
Duplikate oder separate Schadenereignisse mit identischem Betrag darstellen.

Die betroffenen Datensätze bleiben deshalb unverändert erhalten und werden
bei der Aggregation der Schadenhöhen berücksichtigt.

Auch in der analytischen Claim-Schicht wurden die mit einer gültigen
Frequency-Police verknüpfbaren Claim-Level-Zeilen vollständig beibehalten.

Eine mögliche Sensitivitätsanalyse mit alternativer Behandlung dieser
auffälligen Datensätze wird erst im Rahmen der explorativen Analyse
beziehungsweise Modellvalidierung durchgeführt.

#### Begründung

Der Severity-Datensatz enthält keinen eindeutigen Schadenbezeichner, kein
Schadendatum und keine weitere Information, mit der einzelne Schadenereignisse
zweifelsfrei unterschieden werden könnten.

Daher kann nicht festgestellt werden, ob zwei Zeilen mit derselben `IDpol`
und demselben `ClaimAmount` tatsächlich doppelt erfasst wurden oder zwei
unterschiedliche Schäden mit identischer Auszahlung darstellen.

Insbesondere wiederkehrende Beträge wie 1.500,00 €, 1.128,12 € oder
1.204,00 € können standardisierte oder gerundete Zahlungen darstellen.

Eine automatische Entfernung würde deshalb das Risiko bergen, reale Schäden
fälschlicherweise zu löschen.

#### Auswirkungen auf die Modellierung

Die potenziellen Duplikate werden zunächst bei der Aggregation der
Schadenhöhen berücksichtigt.

Während der explorativen Analyse wird geprüft, ob einzelne Policen durch
wiederholte identische Beträge einen ungewöhnlich hohen Gesamtschaden
aufweisen.

Zusätzlich kann eine Sensitivitätsanalyse durchgeführt werden, bei der die
Ergebnisse mit und ohne Zusammenfassung der potenziellen Duplikate verglichen
werden.

Eine endgültige Entfernung erfolgt nur dann, wenn zusätzliche fachliche oder
technische Hinweise einen tatsächlichen Erfassungsfehler belegen.

### 7. Join-Kardinalität zwischen Frequency und Severity

#### Befund

Die Verbindung zwischen dem Frequency- und dem Severity-Datensatz wurde über
den Schlüssel `IDpol` geprüft.

Für die Beziehung wurde eine One-to-Many-Kardinalität erwartet:

- Eine Police darf im Frequency-Datensatz nur einmal vorkommen.
- Eine Police darf im Severity-Datensatz mehrere Schadenzeilen besitzen.

Die Prüfung ergab folgende Werte:

- Frequency-Policen mit mindestens einer passenden Severity-Zeile: 24.944
- Frequency-Policen ohne passende Severity-Zeile: 653.069
- Mit Frequency verknüpfbare Severity-Zeilen: 26.444
- Erwartete Zeilenanzahl nach dem Left Join: 679.513
- Tatsächliche Zeilenanzahl nach dem Left Join: 679.513
- Unerwartete zusätzliche Zeilen: 0
- Frequency-Zeilen mit mehrfach vorkommender `IDpol`: 0

Die Prüfung erhält den Status `PASS`.

#### Entscheidung

Die geprüfte One-to-Many-Beziehung über `IDpol` wurde bei der
Datenaufbereitung berücksichtigt.

Für den policenbasierten Curated-Datensatz wurden die Severity-Zeilen vor
der Verknüpfung nach `IDpol` aggregiert. Dabei wurden je Police die gesamte
Schadenhöhe (`total_claim_amount`) und die Anzahl der vorhandenen
Severity-Zeilen (`claim_record_count`) gebildet.

Anschließend wurde die aggregierte Severity-Tabelle mit dem Frequency-
Datensatz auf Policenebene verknüpft.

Dadurch blieb der Curated-Datensatz bei genau 678.013 Policen und es
entstanden keine doppelten `IDpol`.

Die 195 verwaisten Severity-Zeilen ohne passende Frequency-Police wurden
nicht in diese Verknüpfung übernommen.

Für Claim-Level-Analysen wurde die One-to-Many-Struktur dagegen in der
analytischen Tabelle `fact_claim` erhalten.

#### Begründung

Die höhere Zeilenanzahl nach dem Join stellt keinen Join-Fehler dar.

Einige Policen besitzen mehrere Severity-Zeilen, weil mehrere Schadenereignisse
oder Schadenbeträge zu derselben Police gehören können. Dadurch entstehen bei
einem One-to-Many-Join zusätzliche Zeilen.

Die erwartete und die tatsächliche Zeilenanzahl stimmen vollständig überein.
Es wurden keine unerwarteten Vervielfachungen festgestellt.

Außerdem ist `IDpol` im Frequency-Datensatz eindeutig. Dadurch besteht kein
Risiko einer unkontrollierten Many-to-Many-Verknüpfung.

#### Auswirkungen auf die Modellierung

Für policenbasierte Modelle werden die Severity-Zeilen zunächst nach `IDpol`
aggregiert, bevor sie mit dem Frequency-Datensatz verbunden werden.

Dadurch erhält jede Police wieder genau eine Modellierungszeile.

Für Analysen auf Schadenebene kann die One-to-Many-Struktur dagegen erhalten
bleiben.

Die erfolgreiche Kardinalitätsprüfung bestätigt, dass die spätere Aggregation
und Verknüpfung technisch kontrolliert durchgeführt werden kann und keine
unerwartete Join-Explosion zu erwarten ist.

### 8. Fehlende Werte

#### Befund

Sowohl der Frequency- als auch der Severity-Datensatz wurden vollständig auf
fehlende Werte geprüft.

Die Prüfung ergab:

| Datensatz    | Zeilen mit fehlenden Werten | Status |
| ------------ | --------------------------: | ------ |
| freMTPL2freq |                           0 | PASS   |
| freMTPL2sev  |                           0 | PASS   |

Es wurden in keinem der beiden Datensätze fehlende Werte festgestellt.

#### Entscheidung

Für die beiden Rohdatensätze war keine Missing-Value-Imputation,
Entfernung oder sonstige Behandlung fehlender Zellwerte erforderlich.

Die vorhandenen Werte wurden unverändert in die weiteren
Verarbeitungsschritte übernommen.

Fehlende Schadenhöhen, die erst durch die Verknüpfung von Frequency und
Severity sichtbar werden, wurden davon getrennt behandelt. Für Policen mit
`ClaimNb > 0`, aber ohne passende Severity-Information, wurde kein
Schadenbetrag imputiert. Diese Fälle wurden stattdessen mit
`missing_severity` gekennzeichnet.

#### Begründung

Alle für die Datenqualitätsprüfung vorhandenen Spalten sind vollständig
befüllt.

Eine künstliche Ersetzung oder Ergänzung von Werten ist daher nicht notwendig
und würde keinen zusätzlichen Informationsgewinn bringen.

#### Auswirkungen auf die Modellierung

Die Modelle können die vorhandenen Merkmale grundsätzlich ohne vorherige
Missing-Value-Imputation verwenden.

Die fehlenden Severity-Informationen für 9.116 Policen stellen dabei keinen
klassischen fehlenden Zellwert dar.

Sie entstehen durch nicht vorhandene zugehörige Severity-Datensätze und werden
deshalb separat im Abschnitt zur Frequency-Severity-Konsistenz behandelt.

## Ergebnis der Curated-Aufbereitung

Die beschriebenen Bereinigungsentscheidungen wurden in der Curated-Schicht
technisch umgesetzt.

Der resultierende policenbasierte Curated-Datensatz enthält:

- 678.013 Policen
- 25 Spalten
- 0 doppelte `IDpol`
- 0 Policen mit `Exposure > 1` nach der Bereinigung
- 1.224 Policen mit `exposure_capped = TRUE`
- 9 Policen mit `high_claim_count = TRUE`
- 9.116 Policen mit `missing_severity = TRUE`
- 1 Police mit `claim_count_mismatch = TRUE`

Für schadenfreie Policen mit `ClaimNb = 0` wurde
`total_claim_amount = 0` gesetzt.

Für Policen mit `ClaimNb > 0`, aber ohne vorhandene Severity-Information,
bleibt `total_claim_amount` dagegen NULL beziehungsweise NaN.

Dadurch wird fachlich zwischen „kein Schaden“ und
„Schadenhöhe unbekannt“ unterschieden.

Die Severity-Daten wurden vor der policenbasierten Verknüpfung nach `IDpol`
aggregiert. Dabei wurden je Police die gesamte Schadenhöhe
(`total_claim_amount`) und die Anzahl der vorhandenen Severity-Zeilen
(`claim_record_count`) gebildet.

Von 24.950 unterschiedlichen `IDpol` im Severity-Datensatz konnten
24.944 gültigen Frequency-Policen zugeordnet werden.

Sechs verwaiste Policen mit insgesamt 195 Severity-Zeilen wurden aus der
Curated- und Modeling-Schicht ausgeschlossen.

Für Claim-Level-Analysen stehen 26.444 mit Frequency-Policen verknüpfbare
Severity-Zeilen zur Verfügung.

## Bereinigungs- und Modellierungsentscheidungen

| Befund                                                                 | Status | Entscheidung in der Curated-/Modeling-Schicht                                                                                                                                                                                                            | Begründung                                                                                                                                   |
| ---------------------------------------------------------------------- | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| 1.224 Policen mit`Exposure > 1`                                      | FAIL   | `Exposure` wurde in der Curated-Schicht auf 1,0 begrenzt und mit `exposure_capped` gekennzeichnet                                                                                                                                                    | Die Policen bleiben nutzbar, erhalten aber kein überhöhtes Modellgewicht                                                                    |
| 9 Policen mit`ClaimNb > 4`                                           | WARN   | Die Werte wurden unverändert beibehalten und mit`high_claim_count` gekennzeichnet                                                                                                                                                                     | Hohe Schadenanzahlen sind auffällig, aber nicht nachweislich falsch                                                                          |
| Keine nichtpositiven Schadenhöhen                                     | PASS   | Keine Bereinigung durchgeführt; alle vorhandenen positiven`ClaimAmount`-Werte wurden beibehalten                                                                                                                                                      | Es liegt kein nachweisbarer Datenfehler vor; Großschäden werden später separat analysiert                                                  |
| 9.116 Schadenpolicen ohne Severity-Datensatz                           | FAIL   | Die Policen bleiben für das Frequency-Modell erhalten und wurden mit`missing_severity` gekennzeichnet; unbekannte Schadenhöhen wurden nicht mit null imputiert                                                                                       | Eine beobachtete Schadenhöhe ist nicht vorhanden und darf nicht künstlich ersetzt werden                                                    |
| `IDpol` 4.158.255 mit `ClaimNb = 2`, aber nur einer Severity-Zeile | FAIL   | Die Police bleibt für das Frequency-Modell erhalten und wurde mit`claim_count_mismatch` gekennzeichnet; für die policenbasierte Severity- und direkte Pure-Premium-/Tweedie-Modellierung wird sie nicht als vollständig beobachteter Fall behandelt | Schadenanzahl und vorhandene Severity-Information sind nicht vollständig konsistent                                                          |
| 195 verwaiste Severity-Zeilen aus 6 Policen                            | FAIL   | Die Zeilen bleiben in der Raw-Schicht erhalten, wurden jedoch aus der Curated- und analytischen Claim-Schicht ausgeschlossen                                                                                                                             | Es fehlen die zugehörigen Frequency-Policen und damit die erforderlichen Risikomerkmale                                                      |
| 255 potenziell doppelte Severity-Zeilen                                | WARN   | Die Zeilen wurden nicht automatisch entfernt und werden bei Aggregation und Claim-Level-Analyse beibehalten                                                                                                                                              | Ohne eindeutige Schaden-ID oder Schadendatum kann ein tatsächliches Duplikat nicht sicher nachgewiesen werden                                |
| Keine doppelten`IDpol` im Frequency-Datensatz                        | PASS   | Keine Bereinigung erforderlich                                                                                                                                                                                                                           | Der Policenschlüssel ist eindeutig                                                                                                           |
| Erwartete und tatsächliche Join-Zeilenanzahl identisch                | PASS   | Severity wurde vor dem policenbasierten Join nach`IDpol` aggregiert; die One-to-Many-Struktur bleibt für Claim-Level-Analysen erhalten                                                                                                                | Dadurch bleibt der policenbasierte Curated-Datensatz bei genau einer Zeile pro Police und eine unerwartete Join-Vervielfachung wird vermieden |
| Keine fehlenden Zellwerte in den Rohdatensätzen                       | PASS   | Keine klassische Missing-Value-Imputation erforderlich; durch fehlende Severity-Verknüpfungen entstehende unbekannte Schadenhöhen werden separat über`missing_severity` behandelt                                                                   | Die beiden Ausgangsdatensätze sind auf Zellebene vollständig, die unvollständige Severity-Abdeckung ist dagegen ein referenzielles Problem |

## Modellierungsdatenbestände

Aus den Datenqualitätsprüfungen und der inzwischen umgesetzten
Curated-Aufbereitung ergeben sich unterschiedliche Datenbestände für die
geplanten Modelle und Analysen.

| Modell beziehungsweise Analyse                           |        Verfügbare Datenbasis | Einschränkung                                                                                                                                                                           |
| -------------------------------------------------------- | ----------------------------: | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Frequency-Modell                                         |        bis zu 678.013 Policen | `Exposure > 1` wurde auf 1,0 begrenzt; auffällig hohe Schadenanzahlen bleiben mit `high_claim_count` gekennzeichnet                                                                 |
| Policen mit mindestens einem gemeldeten Schaden          |                34.060 Policen | Stark unausgewogene Zielverteilung; 94,9765 % aller Policen sind schadenfrei                                                                                                             |
| Policen mit mindestens einer vorhandenen Severity-Zeile  |                24.944 Policen | Eine Police weist eine abweichende Schadenanzahl zwischen Frequency und Severity auf                                                                                                     |
| Vollständig konsistente policenbasierte Severity-Daten  |                24.943 Policen | Nur Policen mit vorhandener Schadenhöhe und konsistenter Schadenanzahl                                                                                                                  |
| Claim-Level-Severity-Daten für analytische Auswertungen |                 26.444 Zeilen | 195 verwaiste Severity-Zeilen ohne passende Frequency-Police wurden ausgeschlossen                                                                                                       |
| Direkte Pure-Premium-/Tweedie-Daten                      | auf Basis der Curated-Schicht | Policen mit gemeldetem Schaden, aber unbekannter Schadenhöhe sowie die Police mit`claim_count_mismatch = TRUE` dürfen nicht als vollständig beobachtete Loss-Ziele behandelt werden |

Für das Frequency-Modell kann grundsätzlich die gesamte policenbasierte
Curated-Datenbasis verwendet werden, da die Zielvariable `ClaimNb`
unabhängig von einer vorhandenen Severity-Information vorliegt.

Für das policenbasierte Severity-Modell ist die Datenbasis kleiner. Es werden
nur Policen verwendet, für die eine tatsächlich beobachtete positive
Schadenhöhe vorliegt und deren Schadenanzahl mit den vorhandenen
Severity-Zeilen konsistent ist.

Für direkte Pure-Premium- beziehungsweise Tweedie-Modelle darf insbesondere
nicht angenommen werden, dass eine fehlende Severity-Information einem
Schadenbetrag von null entspricht.

Die Curated-Schicht stellt deshalb die notwendigen DQ-Indikatoren
`missing_severity` und `claim_count_mismatch` bereit, damit diese Fälle in
der späteren Modeling-Schicht gezielt behandelt werden können.

## Schlussfolgerung

Die automatisierten Datenqualitätsprüfungen zeigen, dass die beiden
freMTPL2-Ausgangsdatensätze technisch nutzbar sind, jedoch nicht ohne
fachlich begründete Aufbereitungsentscheidungen direkt für alle geplanten
Modelle verwendet werden können.

Die wichtigste Einschränkung betrifft weiterhin die unvollständige
Severity-Abdeckung. Für 9.116 von 34.060 Policen mit mindestens einem
gemeldeten Schaden liegt keine beobachtete Schadenhöhe vor. Dies entspricht
26,7645 % der Schadenpolicen.

Diese fehlende Information wurde bewusst nicht durch einen Schadenbetrag von
null ersetzt. Dadurch bleibt die fachlich wichtige Unterscheidung zwischen
„kein Schaden“ und „Schadenhöhe unbekannt“ erhalten.

Die wesentlichen Bereinigungsentscheidungen wurden inzwischen technisch in
der Curated-Schicht umgesetzt:

- `Exposure > 1` wurde auf 1,0 begrenzt und mit `exposure_capped`
  gekennzeichnet.
- Auffällig hohe Schadenanzahlen wurden unverändert beibehalten und mit
  `high_claim_count` gekennzeichnet.
- Policen mit gemeldetem Schaden, aber fehlender Severity-Information wurden
  mit `missing_severity` gekennzeichnet.
- Die einzelne Police mit inkonsistenter Schadenanzahl wurde mit
  `claim_count_mismatch` gekennzeichnet.
- Verwaiste Severity-Zeilen wurden aus der Curated- und analytischen
  Claim-Schicht ausgeschlossen.
- Potenziell doppelte Severity-Zeilen wurden mangels eindeutiger
  Schadenidentifikation nicht automatisch entfernt.

Der daraus resultierende policenbasierte Curated-Datensatz umfasst
678.013 Policen und 25 Spalten. Jede `IDpol` kommt genau einmal vor und nach
der Bereinigung existieren keine `Exposure`-Werte größer als 1.

Zusätzlich stehen 26.444 mit gültigen Frequency-Policen verknüpfbare
Claim-Level-Zeilen für weiterführende Severity- und Schadenanalysen zur
Verfügung.

Die aufbereiteten Daten wurden außerdem in ein PostgreSQL-Datenmodell
überführt. Dadurch stehen sowohl policenbasierte als auch claimbasierte
analytische Datenbestände sowie historische Pipeline- und
Datenqualitätsinformationen strukturiert für die weiteren Projektphasen zur
Verfügung.

Alle Rohdaten bleiben unverändert erhalten. Die fachlich begründeten
Bereinigungen und Kennzeichnungen wurden nachvollziehbar in der
Curated-Schicht umgesetzt. Modellabhängige Ausschlüsse erfolgen anschließend
gezielt in der jeweiligen Modeling-Schicht.

Die verbleibenden Auffälligkeiten, insbesondere Großschäden, hohe
Schadenanzahlen und potenziell doppelte Severity-Zeilen, werden in der
explorativen Analyse und späteren Modellvalidierung weiter untersucht.

## Finaler Modellierungs- und Evaluationsstatus

Die ursprünglich definierten Data-Quality-Regeln wurden im weiteren Projektverlauf vollständig in die finale Modellierungs- und Evaluationslogik übernommen.

Die finalen Evaluationspopulationen unterscheiden sich abhängig von der jeweiligen Zielgröße:

| Modell / Analyse          | Finale Holdout-Population | Begründung                                                                                                              |
| ------------------------- | ------------------------: | ------------------------------------------------------------------------------------------------------------------------ |
| Frequency                 |           135.603 Policen | `ClaimNb` ist unabhängig von vorhandener Severity vollständig beobachtbar                                            |
| Severity                  |             4.999 Policen | Nur Policen mit beobachtbarer positiver Schadenhöhe und konsistenter Schadeninformation                                 |
| Tweedie / Loss Evaluation |           133.790 Policen | Schadenfreie Policen bleiben enthalten; Policen mit Schaden, aber fehlender beobachtbarer Severity werden ausgeschlossen |

Für die Severity-Evaluation umfasst der finale Holdout:

- 4.999 Severity-eligible Policen,
- 5.312 beobachtete Schäden,
- 11.055.690,67 € beobachteten Schadenaufwand,
- eine claim-gewichtete beobachtete Severity von 2.081,27 €.

Für die direkte Tweedie-/Loss-Evaluation umfasst der gemeinsame beobachtbare Holdout 133.790 Policen. Darunter befinden sich:

- 128.791 schadenfreie Policen,
- 4.999 Policen mit beobachtbarer positiver Schadenhöhe.

Damit wird weiterhin strikt zwischen:

- `kein Schaden`,
- `Schadenhöhe beobachtbar`,
- und `Schadenhöhe unbekannt`

unterschieden.

### Bedeutung der DQ-Status in Reporting und Power BI

Die Statuswerte `PASS`, `WARN` und `FAIL` dokumentieren Befunde der **Quelldatenprüfung**.

Ein `FAIL` bedeutet daher nicht automatisch, dass der finale Curated-Datensatz technisch fehlerhaft oder für die Modellierung unbrauchbar ist.

Beispielsweise werden:

- `Exposure > 1` in der Curated-Schicht kontrolliert behandelt,
- fehlende Severity-Beobachtungen explizit gekennzeichnet,
- Orphan-Severity-Records aus der analytischen Modellierung ausgeschlossen,
- und Inkonsistenzen zwischen `ClaimNb` und vorhandenen Severity-Records transparent dokumentiert.

Die DQ-Ergebnisse beschreiben damit sowohl die ursprünglichen Datenprobleme als auch die fachlichen Entscheidungen, mit denen diese Probleme in den nachgelagerten Analyse- und Modellierungsschichten behandelt wurden.

### Finaler Status

Die Data-Quality-Schicht bildet die methodische Grundlage der finalen Modellierungsarchitektur.

Insbesondere wurden die DQ-Befunde verwendet, um:

- die zulässigen Modellierungs- und Evaluationspopulationen eindeutig zu definieren,
- fehlende Severity nicht fälschlich als Schadenhöhe null zu interpretieren,
- strikt positive Severity-Ziele für die Gamma-Modellierung sicherzustellen,
- Exposure fachlich kontrolliert zu behandeln,
- und unterschiedliche Beobachtungsuniversen in Frequency-, Severity- und Pure-Premium-Analysen transparent zu kommunizieren.

Die im Bericht dokumentierten Auffälligkeiten sind daher nicht nur explorative Befunde, sondern Bestandteil der finalen Daten- und Modellierungslogik der Plattform.
