---
title: XFDMSync final presentation notes
lang: de-DE
...

Folie 1
=======

Habe mich mit der Synchronisation in Mehrträgersystemen beschäftigt.

---

Folie 2
=======

Dieser Vortrag ist eine Fortsetzung des Zwischenvortrags.
Die grundlegenden Punkte sollen noch mal wiederholt werden.

Was sind Mehrträgersysteme?

Daten werden auf mehrere Unterträger mit leicht unterschiedlicher
Trägerfrequenz aufgeteilt.

---

Folie 3
=======

Störungen wie Frequenzfading betreffen nur einzelne Träger
und sind zumindest theoretisch durch clevere
Forward error correction korrigierbar.

---

Folie 4
=======

Kommt es aber zu Fehlern bei der Zeit/Frequenzsynchronisation
sind alle Träger betroffen und gehen kaputt.

Die FEC kann in dem Fall nicht mehr helfen.

Bei Frequenzoffsets verlieren die Träger Orthogonalität
und interferrieren.

Bei Zeitoffsets werden benachbarte OFDM-Symbole vermischt.
Das ist in der Realität weniger kritisch, dank Cyclic Prefix.

---

Folie 5
=======

Wiederholung zu Schmidl und Cox.

S&C haben ein Synchronisationsverfahren vorgestellt, dass sowohl
in Zeit als auch in der Frequenz synchronisation zulässt.

---

Folie 6
=======

Dazu wird am Sender eine Synchronisationssequenz eingebracht,
die aus zwei gleichen Hälften besteht.

Ansonsten gibt es viele Freiheiten beim Design der Preamble.

Eingenschaften, die man haben wollen kann sind z.B.:

- Niedrige Autokorrelation für Zeitverschiebungen ungleich null
- Niedriges Peak to Average Leistungsverteilung
- Gesamtlänge entsprechend der OFDM-Symbollänge

In den Versuchen zur BA wurden diese Kriterien durch Verwendung
einer Zadoff-Chu Sequenz erfüllt.

---

Folie 7
=======

Detektiert wird die Sequenz durch Konj. Komplexe Multiplikation mit
der der zeitverzögerten Version von sich selbst
und Mittelung über ein rechteckigs Fenster.

*Vielleicht Bild auf Tafel*

    | SC + SC |  OFDM   |  OFDM   |
         | SC + SC |  OFDM   |  OFDM   |
         +----+
          Summe

    -----------------------------------> t

---

Folie 8
=======

Dadurch, dass die verzögerte Version des Rauschens
nicht mit der unversögerten korreliert, die Sync-Sequenz aber
sehr stark wird der Rauschanteil weggemittelt.

---

Folie 9
=======

Wenn man das Verfahren über eine Synchronisationssequenz im Rauschen
gleiten lässt dann sieht man in der Amplitude einen deutlichen Peak.
Die Phase ist, wenn es nur Rauschen und keinen Frequenzunterschied gibt
gleich null.

Was ist, wenn es einen Frequenzunterschied gibt?

---

Folie 10
========

Dann ist die Phase am Ausgang abhängig vom Frequenzunterschied.
Und nicht zeitabgängig.

---

Folie 11
========

Man kann einen Frequenzunterschied also aus der Phase
am Ausgang abschätzen.

Durch Verwendung der Phase ist das ganze aber nicht unbedingt eindeutig.

---

Folie 12
========

So sieht das ganze aus, wenn man Rauschen und Frequenzoffset hat.

---

Folie 13
========

Wiederholung: was ist GNU Radio

---

Folie 13
========

GNU Radio ist ein framework um DSP Blöcke zu schreiben und
diese Blöcke dann zu Programmen zu kombinieren.

---

Folie 14
========

GNU Radio kann man über verschiedene Interfaces nutzen.
Am bekanntesten ist das grafische Interface GNU Radio Companion,
da kann man Verarbeitungsschritte einfach zusammenklicken.

Flexibler ist es Python zu nutzen. Da kann man auch eigene
Blöcke schreiben.

Wenn die Blöcke auch noch schnell sein sollen, dann kann man
sie in C++ schreiben.

---

Folie 15
========

Und das habe ich gemacht.

Schmidl und Cox nehmen und es in C++ implementieren.
Dabei z.B. SIMD-instructions nutzen um es flott zu bekommen.

---

Folie 16
========

Das Ergebnis ist XFDMSync, eine GNU Radio Block-Sammlung zur Mehträgersynchonisation.

Will man XFDMSync nutzen, dann nutzt man wahrscheinlich mindestens zwei Blöcke …

---

Folie 17
========

… zu einen den Schmidl und Cox correlator.

Der führt die vorher besprochene Verzögerung, Multiplikation und
Mittelung durch.
Außerdem normalisiert er auf die Eingangsleistung um die Festlegung
der Erkennungsparameter zu vereinfachen.

---

Folie 18
========

Und den S&C Tagger.

Der betrachtet den Betrag der Korrelation aus dem Correlator block
und setzt eine Annotation an das Ausgangssample bei dem der Anfang
der Preamble erwartet wird.

Dabei setzt er genau einen Tag zwischen zwei Hysteresepunkte.

---

Folie 19
========

Am Ausgang sieht das dann etwa so aus.

Eingekreist ist der Tag.
Der enthält auch noch weiter Informationen, wie z.B.
die Phase der Korrelation zur Schätzung der Differenzfrequenz.

---

Folie 20
========

Jetzt stellt sich die Frage wie gut das ganze performed.

Drei Aspekte wurden geprüft:

- Wie genau ist die Zeitsynchronisation, wenn verschiedene
  Störungen auftreten
