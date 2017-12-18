
_Implementation and Analysis of Multi-Carrier Synchronization Techniques_

---

_Recap:_

multi-carrier systems

---

Localized disturbances
======================

![Localized disturbances](images/ofdm_sync_vis_fades.png)

· Data is distributed onto multiple carriers

· Localized errors correctible using FEC

---

Synchronization errors
======================

![Synchronization errors](images/ofdm_sync_vis_shifts.png)

· Synchronization errors affect all carriers

· Can not be corrected by FEC

---

_Recap:_

Schmidl and Cox synchronization

---

Preamble
========

![S&C preamble](diagrams/ofdm_sc_sync.svg)

Twice the same sequence back-to-back

---

Detection
=========

![S&C block diagram](diagrams/sc_detector_blocks.svg)

Averaged autocorrelation for Δt=½T<sub>Preamble</sub>

---

Detection
=========

![S&C calculation](diagrams/sc_calculation_nooff.svg)

---

Detection
=========

![S&C detector output](diagrams/sc_detector_output_nooff.svg)

|x| and arg(x)

---

Δf estimation
=============

![S&C calculation](diagrams/sc_calculation_fqoff.svg)

---

Δf estimation
=============

![Derive df from argx](diagrams/sc_calculation_argtofqoff.svg)

---

Δf estimation
=============

![S&C detector output](diagrams/sc_detector_output_fqoff.svg)

---

_Recap:_

GNU Radio

---

GNU Radio is …
==============

- … a signal processing framework for PCs
- … usable via a graphical interface
- … usable via Python and C++

---

_Implementation_

A fast S&C implementation for GNU Radio

---

XFDMSync
========

![S&C blocks](diagrams/annotated_gnuradio_companion_detectors.svg)

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

Output
======

![S&C block output](diagrams/annotated_grc_detectors_plot.svg)

---

_Performace evaluation_

---

Synchronization in time
=======================

Compared to …

- … a power based method …
- … a frequency sweep based method …


… when disturbed by …

- … an AWGN channel.
- … a frequency shift.
- … a frequency selective channel.


---

<img src="diagrams/results_time_sync_nois_min.svg" style="height: 75vh; width: 80vw;" />

AWGN

---

<img src="diagrams/results_time_sync_freq.svg" style="height: 75vh; width: 80vw;" />

Frequency shift

---

<img src="diagrams/results_time_sync_chan.svg" style="height: 75vh; width: 80vw;" />

Frequency selective channel

---

Synchronization in frequency
============================

![HW components](images/hw_chan_setup.jpg)

Hardware test where the LO frequency is estimated

---

Synchronization in frequency
============================

![CFO Result](diagrams/time_sync_hw_sloped.svg)

Frequency offset to phase mapping is not unique

---

Synchronization in frequency
============================

![CFO Result](diagrams/time_sync_hw_horiz.svg)

Residual CFO error is small

---

Throughput
==========

![Benchmark setup](diagrams/cpu_bm_dut.svg)

Count the number of samples processed by S&C blocks …

---

Throughput
==========

![Reference setup](diagrams/cpu_bm_baseline.svg)

… and compare them to a baseline figure

---

Throughput
==========

![Throughput table](diagrams/speed_cmp_tab.svg)

Usable for WiFi on a Desktop PC

---

The software sources are released under the terms of the<br/>
GNU GPLv3 license:

[github.com/hnez/XFDMSync](https://github.com/hnez/XFDMSync)

<div style="border-top: 1px solid rgba(255, 255, 255, 0.17); margin-top: 1em; padding-top: 1em;"></div>

This presentation and thesis are released under the terms of the<br/>
GNU FDLv1.3:

[github.com/hnez/XFDMSync-Report](https://github.com/hnez/XFDMSync-Report)

<div style="border-top: 1px solid rgba(255, 255, 255, 0.17); margin-top: 1em; padding-top: 1em;"></div>

The presentation slides are available online at:

[tut.zerforscht.de/ba](https://tut.zerforscht.de/ba/)
