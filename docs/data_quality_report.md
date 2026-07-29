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

Die Datensätze werden in der Raw-Schicht unverändert beibehalten.

In der späteren Curated- beziehungsweise Modeling-Schicht werden
`Exposure`-Werte größer als 1 auf maximal 1,0 begrenzt.

Zusätzlich wird eine Indikatorspalte wie `exposure_capped` erstellt, damit
nachvollziehbar bleibt, bei welchen Policen eine Begrenzung durchgeführt
wurde.

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

Die neun betroffenen Policen werden nicht entfernt und ihre `ClaimNb`-Werte
werden nicht verändert.

In der Curated- beziehungsweise Modeling-Schicht wird eine zusätzliche
Indikatorspalte wie `high_claim_count` erstellt.

Die Prüfung erhält deshalb den Status `WARN` und nicht `FAIL`.

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

Sie werden jedoch aus dem Trainingsdatensatz für das policenbasierte
Severity-Modell ausgeschlossen, da keine beobachtete Schadenhöhe vorhanden
ist.

Auch der Datensatz mit `IDpol` 4.158.255 wird aufgrund der abweichenden
Schadenanzahl nicht ohne weitere Prüfung für das policenbasierte
Severity-Modell verwendet.

Für ein direktes Pure-Premium- beziehungsweise Tweedie-Modell werden diese
inkonsistenten Policen ebenfalls nicht automatisch mit einem Schadenbetrag
von null versehen.

Eine solche Ersetzung würde fälschlicherweise bedeuten, dass kein finanzieller
Schaden entstanden ist, obwohl im Frequency-Datensatz mindestens ein Schaden
gemeldet wurde.

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

Die 195 Datensätze bleiben in der Raw-Schicht unverändert erhalten.

Sie werden jedoch aus allen Curated-, Join- und Modeling-Datensätzen
ausgeschlossen, die eine gültige Zuordnung zum Frequency-Datensatz
voraussetzen.

Die sechs betroffenen `IDpol`-Werte werden zusätzlich als
Datenqualitätsbefund dokumentiert.

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

Die potenziell doppelten Severity-Zeilen werden nicht automatisch entfernt.

Sie bleiben sowohl in der Raw-Schicht als auch zunächst im weiteren
Analysebestand erhalten.

In der Curated-Schicht werden die betroffenen Zeilen beziehungsweise Gruppen
mit einem Merkmal wie `potential_duplicate` gekennzeichnet.

Vor einer möglichen Bereinigung wird ihr Einfluss auf aggregierte
Schadenanzahlen und Schadenhöhen gesondert untersucht.

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

Die vorgesehene One-to-Many-Verknüpfung über `IDpol` kann für die spätere
Datenaufbereitung verwendet werden.

Der Join wird weiterhin mit dem Frequency-Datensatz als linker Haupttabelle
durchgeführt.

Verwaiste Severity-Datensätze ohne passende Frequency-Police werden vor der
Erstellung des Modeling-Datensatzes ausgeschlossen.

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

Es ist keine Imputation, Entfernung oder sonstige Behandlung fehlender Werte
erforderlich.

Die Datensätze werden hinsichtlich fehlender Werte unverändert in die weiteren
Verarbeitungsschritte übernommen.

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


## Bereinigungs- und Modellierungsentscheidungen

