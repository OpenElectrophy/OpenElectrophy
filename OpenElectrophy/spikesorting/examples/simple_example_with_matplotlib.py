# -*- coding: utf-8 -*-
"""
If you are familiar with matplotlib and want to play with SpikeSorter attributes thsi can help.

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
spikesorter.ButterworthFilter( f_low = 200.)
spikesorter.StdThresholdDetection(sign= '-', std_thresh = 6,)
print spikesorter
spikesorter.AlignWaveformOnPeak(left_sweep = 1*pq.ms , right_sweep = 2*pq.ms, sign = '-')
print spikesorter
spikesorter.CombineFeature(use_peak = True, use_peak_to_valley = True, n_pca = 3, n_ica = 3, n_haar = 3, sign = '-')
print spikesorter
spikesorter.SklearnKMeans(n_cluster = 5)
print spikesorter




# Plot signals
from matplotlib import pyplot
from matplotlib.cm import get_cmap


cmap = get_cmap('jet' , 10)
colors = [ ]
for i in range(10):
    colors.append(cmap(i+2) )

fig1 = pyplot.figure()
nseg = len(spikesorter.segs)
nrc = len(spikesorter.rcs)
for s in range(nseg):
    ax = None
    for c in range(nrc):
        ax = fig1.add_subplot(nrc,nseg,c*nseg+s+1, sharex = ax)
        ax.plot(spikesorter.filtered_sigs[c,s], color = 'k')
        #~ ax.plot(spikesorter.fullBandAnaSig[c,s], color = 'k')
        
        pos_on_sig = spikesorter.spike_index_array[s]
        seg_slice = spikesorter.seg_spike_slices[s]
        clusters = spikesorter.spike_clusters[seg_slice]
        
        for cluster in spikesorter.cluster_names.keys():
            mask = clusters == cluster
            ax.plot(pos_on_sig[mask], spikesorter.filtered_sigs[c,s][pos_on_sig[mask]],
                                color = colors[cluster%len(colors)], ls = 'None', marker = 'o')


# Plot waveform and features
fig2 = pyplot.figure()
ax2s = [ ];ax2 = None;
for c in range(nrc):
    ax2 =  fig2.add_subplot(1, nrc,c+1, sharex = ax2)
    ax2s.append(ax2)
fig3 = pyplot.figure()
ax3 = fig3.add_subplot(1,1,1)
clusters = spikesorter.spike_clusters
for cluster in spikesorter.cluster_names.keys():
    color = colors[cluster%len(colors)]
    mask = clusters == cluster
    for c in range(nrc):
        wf = spikesorter.spike_waveforms[mask, c, :]
        m = np.mean(wf, axis=0)
        sd = np.std(wf, axis=0)
        ax2s[c].plot(m,color = color )
        ax2s[c].fill_between(np.arange(m.size), m-sd,m+sd, alpha = .01, color = color )
        ax3.plot(spikesorter.waveform_features[mask, 0], spikesorter.waveform_features[mask, 1],
                                ls = 'None', marker = '.', color = color)
pyplot.show()

