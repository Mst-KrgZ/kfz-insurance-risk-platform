
# Business Understanding

## 1. Project Background

Die Kfz-Versicherung gehört zu den datenintensiven Bereichen der Versicherungswirtschaft. Für eine fundierte Risikobewertung ist es wichtig, nicht nur zu untersuchen, ob Schäden auftreten, sondern auch, wie häufig sie auftreten und welche Schadenhöhe zu erwarten ist. Fahrzeug-, Fahrer- und Regionalmerkmale können dabei mit unterschiedlichen Risikomustern verbunden sein.

Im Rahmen dieses Abschlussprojekts wird ein prototypisches Decision-Support-System entwickelt, das historische Kfz-Versicherungsdaten verarbeitet und die annualisierten erwarteten Schadenkosten für unterschiedliche Versicherungsprofile schätzt. Dazu werden Schadenfrequenz und Schadenhöhe getrennt modelliert und anschließend zur Pure Premium zusammengeführt. Die Ergebnisse sollen Underwriting und Portfoliosteuerung datenbasiert unterstützen, ohne automatische Annahme-, Ablehnungs- oder Tarifentscheidungen zu treffen.

## 2. Business Problem

Versicherungsportfolios bestehen aus vielen unterschiedlichen Risikoprofilen. Fahrermerkmale, Fahrzeugeigenschaften, regionale Faktoren und die jeweilige Versicherungsdauer können mit der Anzahl und der Höhe von Schäden zusammenhängen.

Eine reine Betrachtung der gesamten Schadenkosten reicht für eine differenzierte Risikobewertung nicht aus. Es muss getrennt analysiert werden,

- wie häufig Schäden auftreten,
- wie hoch einzelne Schäden ausfallen,
- und wie lange eine Police tatsächlich unter Risiko stand.

Ohne die Berücksichtigung der Exposure können Policen mit sehr unterschiedlichen Beobachtungszeiträumen fälschlicherweise gleich behandelt werden. Ziel ist daher, die erwartete Schadenfrequenz und die erwartete Schadenhöhe methodisch sauber zu schätzen und daraus annualisierte erwartete Schadenkosten abzuleiten.

## 3. Central Business Question

Welche annualisierten Schadenkosten sind für unterschiedliche Versicherungsprofile statistisch zu erwarten, und wie können Underwriting und Portfoliosteuerung durch diese Informationen datenbasiert unterstützt werden?

## 4. Target Users

Die primären Zielgruppen des Prototyps sind:

- Mitarbeitende im Underwriting, die Risikoprofile strukturiert beurteilen,
- Verantwortliche in der Portfoliosteuerung, die Risikokonzentrationen und Segmentunterschiede analysieren,
- Data- und Business-Analysten, die Datenqualität, Modellgüte und Portfolioentwicklungen überwachen.

Das System unterstützt diese Nutzergruppen mit statistischen Schätzungen, Risikosegmenten und nachvollziehbaren Analysen. Die endgültige fachliche Entscheidung verbleibt jedoch bei den verantwortlichen Mitarbeitenden.

## 5. Project Objectives

Das Projekt verfolgt folgende Ziele:

- die beiden OpenML-Datensätze reproduzierbar zu beschaffen und unverändert in einer Raw-Data-Schicht zu speichern,
- relevante Datenqualitätsprobleme systematisch zu prüfen und nachvollziehbar zu dokumentieren,
- Schadenfrequenz und Schadenhöhe getrennt mit geeigneten statistischen Modellen zu schätzen,
- aus beiden Modellkomponenten eine annualisierte Pure Premium abzuleiten,
- die Modellgüte mithilfe geeigneter Deviance-Metriken und einer Risk-Decile-Kalibrierung zu bewerten,
- Risikoprofile und Portfoliostrukturen verständlich in Power BI darzustellen,
- die Ergebnisse über eine prototypische FastAPI-Schnittstelle bereitzustellen,
- und einen transparenten, reproduzierbaren Decision-Support-Prototyp zu entwickeln.

## 6. Expected Outputs

Am Ende des Projekts sollen folgende Ergebnisse vorliegen:

- ein dokumentierter und reproduzierbarer Datenbeschaffungsprozess,
- unveränderte Raw-Daten sowie aufbereitete Analyse- und Modelldaten,
- ein PostgreSQL-Datenmodell für Datenqualität, Policen, Schäden und Modellvorhersagen,
- ein Exposure-gewichtetes Modell für die Schadenfrequenz,
- ein ClaimNb-gewichtetes Modell für die Schadenhöhe,
- annualisierte Pure-Premium-Schätzungen auf Policenebene,
- eine nachvollziehbare Bewertung der Modellgüte und Portfoliokalibrierung,
- definierte Risikosegmente und Handlungshinweise zur Entscheidungsunterstützung,
- ein Power-BI-Dashboard mit Portfolio-, Risiko- und Modellansichten,
- eine prototypische FastAPI-Schnittstelle,
- sowie eine vollständige Projektdokumentation mit README, Data Dictionary, Data Quality Report und Model Card.

## 7. Project Scope

Der Projektumfang umfasst die Entwicklung eines End-to-End-Analytics-Prototyps für die datenbasierte Risikobewertung in der Kfz-Versicherung.

Zum Projektumfang gehören:

