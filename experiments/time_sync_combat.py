#!/usr/bin/env python2

from __future__ import print_function

from gnuradio import gr, blocks, channels

import matplotlib.pyplot as plt
import numpy as np
import itertools as it
import operator as op

import xfdm_sync

def cplx_randn(length):
    mag= np.random.randn(length)
    ph= 2 * np.pi * np.random.rand(length)

    return mag * np.exp(1j * ph)

class DUTBurstSilence(gr.hier_block2):
    def __init__(self, preamble_length):
        gr.hier_block2.__init__(
            self, "dut_burst_silence",
            gr.io_signature(1, 1, gr.sizeof_gr_complex),
            gr.io_signature(2, 2, gr.sizeof_gr_complex)
        )

        self.preamble_length= preamble_length

        # Blocks
        self.corr = xfdm_sync.burstsilence_corr(preamble_length)
        self.tagger = xfdm_sync.sc_tagger(50, 200, preamble_length)

        # Connections
        self.connect((self, 0), (self.corr, 0))

        self.connect((self.corr, 0), (self.tagger, 0))
        self.connect((self.corr, 1), (self.tagger, 1))

        self.connect((self.tagger, 0), (self, 0))
        self.connect((self.tagger, 1), (self, 1))

    def gen_preamble(self):
        burst= cplx_randn(self.preamble_length/2)
        silence= np.zeros(self.preamble_length/2)

        return(np.concatenate((burst, silence)))

class DUTFreqSweep(gr.hier_block2):
    def __init__(self, preamble_length):
        gr.hier_block2.__init__(
            self, "dut_freq_sweep",
            gr.io_signature(1, 1, gr.sizeof_gr_complex),
            gr.io_signature(2, 2, gr.sizeof_gr_complex)
        )

        self.preamble_length= preamble_length

        # Blocks
        self.corr = xfdm_sync.fqsweep_corr(preamble_length)
        self.tagger = xfdm_sync.sc_tagger(180, 220, preamble_length)

        # Connections
        self.connect((self, 0), (self.corr, 0))

        self.connect((self.corr, 0), (self.tagger, 0))
        self.connect((self.corr, 1), (self.tagger, 1))

        self.connect((self.tagger, 0), (self, 0))
        self.connect((self.tagger, 1), (self, 1))

    def gen_preamble(self):
        SPAN= np.pi*7/8

        freq_rise= np.linspace(-SPAN, SPAN, self.preamble_length/2)
        freqs= np.concatenate((freq_rise, freq_rise[::-1]))
        phases= np.add.accumulate(freqs)
        samples= np.exp(1j * phases)

        return(samples)

class DUTSchCox(gr.hier_block2):
    def __init__(self, preamble_length):
        gr.hier_block2.__init__(
            self, "dut_sch_cox",
            gr.io_signature(1, 1, gr.sizeof_gr_complex),
            gr.io_signature(2, 2, gr.sizeof_gr_complex)
        )

        self.preamble_length= preamble_length

        # Blocks
        self.corr = xfdm_sync.sc_delay_corr(preamble_length/2, True)
        self.tagger = xfdm_sync.sc_tagger(0.6, 0.8, preamble_length)

        # Connections
        self.connect((self, 0), (self.corr, 0))

        self.connect((self.corr, 0), (self.tagger, 0))
        self.connect((self.corr, 1), (self.tagger, 1))

        self.connect((self.tagger, 0), (self, 0))
        self.connect((self.tagger, 1), (self, 1))

    def gen_preamble(self):
        ZCH_U= 47
        ZCH_Q= 13

        length= self.preamble_length/2

        n= np.arange(length)
        half= 3 * np.exp(
            -1j * np.pi * ZCH_U * n * (n + 1 + 2*ZCH_Q) / length
        )

        samples= np.concatenate((half, half))

        return(samples)