- Wie genau ist die Frequenzsynchronisation
- Mit welcher Samplerate wird die Implementierung fertig?

---

Folie 21
========

Zuerst die Zeitsynchronisation.

Dafür wurden drei Implementierungen mit gleichen Regeln getestet.

- Zum einen Schmidl & Cox
- Dann ein Verfahren bei dem Leistungsburst von einer Stille-
  Sequenz gefolgt wird.
  *Bild malen*
  Die Energie in zwei Detektionsfenstern wird verglichen
  und darauf synchronisiert.
- Und eine frequenzssweep basierte Methode.
  Die Sync- Sequenz besteht aus einem Frequenzssweep.
  Am Empfänger wird der durch eine umgekehrte Sweepfolge
  entspreizt. Das ergibt konstante Frequenzen. Also
  konstante Phasenunterschiede. Und die werden zur
  Erkennung genutzt.

Getestet wird über drei Arten von Kanälen.

- AWGN-Kanal Rauschen mit verschiedenen Intensitäten wird
  überlagert
- Ein Frequenzshift
- Einen frequenzselektiven Kanal

---

Folie 22
========

Schmidl und Cox, sowie das Leistungsbasierte Verfahren
kommen gut mit Rauschen zurecht.

Das Frequenzsweep-Verfahren versagt.

---

Folie 23
========

Frequenzshifts hatten in den Simulationen keinen Einfluss auf
das Ergebnis.

Das macht auch Sinn, weil keines der Verfahren zu Detektion die
absolute Frequenzinformation nutzt und die Simulation eine
zyklische Frequenzdrehung macht.

---

Folie 24
========

Die Kanäle im Frequenzselektiven Kanaltest sind zunehmend
feindlich konstruiert.

Der erste Kanal ist komplett flach.

Der zweite Kanal ist einem Kanalmodell für Räume nachempfunden.

Die anderen sind einfach nur designed um fies zu sein.

Was nicht Schmidl und Cox ist versagt hier kläglich.

Warum das so ist kann man sich zumindest beim Leistungsbasierten
Verfahren gut vorstellen.

*Auf Tafelbild zeigen wie die Burst-Phase dann in die Stille-Phase leckt*

---

Folie 25
========

Der nächste Test wurde mit Hardware durchgeführt.

Es sollte die Genauigkeit der Frequenzoffset-Schätzung
gemessen werden.
Das können die naiven Algorithmen gar nicht erst.
Deshalb wird hier nur S&C getestet.

Weil keine SDR-Sender zur Hand waren mit Audio-Hardware.

Preamblen wurden mit etwa vier Kilohertz Bandbreite auf einen
4kHz Träger aufmoduliert und dann mit einem Lautsprecher abgespielt.

Auf der anderen Seite eines Raumes wurde das dann mit einem Mikrophon aufgenommen.
Weil kein echtes Mikrophon zur Hand war wurde dafür ein Kopfhörer am
Mikrophoneingang missbraucht.

Dann wurde mit einem LO zwischen 15Hz unter 4kHz und 15Hz über 4kHz
runtergemischt und die LO-Frequenz durch Schmidl & Cox geschätzt.

---

Folie 26
========

Trägt man tatsächliche LO-Frequenz und von S&C geschätzte LO-Frequenz
übereinander auf entsteht so ein Diagramm.

Die Punkte sind die geschätzte LO-Frequenz. Die Linie ist die
theoretisch perfekte Schätzung.

Man sieht sofort, dass die Schätzung nur in bestimmten
Grenzen eindeutig ist durch die Verwendung der Phase.

---

Folie 27
========

Guckt man sich den eindeutigen Bereich an
und schaut ihn genauer an, dann ist der Restfehler recht klein.
Im Bereich von zehntel Hz.

Dabei muss man beachten, dass ich mich während der Messung im
Raum befunden habe. Reflexionen können also Gedopplershiftet worden sein.

---

Folie 28
========

Dass S&C gut performed ist eine bekannte Sache.

Die bisherigen Tests haben nicht wirklich meine Implementierung
getestet sondern den Algortithmus an sich.

Dieser Test testet die Implementierung.
Genauer die maximal erreichbare Samplerate.

Dazu wurde ein Block implementiert, der die Samples pro
Zeit zählt, die er ausgibt.

Dieser wurde an die S&C-Blöcke angeschlossen und im reinen
Simulationsbetrieb getestet. Die Verarbeitungsgeschwindigkeit
war also nur durch die CPU begrenzt. Nicht durch
Sende-/Empfangshardware.

---

Folie 29
========

Um sicherzustellen, dass nicht eine andere GNU Radio komponente
die Verarbeitung bremst wurde auch noch ein baseline-test
durchgeführt ohne S&C komponenten.

---

Folie 30
========

Ergebnis waren auf recht schneller Desktop-Hardware etwa
120 Megasamples pro Sekunde und auf einem low-power Laptop
etwa 20 Megasamples pro Sekunde.

In beiden Fällen lag die Baseline-rate deutlich höher.
Der Test wurde also wie gewollt durch die S&C blöcke gebremst.

---

Folie 31
========

Während der benchmark test läuft sieht man in der
Prozessübersicht auch, dass durch S&C Komponenten zur zwei
Prozessorkerne genutzt werden.

Durch mehr parallelisierung könnte man mehr Kerne nutzen
und dadurch möglicherweise noch die Samplerate erhöhen.

Andererseits sind alle verbleibenden Kerne noch für
andere Berechnungen verfügbar, was vorteilhaft sein kann.

---

Folie 32
========

Fragen?
