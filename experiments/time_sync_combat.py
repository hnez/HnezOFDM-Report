#!/usr/bin/env python2

import numpy as np

from gnuradio import gr, blocks, channels

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

class AlgorithmArena(gr.top_block):
    def __init__(self, dut, noise_level):
        gr.top_block.__init__(self, "Algorithm Arena")

        # Generate Signal
        preamble= dut.gen_preamble()
        frame= self.gen_ofdmframe(512, 64, 8)
        pad= np.zeros(10000)

        signal= np.concatenate((pad, preamble, frame, pad))


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

    def battle(self):
        self.run()

        import matplotlib.pyplot as plt
        
        pwr= np.array(self.dst_corr.data())

        #plt.plot(abs(pwr))
        #plt.show()

        for k in self.dst_pass.tags():
            print('{} {} {}'.format(k.offset, k.key, k.value))

    def gen_ofdmsym(self, len_fft, len_cp):
        fqd= np.random.choice((-1, 1), len_fft) + np.random.choice((-1j, 1j), len_fft)
        tid= np.fft.ifft(fqd)

        cyc= np.concatenate((tid[-len_cp:], tid))

        return(cyc)

    def gen_ofdmframe(self, len_fft, len_cp, num_symbols):
        frame= np.concatenate(
            tuple(self.gen_ofdmsym(len_fft, len_cp) for i in range(num_symbols))
        )

        return(frame)

def main():
    dut= DUTBurstSilence(512)
    aa= AlgorithmArena(dut, 0.5)

    aa.battle()

main()
