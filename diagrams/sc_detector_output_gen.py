#!/usr/bin/env python3

from matplotlib.figure import Figure
from matplotlib.backends.backend_cairo import FigureCanvasCairo as FigureCanvas
import commpy as cp
import numpy as np

rand= np.random.RandomState(0)

SIGLEN= 4096
SCLEN= 512
CPLEN= 128

def cplx_randn(length):
    mag= rand.randn(length)
    ph= 2 * np.pi * rand.rand(length)

    return mag * np.exp(1j * ph)

signal= 0.9 * cplx_randn(SIGLEN)
sc_half_seq= cplx_randn(SCLEN)
sc_seq= np.concatenate((sc_half_seq[-CPLEN:], sc_half_seq, sc_half_seq))


start= (len(signal) - len(sc_seq)) // 2
end= start + len(sc_seq)

signal[start:end]+= sc_seq

for (fqname, fqoff) in (('nooff', 0), ('fqoff', 0.01)):
    df= np.exp(1j * np.linspace(0, fqoff * SIGLEN, len(signal)))
    fqadj= signal * df

    detection= fqadj[SCLEN:] * fqadj[:-SCLEN].conj()
    detection= np.convolve(detection, np.ones(SCLEN) / SCLEN, mode='valid')

    for (name, src) in (('abs', abs(detection)), ('arg', np.angle(detection))):
        fig= Figure()
        canvas= FigureCanvas(fig)
        ax= fig.add_subplot('111')

        ax.plot(
            np.arange(len(src)),
            src, 'b'
        )

        canvas.print_pdf('sc_detector_output_{}_{}.pdf'.format(fqname, name))
