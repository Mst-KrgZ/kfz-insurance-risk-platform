
# Statusbericht – Woche 4

**Projekt:** Kfz Insurance Risk & Pure Premium Intelligence Platform
**Berichtszeitraum:** Technisches Arbeitspaket Woche 4, vorgezogen bearbeitet vom 19.08.2026 bis 20.08.2026
**Stand:** 20.08.2026
**Gesamtarbeitszeit:** Wird nach Abschluss der Zeiterfassung ergänzt

## 1. Aktueller Projektstand

In der vierten Projektphase wurde die geschäftsorientierte explorative
Datenanalyse abgeschlossen und anschließend der geplante kritische
End-to-End-Kontrollpunkt umgesetzt.

Der aufbereitete policenbasierte Datensatz mit 678.013 Policen und
25 Spalten wurde im Notebook `03_eda.ipynb` systematisch untersucht.
Dabei wurden zentrale Risikomerkmale, Schadenhäufigkeiten,
Schadenhöhen, Exposure-Strukturen und beobachtete Pure-Premium-Werte
analysiert.

Zusätzlich wurde ein einfacher Exposure-gewichteter Poisson-Checkpoint
entwickelt. Die Modellierungsdaten wurden direkt aus PostgreSQL geladen,
in Python verarbeitet und zur Erzeugung von Policy-Level-Vorhersagen
verwendet.

Die erzeugten Vorhersagen wurden anschließend wieder in PostgreSQL
gespeichert und über eine analytische View in Power BI eingebunden.

Damit konnte die vollständige technische Kette

`PostgreSQL → Python → Poisson-Modell → SQL-Vorhersagen → Power BI`

erfolgreich durchgängig validiert werden.

Das verwendete Poisson-Modell dient ausschließlich als technischer
Checkpoint. Die finale Modellierung und Modellbewertung mit Train-/Test-Split,
Deviance-Metriken und Kalibrierung wurde noch nicht begonnen.

## 2. Abgeschlossene Arbeiten

- Explorative Datenanalyse in `notebooks/03_eda.ipynb` durchgeführt
- Struktur, Datentypen, fehlende Werte und Duplikate des Curated-Datensatzes geprüft
- Fahrer-Altersgruppen hinsichtlich Schadenhäufigkeit analysiert
- Fahrzeugalter und Fahrzeugleistung untersucht
- Bonus-Malus-Segmente hinsichtlich Schadenhäufigkeit analysiert
- Unterschiede nach `Area`, `Region` und `Density` untersucht
- Schadenhäufigkeit nach Kraftstoffart verglichen
- Schadenhöhenverteilung auf logarithmischer Skala analysiert
- Ausgeprägten rechten Tail der Schadenhöhen dokumentiert
- Beobachteten Pure Premium nach relevanten Risikosegmenten untersucht
- Zentrale Portfoliokennzahlen berechnet und dokumentiert
- Anteil schadenfreier Policen mit 94,98 % bestätigt
- 34.060 Policen mit mindestens einem gemeldeten Schaden dokumentiert
- 26.639 Severity-Zeilen und eine Matching-Quote von 99,27 % bestätigt
- Severity-Abdeckung bei Schadenpolicen mit 73,24 % dokumentiert
- Spearman-Korrelationsanalyse für ausgewählte numerische Risikomerkmale durchgeführt
- Verteilung der Schadenanzahl analysiert und starke Konzentration bei `ClaimNb = 0` bestätigt
- Exposure-Verteilung untersucht und Bedeutung für die spätere Modellierung dokumentiert
- Notebook vollständig mit einem neuen Kernel über `Run All` validiert
- Checkpoint-Modell in `src/models/checkpoint_poisson.py` entwickelt
- Modellierungsdaten aus `vw_policy_risk_base` direkt aus PostgreSQL geladen
- Sieben ausgewählte numerische und kategorische Risikomerkmale für den Checkpoint verwendet
- Annualisierte Schadenfrequenz als `ClaimNb / Exposure` vorbereitet
- `Exposure` als Sample Weight im Poisson-Modell berücksichtigt
- Portfolioweite Schadenfrequenz von ca. 0,10074 validiert
- Policy-Level-Vorhersagen für alle 678.013 Policen erzeugt
- PostgreSQL-Tabelle `policy_frequency_predictions` erstellt
- Zusammengesetzten Primärschlüssel aus `idpol` und `model_name` eingerichtet
- Vorhersagen mit PostgreSQL `COPY` in die Datenbank geladen
- 678.013 gespeicherte Prediction-Zeilen auf SQL-Ebene bestätigt
- Analytische View `vw_frequency_prediction_analysis` erstellt
- Actual Claims und Predicted Claims auf PostgreSQL-Ebene validiert
- Power-BI-Checkpoint `powerbi/week4_checkpoint.pbix` erstellt
- DAX-Measures für Exposure, Actual Claims, Predicted Claims,
  Actual Frequency und Predicted Frequency erstellt
- Beobachtete und prognostizierte Schadenfrequenz nach Gebietsklasse
  in Power BI visualisiert
- Kritischen End-to-End-Kontrollpunkt erfolgreich abgeschlossen

## 3. Technische Probleme und Lösungen

### Unterschied zwischen einfacher und Exposure-gewichteter Schadenfrequenz

Die einfache arithmetische Mittelung von `ClaimNb / Exposure` ergab eine
durch sehr kleine Exposure-Werte stark beeinflusste durchschnittliche
Schadenfrequenz.

**Lösung:**
Für die Portfoliofrequenz wurde die fachlich korrekte Berechnung

`SUM(ClaimNb) / SUM(Exposure)`

verwendet.

