#!/usr/bin/env python2

from __future__ import print_function

from gnuradio import gr, blocks, channels, analog, audio
from gnuradio import filter as gr_filter

import matplotlib.pyplot as plt
import matplotlib.animation as animation

import Queue as queue
import numpy as np
import itertools as it

import cmath
import pmt
import xfdm_sync
import time

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

class VeloPlot(object):
    def __init__(self):
        self.queue= queue.Queue()
        self.last= 0

    def put(self, value):
        self.queue.put(value)

    def show(self):
        fig= plt.figure()
        ax= fig.add_subplot(1,1,1)
        plot= ax.plot(np.arange(512), np.zeros(512))[0]
        ax.set_ylim((-1, 1))

        def prepare_frame(f_idx):
            y= plot.get_ydata()

            if not self.queue.empty():
                self.last= self.queue.get()

            print(self.last)

            y[:-1]= y[1:]
            y[-1]= self.last

            plot.set_ydata(y)

        anim = animation.FuncAnimation(fig, prepare_frame, repeat=False, interval=50)
        plt.show()

class Doppler(gr.top_block):
    def __init__(self, velo):
        gr.top_block.__init__(self, "fq_off_tester")

        self.velo= velo
        self.samp_rate= 44100
        self.preamble_len= 512

        self.dst= ProgTagDST(self.on_tag)

        self.asm_cplx = blocks.float_to_complex(1)
        self.audio_in = audio.source(self.samp_rate, '', True)
        self.audio_im= blocks.null_source(gr.sizeof_float)

        self.sample_down = gr_filter.rational_resampler_ccc(
            interpolation=1, decimation=10,
            taps=None, fractional_bw=None
        )

        self.mix_down = blocks.multiply_conjugate_cc(1)
        self.lo_down = analog.sig_source_c(self.samp_rate, analog.GR_COS_WAVE, 4000, 1, 0)

        self.corr = xfdm_sync.sc_delay_corr(self.preamble_len/2, True)
        self.tagger = xfdm_sync.sc_tagger(0.5, 0.6, self.preamble_len)

        self.corr_dump = blocks.null_sink(gr.sizeof_gr_complex)

        # Connections
        self.connect((self.audio_in, 0), (self.asm_cplx, 0))
        self.connect((self.audio_im, 0), (self.asm_cplx, 1))

        self.connect((self.asm_cplx, 0), (self.mix_down, 0))
        self.connect((self.lo_down, 0), (self.mix_down, 1))
        self.connect((self.mix_down, 0), (self.sample_down, 0))

        self.connect((self.sample_down, 0), (self.corr, 0))
        self.connect((self.corr, 0), (self.tagger, 0))
        self.connect((self.corr, 1), (self.tagger, 1))

        self.connect((self.tagger, 0), (self.dst, 0))
        self.connect((self.tagger, 1), (self.corr_dump, 0))

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
        df_estim= sc_phase * self.samp_rate / 512.0 / np.pi * 50
        fq_estim= 4000.0 + df_estim

        vel= (1.0 - 4000.0/fq_estim) * 340

        self.velo.put(vel)
        print(vel)

def main():
    velo= VeloPlot()
    do= Doppler(velo)
    do.start()

    velo.show()

if __name__ == '__main__':
    main()
