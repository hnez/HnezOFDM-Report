#!/usr/bin/env python2

from __future__ import print_function

from gnuradio import gr, blocks, channels
from multiprocessing import Pool

import matplotlib.pyplot as plt
import numpy as np
import itertools as it
import operator as op

import xfdm_sync
import time

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
        self.tagger = xfdm_sync.sc_tagger(300, 400, preamble_length)

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
        self.tagger = xfdm_sync.sc_tagger(0.7, 0.9, preamble_length)

        # Connections
        self.connect((self, 0), (self.corr, 0))

        self.connect((self.corr, 0), (self.tagger, 0))
        self.connect((self.corr, 1), (self.tagger, 1))

        self.connect((self.tagger, 0), (self, 0))
        self.connect((self.tagger, 1), (self, 1))

    def gen_preamble(self):
        span= np.pi*3/4

        freqs= np.linspace(-span, span, self.preamble_length)
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
        self.tagger = xfdm_sync.sc_tagger(0.3, 0.4, preamble_length)

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

def rms(sig):
    return np.sqrt((abs(sig) ** 2).sum() / len(sig))

class AlgorithmArena(gr.top_block):
    def __init__(self, dut, noise_level, channel_irs, delta_f):
        gr.top_block.__init__(self, "Algorithm Arena")

        channel_irs= np.array(channel_irs,np.float64)

        # Generate Signal
        self.dut= dut
        preamble= dut.gen_preamble()
        frame= self.gen_ofdmframe(512, 64, 64)

        # Normalize power
        preamble/= rms(preamble)
        frame/= rms(frame)
        channel_irs/= rms(channel_irs)

        pad= np.zeros(9000)

        signal= np.concatenate((pad, preamble, frame))

        # Blocks
        self.src = blocks.vector_source_c(signal, False, 1, [])
        self.dst_pass = blocks.vector_sink_c(1)
        self.dst_corr = blocks.vector_sink_c(1)

        self.channel = channels.channel_model(
            noise_voltage= noise_level,
            frequency_offset= delta_f,
            epsilon= 1.0,
            taps= channel_irs,
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
        tid= np.fft.ifft(fqd)

        cyc= np.concatenate((tid[-len_cp:], tid))

        return(cyc)

    def gen_ofdmframe(self, len_fft, len_cp, num_symbols):
        frame= np.concatenate(
            tuple(self.gen_ofdmsym(len_fft, len_cp) for i in range(num_symbols))
        )

        return(frame)

def histogram(arena_gen, iterations, center):
    dist= dict()

    for i in range(iterations):
        arena= arena_gen()

        for hit in arena.battle():
            dist[hit]= (dist[hit] + 1) if (hit in dist) else 1

        #arena.plot()

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

    return(hist)

def db_ampl(db):
    return 10 ** (db / 20.0)

def db_pwr(db):
    return 10 ** (db / 10.0)

def test_snr(preamble_len, runs, snr):
    noise_level= db_ampl(-snr)

    print('Working on snr {}dB, {}'.format(snr,noise_level))

    algos= dict()

    def bs_gen():
        dut= DUTBurstSilence(preamble_len)
        aa= AlgorithmArena(dut, noise_level, (1,), 0)

        return(aa)

    algos['bs']= histogram(bs_gen, runs, 10532)


    def fqs_gen():
        dut= DUTFreqSweep(preamble_len)
        aa= AlgorithmArena(dut, noise_level, (1,), 0)

        return(aa)

    algos['fq']= histogram(fqs_gen, runs, 10534)


    def sc_gen():
        dut= DUTSchCox(preamble_len)
        aa= AlgorithmArena(dut, noise_level, (1,), 0)

        return(aa)

    algos['sc']= histogram(sc_gen, runs, 10531)

    return algos

def test_channels(preamble_len, runs, channel):
    noise_level= db_ampl(-6.0)

    print('Working on channel {}'.format(' | '.join(map(str, channel))))

    algos= dict()

    def bs_gen():
        dut= DUTBurstSilence(preamble_len)
        aa= AlgorithmArena(dut, noise_level, channel, 0)

        return(aa)

    algos['bs']= histogram(bs_gen, runs, 10532)


    def fqs_gen():
        dut= DUTFreqSweep(preamble_len)
        aa= AlgorithmArena(dut, noise_level, channel, 0)

        return(aa)

    algos['fq']= histogram(fqs_gen, runs, 10534)


    def sc_gen():
        dut= DUTSchCox(preamble_len)
        aa= AlgorithmArena(dut, noise_level, channel, 0)

        return(aa)

    algos['sc']= histogram(sc_gen, runs, 10531)

    return algos


def test_freqoffs(preamble_len, runs, freq_off):
    noise_level= db_ampl(-6.0)

    print('Working on freq {}'.format(freq_off))

    algos= dict()

    def bs_gen():
        dut= DUTBurstSilence(preamble_len)
        aa= AlgorithmArena(dut, noise_level, (1, ), freq_off)

        return(aa)

    algos['bs']= histogram(bs_gen, runs, 10532)


    def fqs_gen():
        dut= DUTFreqSweep(preamble_len)
        aa= AlgorithmArena(dut, noise_level, (1, ), freq_off)

        return(aa)

    algos['fq']= histogram(fqs_gen, runs, 10534)


    def sc_gen():
        dut= DUTSchCox(preamble_len)
        aa= AlgorithmArena(dut, noise_level, (1, ), freq_off)

        return(aa)

    algos['sc']= histogram(sc_gen, runs, 10531)

    return algos

def main():
    TEST_RUNS= 20
    PREAMBLE_LEN= 512

    SNR_DB= (6.0, 4.5, 3.0, 1.5, 0.0, -1.5, -3)
    CHANNEL_IRS= (
        (1, ),
        (1, db_ampl(-10), db_ampl(-10), db_ampl(-20), db_ampl(-20), 0, db_ampl(-17)),
        (1, ) + 10 * (0, ) + (db_ampl(-7), db_ampl(-4), db_ampl(-7)),
        (1, ) + 10 * (0, ) + (db_ampl(-2), ),
        (1, ) + 5 * (0, ) + (1, 1, 1) + 4 * (0, ) + (1, )
    )
    FREQ_OFFS= (0, 0.1, 0.3)

    process_pool= Pool(12)

    tasks= dict()

    time_start= time.time()

    tasks['nois']= list(
        process_pool.apply_async(test_snr, (PREAMBLE_LEN, TEST_RUNS, snr))
        for snr in SNR_DB
    )

    tasks['chan']= list(
        process_pool.apply_async(test_channels, (PREAMBLE_LEN, TEST_RUNS, chan))
        for chan in CHANNEL_IRS
    )

    tasks['freq']= list(
        process_pool.apply_async(test_freqoffs, (PREAMBLE_LEN, TEST_RUNS, fo))
        for fo in FREQ_OFFS
    )

    tests= dict(
        (name, list(task.get() for task in task_list))
        for (name, task_list)
        in tasks.items()
    )

    process_pool.terminate()
    process_pool.join()

    time_end= time.time()

    print(time_end, time_start)

    print('Doing {} runs took {:.2f} Minutes'.format(
        TEST_RUNS,
        (time_end - time_start) / 60.0
    ))

    for (test_name, test_results) in tests.items():
        plt.figure()
        plot_num= 1

        for (subtest_id, subtest_results) in enumerate(test_results):
            for (algo_name, algo_results) in subtest_results.items():
                n_subtests= len(test_results)
                n_algos= len(subtest_results)

                plt.subplot(n_subtests, n_algos, plot_num)
                plt.bar(
                    np.arange(len(algo_results)),
                    algo_results
                )

                plot_num+= 1

                print('{}_{}_{} = {}'.format(
                    test_name,
                    subtest_id,
                    algo_name,
                    ', '.join(map(str, algo_results))
                ))

    plt.show()

if __name__ == '__main__':
    main()