- die Beschaffung und unveränderte Speicherung der beiden OpenML-Datensätze,
- die Prüfung und Dokumentation relevanter Datenqualitätsprobleme,
- die Aggregation der Schadendaten auf Policenebene,
- der Aufbau eines analytischen Datenmodells in PostgreSQL,
- die geschäftsorientierte explorative Datenanalyse,
- die getrennte Modellierung von Schadenfrequenz und Schadenhöhe,
- die Berechnung der annualisierten Pure Premium,
- die Bewertung und Kalibrierung der Modelle,
- die Segmentierung von Risikoprofilen,
- sowie die Bereitstellung der Ergebnisse über Power BI und eine prototypische FastAPI-Schnittstelle.

Der entwickelte Prototyp dient ausschließlich der analytischen Entscheidungsunterstützung.

## 8. Out of Scope

Folgende Punkte sind ausdrücklich nicht Bestandteil des Projekts:

- die Berechnung einer Endkundenprämie oder eines Versicherungstarifs,
- die Aussage, dass einzelne Kunden falsch bepreist sind,
- die Berechnung von Gewinn, Verlust oder Combined Ratio,
- die Prognose eines zukünftigen Kalenderjahres,
- automatische Annahme-, Ablehnungs- oder Kündigungsentscheidungen,
- der Ersatz menschlicher Underwriting-Entscheidungen,
- eine produktive Echtzeit-Anwendung,
- sowie der Einsatz von RAG, Chatbots oder AI-Agenten.

Die Pure Premium stellt ausschließlich die statistisch erwarteten, annualisierten Schadenkosten dar. Sie enthält keine Verwaltungs-, Vertriebs-, Sicherheits- oder Gewinnaufschläge und darf daher nicht mit einer Kundenprämie gleichgesetzt werden.

## 9. Success Criteria

Das Projekt gilt als erfolgreich, wenn die folgenden Kriterien erfüllt sind:

- die beiden Quelldatensätze wurden nachvollziehbar beschafft und unverändert gespeichert,
- zentrale Datenqualitätsprobleme wurden systematisch geprüft und dokumentiert,
- die Policen- und Schadendaten wurden methodisch korrekt auf Policenebene zusammengeführt,
- Schadenfrequenz und Schadenhöhe wurden mit geeigneten, gewichteten Modellen geschätzt,
- die annualisierte Pure Premium wurde korrekt berechnet,
- die Modellgüte wurde mit geeigneten Deviance-Metriken und einer Risk-Decile-Kalibrierung bewertet,
- die Portfolioergebnisse wurden unter Berücksichtigung der Exposure aggregiert,
- die Ergebnisse sind in PostgreSQL gespeichert und in Power BI verständlich dargestellt,
- die wichtigsten Funktionen sind reproduzierbar und nachvollziehbar dokumentiert,
- und die Grenzen sowie zulässigen Einsatzbereiche des Prototyps werden transparent kommuniziert.


## 10. Data Sources

Für das Projekt werden zwei öffentlich verfügbare Datensätze aus OpenML verwendet:

### 10.1 freMTPL2freq

- OpenML Dataset ID: `41214`
- Beobachtungsebene: eine Zeile pro Versicherungspolice
- Inhalt: Schadenanzahl, Exposure sowie Fahrer-, Fahrzeug- und Regionalmerkmale
- Verwendung: Analyse und Modellierung der Schadenfrequenz

Der Datensatz enthält unter anderem die Variablen `IDpol`, `ClaimNb`, `Exposure`, `Area`, `VehPower`, `VehAge`, `DrivAge`, `BonusMalus`, `VehBrand`, `VehGas`, `Density` und `Region`.

### 10.2 freMTPL2sev

- OpenML Dataset ID: `41215`
- Beobachtungsebene: eine Zeile pro Schadenereignis
- Inhalt: Policen-ID und Schadenbetrag
- Verwendung: Analyse und Modellierung der Schadenhöhe

Der Datensatz enthält die Variablen `IDpol` und `ClaimAmount`. Da eine Police mehrere Schadenereignisse aufweisen kann, wird dieser Datensatz vor der Verknüpfung mit der Policentabelle auf Policenebene aggregiert.

### 10.3 Verbindung der Datensätze

Die beiden Datensätze werden über die gemeinsame Variable `IDpol` miteinander verbunden. Vor dem Join werden die Schadenereignisse pro Police aggregiert:

- `total_claim_amount`: Summe aller Schadenbeträge einer Police
- `claim_record_count`: Anzahl der Schadenereignisse einer Police

Anschließend wird die aggregierte Schadentabelle mit der Policentabelle über einen Left Join verbunden, damit auch schadenfreie Policen im analytischen Datenbestand erhalten bleiben.

### 10.4 Datenbeschaffung und Raw-Data-Schicht

Die Datenbeschaffung ist grundsätzlich über die OpenML-API vorgesehen. Während der initialen Einrichtung lieferte die OpenML-Metadaten-API wiederholt einen HTTP-504-Fehler. Daher wurden die unveränderten Parquet-Dateien vorübergehend direkt vom offiziellen statischen OpenML-Datenserver geladen.

Die Herkunft, Dateigröße und SHA-256-Prüfsumme der Raw-Dateien werden in `data/raw/source_manifest.json` dokumentiert. Die Raw-Dateien bleiben unverändert und werden nicht in das GitHub-Repository aufgenommen.
