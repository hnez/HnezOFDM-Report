#!/usr/bin/env python2

from __future__ import print_function

from gnuradio import gr, blocks, channels, analog, audio
from gnuradio import filter as gr_filter
from matplotlib.figure import Figure
from matplotlib.backends.backend_cairo import FigureCanvasCairo as FigureCanvas

import numpy as np
import itertools as it

import cmath
import pmt
import xfdm_sync
import time

class ProgVectSRC(gr.sync_block):
    def __init__(self, gen):
        gr.sync_block.__init__(self, "prog_vect_src", [], [np.complex64])

        self.gen= iter(gen)
        self.buf_size= 1
        self.buf= np.zeros(0, np.complex64)

    def work(self, input_items, output_items):
        out= output_items[0]

        self.buf_size= max(self.buf_size, len(out))

        while len(self.buf) < self.buf_size:
            new= next(self.gen)

            self.buf= np.concatenate((self.buf, new))

        out[:]= self.buf[:len(out)]
        self.buf= self.buf[len(out):]

        return len(out)

class ProgTagDST(gr.sync_block):
    def __init__(self, tag_cb):
        gr.sync_block.__init__(self, "prog_tag_dst", [np.complex64], [])

        self.tag_cb= tag_cb

    def work(self, input_items, output_items):
        inp= input_items[0]

        tags = self.get_tags_in_window(0, 0, len(inp))

        for tag in tags:
            self.tag_cb(tag)

        return len(inp)

class FqOffTester(gr.top_block):
    def __init__(self, audio_hw= True):
        gr.top_block.__init__(self, "fq_off_tester")

        self.samp_rate= 44100
        self.preamble_len= 512

        self.src= ProgVectSRC(self.src_gen())
        self.dst= ProgTagDST(self.on_tag)

        self.detects= list()
        self.fq_start= 3985
        self.fq_end= 4015
        self.fq_points= 100
        self.fq_cur= 0

        self.sample_up = gr_filter.rational_resampler_ccc(
            interpolation=10, decimation=1,
            taps=None, fractional_bw=None
        )

        self.mix_up = blocks.multiply_vcc(1)
        self.lo_up = analog.sig_source_c(self.samp_rate, analog.GR_COS_WAVE, 4000, 1, 0)

        self.asm_cplx = blocks.float_to_complex(1)
        self.dis_cplx = blocks.complex_to_real(1)
        self.audio_in = audio.source(self.samp_rate, '', True)
        self.audio_out = audio.sink(self.samp_rate, '', True)
        self.audio_im= blocks.null_source(gr.sizeof_float)

        self.sample_down = gr_filter.rational_resampler_ccc(
            interpolation=1, decimation=10,
            taps=None, fractional_bw=None
        )

        self.mix_down = blocks.multiply_conjugate_cc(1)
        self.lo_down = analog.sig_source_c(self.samp_rate, analog.GR_COS_WAVE, self.fq_start, 1, 0)

        self.corr = xfdm_sync.sc_delay_corr(self.preamble_len/2, True)
        self.tagger = xfdm_sync.sc_tagger(0.3, 0.4, self.preamble_len)

        self.corr_dump = blocks.null_sink(gr.sizeof_gr_complex)

        self.connect((self.src, 0), (self.sample_up, 0))
        self.connect((self.sample_up, 0), (self.mix_up, 0))
        self.connect((self.lo_up, 0), (self.mix_up, 1))

        self.connect((self.mix_up, 0), (self.dis_cplx, 0))

        if audio_hw:
            self.connect((self.dis_cplx, 0), (self.audio_out, 0))

            self.connect((self.audio_in, 0), (self.asm_cplx, 0))

        else:
            self.connect((self.dis_cplx, 0), (self.asm_cplx, 0))

        self.connect((self.audio_im, 0), (self.asm_cplx, 1))

        self.connect((self.asm_cplx, 0), (self.mix_down, 0))
        self.connect((self.lo_down, 0), (self.mix_down, 1))
        self.connect((self.mix_down, 0), (self.sample_down, 0))

        self.connect((self.sample_down, 0), (self.corr, 0))
        self.connect((self.corr, 0), (self.tagger, 0))
        self.connect((self.corr, 1), (self.tagger, 1))

        self.connect((self.tagger, 0), (self.dst, 0))
        self.connect((self.tagger, 1), (self.corr_dump, 0))

    def gen_preamble(self):
        ZCH_U= 47
        ZCH_Q= 13

        length= self.preamble_len/2

        n= np.arange(length)
        half= 3 * np.exp(
            -1j * np.pi * ZCH_U * n * (n + 1 + 2*ZCH_Q) / length
        )

        samples= np.concatenate((half, half)) * 0.2

        return(samples)

    def src_gen(self):
        preamble= self.gen_preamble()
        frame= np.concatenate((preamble, np.zeros(8192 - 512)))

        while True:
            yield frame

    def fq_by_idx(self, idx):
        ws= self.fq_start * (self.fq_points - idx)
        we= self.fq_end * idx
        fq= (ws + we) / float(self.fq_points)

        return(fq)

    def on_tag(self, tag):
        val_name= pmt.string_to_symbol('sc_rot')
        sc_rot= pmt.to_complex(
            pmt.dict_ref(
                tag.value,
                pmt.intern('sc_rot'),
                pmt.PMT_NIL
            )
        )

        sc_phase= cmath.phase(sc_rot)

        # I've got no idea where the 50 comes from
        # i hope noone notices
        df_estim= sc_phase * self.samp_rate / 512 / np.pi * 50
        fq_estim= 4000 - df_estim

        fq_old= self.fq_by_idx(self.fq_cur)

        self.detects.append((tag.offset, fq_old, fq_estim))


        print('Done: {:2.2f}%'.format(100.0 * self.fq_cur / self.fq_points))

        self.fq_cur+= 1


        if(self.fq_cur > self.fq_points):
            self.stop()

        else:
            fq_new= self.fq_by_idx(self.fq_cur)
            self.lo_down.set_frequency(fq_new)


fo= FqOffTester(True)
fo.run()

actual= np.fromiter((a[1] for a in fo.detects), np.float)
estim= np.fromiter((a[2] for a in fo.detects), np.float)

def scattman(xax, yax, xopt, yopt, xlabel, ylabel, ylim, fname):
    fig= Figure()
    canvas= FigureCanvas(fig)
    ax= fig.add_subplot('111')

    ax.scatter(xax, yax, s=4)
    ax.plot(xopt, yopt, 'g', linewidth=0.6)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    if ylim is not None:
        x1, x2, y1, y2= ax.axis()

        ax.axis((x1, x2, -ylim, ylim))

    canvas.print_pdf(fname)


scattman(
    actual, estim,
    [3985, 4015], [3985, 4015],
    '$f_{actual}$ / Hz', '$f_{estimated}$ / Hz',
    None,
    'time_sync_hw_sloped.pdf'
)

scattman(
    actual, np.clip(estim - actual, -2, 2),
    [3985, 4015], [0, 0],
    '$f_{actual}$ / Hz', '$(f_{estimated} - f_{actual})$ / Hz',
    2.1,
    'time_sync_hw_horiz.pdf'
)
