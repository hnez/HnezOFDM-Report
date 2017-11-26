from __future__ import print_function

from gnuradio import gr, blocks, channels, analog, audio
from gnuradio import filter as gr_filter

import numpy as np
import itertools as it

import cmath
import pmt
import xfdm_sync
import time

def gen_preamble(preamble_len):
    ZCH_U= 47
    ZCH_Q= 13

    length= preamble_len/2

    n= np.arange(length)
    half= 3 * np.exp(
        -1j * np.pi * ZCH_U * n * (n + 1 + 2*ZCH_Q) / length
    )

    samples= np.concatenate((half, half))

    return(samples)

def cplx_randn(length):
    mag= np.random.randn(length)
    ph= 2 * np.pi * np.random.rand(length)

    return mag * np.exp(1j * ph)

class CountingSource(gr.sync_block):
    def __init__(self):
        gr.sync_block.__init__(self, "counting_source", [], [np.complex64])

        preamble= gen_preamble(512)

        sig= cplx_randn(262144) * 0.5

        sig[19000:19512]+= preamble
        sig[41000:41512]+= preamble
        sig[75000:75512]+= preamble
        sig[97000:97512]+= preamble
        sig[130000:130512]+= preamble
        sig[170000:170512]+= preamble
        sig[200000:200512]+= preamble
        sig[230000:230512]+= preamble

        self.sig= sig
        self.buf_pos= 0

        self.sample_num= 0
        self.start_time= time.time()

    def work(self, input_items, output_items):
        out= output_items[0]

        if len(out) + self.buf_pos > len(self.sig):
            self.buf_pos= 0

        out[:]= self.sig[self.buf_pos:self.buf_pos + len(out)]

        self.buf_pos+= len(out)
        self.sample_num+= len(out)

        dt= time.time() - self.start_time

        if dt > 60:
            print('Processed {} samples in {} seconds ({} Samples per Second)'.format(
                self.sample_num, dt, self.sample_num / dt
            ))

            self.start_time+= dt
            self.sample_num= 0

        return len(out)


class Reference(gr.top_block):
    def __init__(self):
        gr.top_block.__init__(self, "reference")

        self.csrc= CountingSource()
        self.corr_dump = blocks.null_sink(gr.sizeof_gr_complex)
        self.pass_dump = blocks.null_sink(gr.sizeof_gr_complex)

        self.connect((self.csrc, 0), (self.corr_dump, 0))
        self.connect((self.csrc, 0), (self.pass_dump, 0))

class Benchmark(gr.top_block):
    def __init__(self):
        gr.top_block.__init__(self, "benchmark")

        preamble_len= 512

        self.csrc= CountingSource()

        self.corr = xfdm_sync.sc_delay_corr(preamble_len/2, True)
        self.tagger = xfdm_sync.sc_tagger(0.5, 0.8, preamble_len)

        self.corr_dump = blocks.null_sink(gr.sizeof_gr_complex)
        self.pass_dump = blocks.null_sink(gr.sizeof_gr_complex)

        self.connect((self.csrc, 0), (self.corr, 0))

        self.connect((self.corr, 0), (self.tagger, 0))
        self.connect((self.corr, 1), (self.tagger, 1))

        self.connect((self.tagger, 0), (self.pass_dump, 0))
        self.connect((self.tagger, 1), (self.corr_dump, 0))

ref= Reference()
bm= Benchmark()