Zusätzlich wurde bestätigt, dass die mit `Exposure` gewichtete mittlere
annualisierte Schadenfrequenz exakt mit dieser Portfoliofrequenz
übereinstimmt.

### Speicherung mehrerer Modellversionen

Die Prediction-Tabelle war zunächst mit `idpol` als alleinigen Primärschlüssel
definiert. Dadurch hätte pro Police nur eine einzige Modellvorhersage
gespeichert werden können.

**Lösung:**
Der Primärschlüssel wurde auf die Kombination aus `idpol` und `model_name`
umgestellt.

Dadurch können später mehrere Modellversionen parallel gespeichert und
miteinander verglichen werden.

### Abgrenzung des Checkpoint-Modells von der finalen Modellbewertung

Das einfache Poisson-Modell wurde auf dem vollständigen vorhandenen
Frequency-Datenbestand trainiert und die Vorhersagen anschließend auf
demselben Bestand erzeugt.

Die aggregierten vorhergesagten Schadenanzahlen liegen deshalb sehr nahe
an den beobachteten Gesamtwerten. Dies stellt jedoch keine unabhängige
Bewertung der Modellgüte dar.

**Lösung:**
Das Modell wird ausdrücklich nur als technischer End-to-End-Checkpoint
verwendet.

Die finale Modellbewertung erfolgt erst im nächsten Arbeitspaket mit einem
einheitlichen Train-/Test-Split, geeigneten Deviance-Metriken und einer
Risk-Decile-Kalibrierung.

## 4. Ergebnisse und fachliche Erkenntnisse

Die EDA zeigt deutliche Unterschiede in der beobachteten Schadenhäufigkeit
zwischen verschiedenen Risikosegmenten.

Besonders auffällig sind junge Fahrer, höhere Bonus-Malus-Werte sowie dichter
besiedelte Gebiete.

Die Schadenhöhen sind stark rechtsschief verteilt. Die meisten Schäden liegen
im niedrigen bis mittleren Bereich, während wenige Großschäden einen
ausgeprägten rechten Tail erzeugen.

Die Schadenanzahl ist stark auf null konzentriert. Von insgesamt
678.013 Policen weisen 643.953 keinen gemeldeten Schaden auf.

Die Exposure-Werte unterscheiden sich deutlich zwischen den Policen.
Daher muss die jeweilige Beobachtungsdauer bei der späteren
Frequency-Modellierung ausdrücklich berücksichtigt werden.

Die Korrelationsanalyse zeigt überwiegend geringe paarweise Zusammenhänge
zwischen den numerischen Risikomerkmalen. Eine stärkere negative Beziehung
besteht insbesondere zwischen Fahrer-Alter und Bonus-Malus.

Für den technischen Poisson-Checkpoint wurden folgende aggregierte Werte
bestätigt:

- Gesamtzahl Policen: 678.013
- Gesamt-Exposure: ca. 358.360,11
- Beobachtete Schadenanzahl: 36.102
- Beobachtete Portfoliofrequenz: ca. 0,100742
- Prognostizierte Schadenanzahl: ca. 36.098,70
- Prognostizierte Portfoliofrequenz: ca. 0,100733

Diese Werte dienen ausschließlich der technischen Plausibilitätsprüfung
des Checkpoint-Modells und stellen noch keine unabhängige
Modellgütebewertung dar.

## 5. Offene Aufgaben

- Einheitlichen Train-/Test-Split auf Policy-Ebene erstellen
- Finales Poisson-Frequency-Modell entwickeln
- Frequency-Modell mit geeigneten Deviance-Metriken bewerten
- Gamma-Severity-Modell auf dem dafür gültigen Datenbestand entwickeln
- Severity-Modell mit geeigneten Metriken bewerten
- Prognostizierte Frequency und Severity zur annualisierten Pure Premium kombinieren
- Risk-Decile-Kalibrierung durchführen
- Portfolioebene auf beobachtete und prognostizierte Werte prüfen
- Finale `model_predictions`-Tabelle erstellen und befüllen
- Modellvergleich und weitere Validierung vorbereiten

## 6. Nächste Schritte

Im nächsten technischen Arbeitspaket beginnt die Hauptmodellierungsphase.

Zunächst wird ein einheitlicher Train-/Test-Split auf Policy-Ebene erstellt.
Darauf aufbauend wird das finale Poisson-Frequency-Modell trainiert und
mithilfe geeigneter Metriken bewertet.

Anschließend wird für Policen mit gültiger und vollständig beobachteter
Schadenhöhe ein Gamma-Severity-Modell entwickelt.

Die prognostizierte Schadenfrequenz und die prognostizierte Schadenhöhe
werden danach zu einer annualisierten Pure Premium zusammengeführt.

Abschließend werden die Modelle mit Deviance-Metriken, Portfolioaggregaten
und einer Risk-Decile-Kalibrierung überprüft.

## 7. Zusammenfassung

Die geschäftsorientierte explorative Datenanalyse wurde erfolgreich
abgeschlossen.

Neben der Untersuchung zentraler Risikomerkmale, Schadenhöhen,
Exposure-Strukturen und Pure-Premium-Segmente wurde der geplante
End-to-End-Kontrollpunkt vollständig umgesetzt.

Daten konnten aus PostgreSQL in Python geladen, mit einem einfachen
Exposure-gewichteten Poisson-Modell verarbeitet, auf Policenebene
prognostiziert, wieder in PostgreSQL gespeichert und anschließend in
Power BI visualisiert werden.

Damit ist das technische Arbeitspaket Woche 4 abgeschlossen und die
End-to-End-Architektur für die folgende Hauptmodellierungsphase erfolgreich
validiert.
