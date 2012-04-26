# -*- coding: utf-8 -*-
"""
This is a basic example of the spikesorting framework in OpenElectrophy.

It is easy:
    1. Understand that a spikesorting is computed on a neo.RecordingChannelGroup
        (one or several eelctrodes along one or several segments)
    2. instantiate a SpikeSorter object
    3. play with it by calling methods.


"""

from OpenElectrophy.spikesorting import *
import quantities as pq
import numpy as np

# generate dataset
bl = generate_block_for_sorting(nb_unit = 6,
                                                    duration = 10.*pq.s,
                                                    noise_ratio = 0.2,
                                                    nb_segment = 2,
                                                    )
rcg = bl.recordingchannelgroups[0]
spikesorter = SpikeSorter(rcg, initial_state='full_band_signal')
print spikesorter


# Apply a chain
# 1. Filter
spikesorter.ButterworthFilter( f_low = 200.)
print spikesorter

# 2. Detection
#~ spikesorter.MedianThresholdDetection(sign= '-', median_thresh = 6.,)
spikesorter.StdThresholdDetection(sign= '-', std_thresh = 6,)
#~ spikesorter.ManualThresholdDetection(sign= '-', threshold = -3.5,)
#~ spikesorter.MTEODetection(k_inc=1,k_max=5, median_thresh = 6.,)
print spikesorter


# 3. Waveform extraction and alignement
#~ spikesorter.AlignWaveformOnDetection(left_sweep = 1*pq.ms , right_sweep = 2*pq.ms)
spikesorter.AlignWaveformOnPeak(left_sweep = 1*pq.ms , right_sweep = 2*pq.ms, sign = '-')
print spikesorter
print spikesorter.left_sweep

# 4. Features (dimension redution) from weaveforms
#~ spikesorter.PcaFeature(n_components = 3)
#~ spikesorter.IcaFeature(n_components = 3)
#~ spikesorter.AllPeak(sign = '-')
#~ spikesorter.PeakToValley()
#~ spikesorter.HaarWaveletFeature(n_components = 3, level = 4, std_restrict = 3.)
spikesorter.CombineFeature(use_peak = True, use_peak_to_valley = True, n_pca = 3, n_ica = 3, n_haar = 3, sign = '-')
print spikesorter

# 5. Clustering
#~ spikesorter.SklearnGaussianMixtureEm(n_cluster = 12, n_iter = 500 )
spikesorter.SklearnKMeans(n_cluster = 5)
#~ spikesorter.SklearnMiniBatchKMeans(n_cluster = 16)
#~ spikesorter.SklearnMeanShift()
#~ print spikesorter.spike_clusters.shape
#~ print spikesorter.cluster_names
print spikesorter



