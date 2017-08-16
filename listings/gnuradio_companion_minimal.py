#!/usr/bin/env python2

from gnuradio import analog, blocks, gr

class top_block(gr.top_block):
    def __init__(self):
        gr.top_block.__init__(self, "Top Block")

        # Instanciate blocks
        self.sink = blocks.null_sink(gr.sizeof_gr_complex)
        self.multiply = blocks.multiply_vcc(1)

        self.source_a = analog.sig_source_c(
            44100, analog.GR_COS_WAVE, -1000, 1, 0
        )

        self.source_b = analog.sig_source_c(
            44100, analog.GR_COS_WAVE,  1000, 1, 0
        )

        # Connect blocks
        self.connect((self.source_a, 0), (self.multiply, 0))
        self.connect((self.source_b, 0), (self.multiply, 1))
        self.connect((self.multiply, 0), (self.sink, 0))

if __name__ == '__main__':
    tb = top_block()
    tb.start()
    raw_input('Press Enter to quit: ')
    tb.stop()
    tb.wait()
