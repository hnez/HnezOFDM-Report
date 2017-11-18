_Implementation and Analysis of Multi-Carrier Synchronization Techniques_

---

Multi-Carrier systems
=====================

Goal:

- Improve reliability of communications over frequency-selective
  channels

Approach:

- Split data into multiple narrow-band sub-streams
- Use coding to mitigate losses in these sub-streams

---

_OFDM …_

---

… from 10000 feet


![Aerial Photo](images/ofdm_from_1000fts.jpg)

[Source: Google maps](https://maps.google.de/)

---

Waterfall diagram
=================

FFTing Chunks of the input stream is essentially the
same thing a waterfall diagram does

![Waterfall diagram](images/waterfall.png)

---

TD/FD Grid
----------

![Selecting Sample points](images/ofdm_sync_vis_okay.png)

---

Frequency selective channel
---------------------------

![Fq fading](images/ofdm_sync_vis_fdfade.png)

---

Interfering burst
-----------------

![Td fading](images/ofdm_sync_vis_tdfade.png)

---

Frequency offset
----------------

![Fq offset](images/ofdm_sync_vis_fdshift.png)

---

Time offset
-----------

![Td offset](images/ofdm_sync_vis_tdshift.png)

---

Non-linear channel
------------------

![Non-linear](images/ofdm_sync_vis_nonlinear.png)

---

Simple synchronization
----------------------

![Burst sync](images/sync_burst.png)

---

Schmidl & Cox - preamble
------------------------

![S&C preamble](diagrams/ofdm_sc_sync.svg)

---

Schmidl & Cox - detector
------------------------

![S&C block diagram](diagrams/sc_detector_blocks.svg)

---

Schmidl & Cox - detector
------------------------

![S&C detector output](diagrams/sc_detector_output_nooff.svg)

|x| and arg(x)

---

![S&C calculation](diagrams/sc_calculation_nooff.svg)

---

![S&C calculation](diagrams/sc_calculation_fqoff.svg)

S&C detector with frequency offset

---

![S&C detector output](diagrams/sc_detector_output_fqoff.svg)

|x| and arg(x)

with frequency offset

---

![Derive df from argx](diagrams/sc_calculation_argtofqoff.svg)

Calculating the frequency offset from the
S&C phase

---

![Corrected frequency offset](images/ofdm_sync_vis_fqshift_corrected.png)

---

_GnuRadio_

---

GnuRadio …
==========

- … provides a set of digital signal processing components
- … lets an user combine components to form a signal processing chain
- … lets developers write own components while abstracting away
  the stream processing and multithreading

---

GnuRadio companion
==================

![GnuRadio companion UI](diagrams/annotated_gnuradio_companion.svg)

---

Using GnuRadio
==============

GnuRadio provides different levels of abstraction/programming interfaces:

- Graphical block-diagram based interface<br/>
  → <span style="color: rgb(161, 206, 76);">very intuitive</span>
- Python programming interface<br/>
  → <span style="color: rgb(161, 206, 76);">more flexible than the graphical interface</span>
- C++ interface<br/>
  → <span style="color: rgb(161, 206, 76);">can be a lot faster than python code</span>

---

_The Project_

---

<span style="color: rgb(234, 58, 58);">_Problem:_</span>

- A Schmidl & Cox implemented using the graphical interface is too
  slow to detect WiFi frames on an usual Desktop computer

<span style="color: rgb(161, 206, 76);">_Solution:_</span>

- Integrate the functionality of the discrete blocks into a
  single, highly optimized block

---

XFDMSync - usage
================

![S&C blocks](diagrams/annotated_gnuradio_companion_detectors.svg)

Processing is still split into logic blocks to allow …

- … tapping of debug information
- … replacing of blocks with custom ones

---

XFDMSync - output
=================

![S&C block output](diagrams/annotated_grc_detectors_plot.svg)

The default configuration adds a tag to the sample stream
whenever a S&C sequence is detected

---

Correlator
==========

![S&C correlator](diagrams/sc_correlator_blocks.svg)

Performs the raw S&C calculation and outputs a correlation
value normalized to the mean input power

---

Tagger
======

![S&C tagger](diagrams/sc_tagger_hysteresis.svg)

Adds a tag to the sample stream when set thresholds
are crossed

---

XCorr Tagger
============

![Xcorr tagger](diagrams/xcorr_tagger_blocks.svg)

Relocates incomming tags based on cross-correlation
of stored preamble and received preamble

---

_What i have learned_

---

- OFDM<br/>
  → usecases / requirements / limitations
- Multicarrier synchronization<br/>
  → requirements / implementations / tradeoffs
- GnuRadio<br/>
  → internal structure / writing blocks in Python & C++ /
  vectorizing calculations

---

_Next steps_

---

- Performance evaluation
- Code cleanup for public use

---

The software sources are released under the terms of the<br/>
GNU GPLv3 license:

[github.com/hnez/XFDMSync](https://github.com/hnez/XFDMSync)

<div style="border-top: 1px solid rgba(255, 255, 255, 0.17); margin-top: 1em; padding-top: 1em;"></div>

This presentation is released under the terms of the<br/>
GNU FDLv1.3:

[github.com/hnez/XFDMSync-Report](https://github.com/hnez/XFDMSync-Report)
