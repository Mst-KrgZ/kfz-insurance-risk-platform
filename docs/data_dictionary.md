
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
