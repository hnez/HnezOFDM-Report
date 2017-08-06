#!/usr/bin/env python3

import matplotlib.pyplot as plt
import commpy as cp
import numpy as np

rand= np.random.RandomState(0)

IMPRESLEN= 1000
SAMP_RATE= 100
SYMPERIOD= 1

imp_res_t, imp_res= cp.filters.rcosfilter(
    IMPRESLEN, 0.6, SYMPERIOD, SAMP_RATE
)

target= list()

for i in range(20):
    seq= np.zeros(IMPRESLEN)
    seq[::SAMP_RATE]= rand.choice((-1, 1), IMPRESLEN//SAMP_RATE)

    full= np.convolve(seq, imp_res)
    start= (len(full) - 3*SAMP_RATE)//2
    end=  (len(full) + 3*SAMP_RATE)//2

    crop= full[start:end]

    crop+= 0.01 * rand.randn(len(crop))

    target.append(crop)

for tgt in target:
    plt.plot(
        np.linspace(0, 0.1, len(tgt)),
        tgt, 'k'
    )

plt.axvline(x=0.05,  linewidth=0.7)
plt.axvline(x=0.033, linewidth=0.7)
plt.axvline(x=0.067, linewidth=0.7)

plt.savefig('eye_diagram.pdf')
