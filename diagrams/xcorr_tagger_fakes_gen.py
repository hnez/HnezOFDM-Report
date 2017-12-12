#!/usr/bin/env python3

from matplotlib.figure import Figure
from matplotlib.backends.backend_cairo import FigureCanvasCairo as FigureCanvas
import commpy as cp
import numpy as np

rand= np.random.RandomState(0)

PADDEDLEN= 1024
SIGLEN= 512
SCLEN= 128

def print_pdf(name, data):
    fig= Figure()
    canvas= FigureCanvas(fig)
    ax= fig.add_subplot('111')

    sl= len(data)

    ax.axis('off')

    ax.plot(
        np.linspace(-sl/2, sl/2, sl),
        data, 'k'
    )

    canvas.print_pdf(name)


sync_half= rand.randn(SCLEN//2)
sync_seq= np.concatenate((sync_half, sync_half))

bg_noise= 0.2 * rand.randn(PADDEDLEN)

sync_in_noise= np.copy(bg_noise)
sync_in_noise[(PADDEDLEN-SCLEN)//2:(PADDEDLEN+SCLEN)//2]+= sync_seq

print_pdf('xcorr_tagger_extract.pdf', sync_in_noise)

sync_in_noise= sync_in_noise[(PADDEDLEN-SIGLEN)//2:(PADDEDLEN+SIGLEN)//2]

print_pdf('xcorr_tagger_extract_cropped.pdf', sync_in_noise)

sync_in_noise_padded= np.zeros(PADDEDLEN)
sync_in_noise_padded[(PADDEDLEN-SIGLEN)//2:(PADDEDLEN+SIGLEN)//2]= sync_in_noise

print_pdf('xcorr_tagger_extract_padded.pdf', sync_in_noise_padded)

sync_padded= np.zeros(PADDEDLEN)
sync_padded[(PADDEDLEN-SCLEN)//2:(PADDEDLEN+SCLEN)//2]= sync_seq

print_pdf('xcorr_tagger_sync_padded.pdf', sync_padded)

sc_corr= abs(sync_in_noise_padded[128:] * sync_in_noise_padded[:-128].conj())
sc= np.convolve(sc_corr, np.ones(128))
sc_pad= np.concatenate((np.zeros(512), sc, np.zeros(512)))
print_pdf('xcorr_sc.pdf', sc_pad)

find_max= np.correlate(sync_seq, sync_in_noise)
find_max_padded= np.zeros(PADDEDLEN)

fml= len(find_max)
fmlp= len(find_max_padded)

find_max_padded[(fmlp-fml)//2:(fmlp-fml)//2+fml]= find_max

print_pdf('xcorr_tagger_find_max.pdf', find_max_padded)

fake_sc= np.linspace(0, 1, SCLEN//2)
fake_sc= np.concatenate((fake_sc, fake_sc[::-1]))
fake_sc_padded= np.zeros(PADDEDLEN)
fake_sc_padded[(PADDEDLEN-SCLEN)//2:(PADDEDLEN+SCLEN)//2]= fake_sc

find_max_masked= find_max_padded * fake_sc_padded

print_pdf('xcorr_tagger_find_max_masked.pdf', find_max_masked)