| Befund                                                                 | Status | Entscheidung in der Curated-/Modeling-Schicht                                                              | Begründung                                                                              |
| ---------------------------------------------------------------------- | ------ | ---------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| 1.224 Policen mit`Exposure > 1`                                      | FAIL   | `Exposure` auf 1,0 begrenzen und mit `exposure_capped` kennzeichnen                                    | Die Policen bleiben nutzbar, erhalten aber kein überhöhtes Modellgewicht               |
| 9 Policen mit`ClaimNb > 4`                                           | WARN   | Werte beibehalten und mit`high_claim_count` kennzeichnen                                                 | Hohe Schadenanzahlen sind auffällig, aber nicht nachweislich falsch                     |
| Keine nichtpositiven Schadenhöhen                                     | PASS   | Keine Bereinigung erforderlich                                                                             | Alle vorhandenen`ClaimAmount`-Werte sind positiv                                       |
| 9.116 Schadenpolicen ohne Severity-Datensatz                           | FAIL   | Im Frequency-Modell beibehalten, aus Severity- und direktem Pure-Premium-Training ausschließen            | Eine beobachtete Schadenhöhe ist nicht vorhanden und darf nicht mit null ersetzt werden |
| `IDpol` 4.158.255 mit `ClaimNb = 2`, aber nur einer Severity-Zeile | FAIL   | Für Frequency verwendbar, für policenbasierte Severity-Modellierung zunächst ausschließen              | Schadenanzahl und vorhandene Schadenhöhen sind nicht vollständig konsistent            |
| 195 verwaiste Severity-Zeilen aus 6 Policen                            | FAIL   | Aus Curated-, Join- und Modeling-Datensätzen ausschließen                                                | Es fehlen die zugehörigen Frequency-Policen und Risikomerkmale                          |
| 255 potenziell doppelte Severity-Zeilen                                | WARN   | Nicht automatisch löschen; mit`potential_duplicate` kennzeichnen und Sensitivitätsanalyse durchführen | Ohne Schaden-ID oder Schadendatum ist ein tatsächliches Duplikat nicht nachweisbar      |
| Keine doppelten`IDpol` im Frequency-Datensatz                        | PASS   | Keine Bereinigung erforderlich                                                                             | Der Policenschlüssel ist eindeutig                                                      |
| Erwartete und tatsächliche Join-Zeilenanzahl identisch                | PASS   | One-to-Many-Join über`IDpol` verwenden                                                                  | Es wurde keine unerwartete Join-Vervielfachung festgestellt                              |
| Keine fehlenden Zellwerte                                              | PASS   | Keine Missing-Value-Imputation erforderlich                                                                | Beide Ausgangsdatensätze sind auf Zellebene vollständig                                |

## Modellierungsdatenbestände

Aus den Datenqualitätsprüfungen ergeben sich unterschiedliche Datenbestände
für die geplanten Modelle.

| Modell beziehungsweise Analyse                          |                       Verfügbare Datenbasis | Einschränkung                                                                                                     |
| ------------------------------------------------------- | -------------------------------------------: | ------------------------------------------------------------------------------------------------------------------ |
| Frequency-Modell                                        |                       bis zu 678.013 Policen | `Exposure > 1` wird in der Modeling-Schicht begrenzt                                                             |
| Policen mit mindestens einem Schaden                    |                               34.060 Policen | Stark unausgewogene Zielverteilung                                                                                 |
| Policen mit mindestens einer Severity-Zeile             |                               24.944 Policen | Eine Police weist eine abweichende Schadenanzahl auf                                                               |
| Vollständig konsistente policenbasierte Severity-Daten |                               24.943 Policen | Nur Policen mit übereinstimmender Schadenanzahl und vorhandener Schadenhöhe                                      |
| Verknüpfbare Schadenzeilen auf Claim-Ebene             |                                26.444 Zeilen | 195 verwaiste Severity-Zeilen ausgeschlossen                                                                       |
| Direkte Pure-Premium-/Tweedie-Daten                     | Nach Erstellung des bereinigten Loss-Targets | Policen mit gemeldetem Schaden, aber unbekannter Schadenhöhe dürfen nicht als Schadenhöhe null behandelt werden |

## Schlussfolgerung

Die automatisierten Prüfungen zeigen, dass die beiden freMTPL2-Datensätze
technisch verwendbar sind, jedoch nicht ohne fachlich begründete
Aufbereitungsentscheidungen direkt für alle Modelle eingesetzt werden können.

Besonders relevant ist die unvollständige Severity-Abdeckung: Für 26,7645 %
der Policen mit mindestens einem gemeldeten Schaden liegt keine beobachtete
Schadenhöhe vor.

Die Datenbasis für das Severity- und Pure-Premium-Modell ist daher kleiner als
die Datenbasis für das Frequency-Modell. Diese Einschränkung wird bei der
Modellbildung, Validierung und Interpretation ausdrücklich berücksichtigt.

Alle Rohdaten bleiben unverändert erhalten. Sämtliche Ausschlüsse,
Begrenzungen und Kennzeichnungen werden nachvollziehbar in einer späteren
Curated- beziehungsweise Modeling-Schicht durchgeführt.