class AlgorithmArena(gr.top_block):
    def __init__(self, dut, noise_level):
        gr.top_block.__init__(self, "Algorithm Arena")

        # Generate Signal
        self.dut= dut
        preamble= dut.gen_preamble()
        frame= self.gen_ofdmframe(512, 64, 64)
        pad= np.zeros(9000)

        signal= np.concatenate((pad, preamble, frame))

        # Blocks
        self.src = blocks.vector_source_c(signal, False, 1, [])
        self.dst_pass = blocks.vector_sink_c(1)
        self.dst_corr = blocks.vector_sink_c(1)

        self.channel = channels.channel_model(
            noise_voltage= noise_level,
            frequency_offset= 0.0,
            epsilon= 1.0,
            taps= ((1.0, )),
            noise_seed= np.random.randint(2**31),
            block_tags= False
        )


        # Connections
        self.connect((self.src, 0), (self.channel, 0))
        self.connect((self.channel, 0), (dut, 0))
        self.connect((dut, 0), (self.dst_pass, 0))
        self.connect((dut, 1), (self.dst_corr, 0))

    def plot(self):
        corr= np.array(self.dst_corr.data())
        dass= np.array(self.dst_pass.data())

        print(', '.join(str(t.offset) for t in self.dst_pass.tags()))

        plt.subplot(2, 1, 1)
        plt.plot(abs(corr))

        plt.subplot(2, 1, 2)
        plt.plot(abs(dass))

        plt.show()

    def battle(self):
        self.run()

        hits= list(
            int(tag.offset)
            for tag in self.dst_pass.tags()
            if str(tag.key) == 'preamble_start'
        )

        if len(hits) == 0:
            hits.append(0)

        return(hits)

    def gen_ofdmsym(self, len_fft, len_cp):
        fqd= np.random.choice((-1, 1), len_fft) + np.random.choice((-1j, 1j), len_fft)
        tid= np.fft.ifft(fqd) * (len_fft**0.5)

        cyc= np.concatenate((tid[-len_cp:], tid))

        return(cyc)

    def gen_ofdmframe(self, len_fft, len_cp, num_symbols):
        frame= np.concatenate(
            tuple(self.gen_ofdmsym(len_fft, len_cp) for i in range(num_symbols))
        )

        return(frame)

def histogram(arena_gen, iterations):
    dist= dict()

    for i in range(iterations):
        arena= arena_gen()

        for hit in arena.battle():
            dist[hit]= (dist[hit] + 1) if (hit in dist) else 1

        #arena.plot()

    center, _= max(
        filter(lambda h: (h[0] > 9000 and h[0] < 12000), dist.items()),
        key= lambda h: h[1]
    )
    start= center-10
    end= center+11

    outliers= sum(
        value
        for key, value in dist.items()
        if (key < start) or (key >= end)
    )

    hist= [outliers]

    hist.extend(
        dist[i] if (i in dist) else 0
        for i in range(start, end)
    )

    return(center, hist)


def main():
    TEST_RUNS= 500
    PREAMBLE_LEN= 512
    NOISE_LEVELS= (0.1, 0.4, 0.7, 1.0, 1.5)

    global histograms
    histograms= dict()

    for noise_level in NOISE_LEVELS:
        histograms[noise_level]= dict()

        def bs_gen():
            dut= DUTBurstSilence(PREAMBLE_LEN)
            aa= AlgorithmArena(dut, noise_level)

            return(aa)

        histograms[noise_level]['bs']= histogram(bs_gen, TEST_RUNS)


        def fqs_gen():
            dut= DUTFreqSweep(PREAMBLE_LEN)
            aa= AlgorithmArena(dut, noise_level)

            return(aa)

        histograms[noise_level]['fq']= histogram(fqs_gen, TEST_RUNS)


        def sc_gen():
            dut= DUTSchCox(PREAMBLE_LEN)
            aa= AlgorithmArena(dut, noise_level)

            return(aa)

        histograms[noise_level]['sc']= histogram(sc_gen, TEST_RUNS)


    for row in range(5):
        for col in range(3):
            rowa= NOISE_LEVELS[row]
            cola= ('bs', 'fq', 'sc')[col]

            plt.subplot(5, 3, col + row*3 +1)

            hs= np.array(histograms[rowa][cola][1])

            plt.bar(np.arange(len(hs)), hs)

    plt.show()

if __name__ == '__main__':
    main()
