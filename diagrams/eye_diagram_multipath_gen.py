#!/usr/bin/env python3

from matplotlib.figure import Figure
from matplotlib.backends.backend_cairo import FigureCanvasCairo as FigureCanvas
import commpy as cp
import numpy as np

IMPRESLEN= 1000
SAMP_RATE= 100
SYMPERIOD= 1
MPDELAYS= (
    (90, 0.1),
    (90, 0.3),
    (90, 0.5),
    (90, 0.7)
)

imp_res_t, imp_res= cp.filters.rcosfilter(
    IMPRESLEN, 0.6, SYMPERIOD, SAMP_RATE
)

for (delay, mag) in MPDELAYS:
    rand= np.random.RandomState(1)
    fig= Figure()
    canvas= FigureCanvas(fig)
    ax= fig.add_subplot('111')

    ax.set_title('Δt={}T, a={}'.format(delay/SAMP_RATE, mag))

    target= list()

    for i in range(64):
        seq= np.zeros(IMPRESLEN)
        seq[::SAMP_RATE]= rand.choice((-1, 1), IMPRESLEN//SAMP_RATE)

        full= np.convolve(seq, imp_res)
        start= (len(full) - 3*SAMP_RATE)//2
        end=  (len(full) + 3*SAMP_RATE)//2

        full[:-delay]+= mag * full[delay:]
        full/= 1 + mag

        crop= full[start:end]

        crop+= 0.01 * rand.randn(len(crop))

        target.append(crop)

    for tgt in target:
        ax.plot(
            np.linspace(0, 0.1, len(tgt)),
            tgt,
            'b'
        )

    canvas.print_pdf('eye_diagram_multipath_{}_{}m.pdf'.format(delay,int(mag*1000)))
