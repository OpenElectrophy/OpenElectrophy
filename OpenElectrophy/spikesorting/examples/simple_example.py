# This for the moment not a test but a basic example.


# TO BE REMOVE
import sys
sys.path.append('../..')
#


import quantities as pq
from spikesorting import *
import numpy as np

# generate dataset
bl = generate_block_for_sorting(nb_unit = 6,
                                                    duration = 10.*pq.s,
                                                    noise_ratio = 0.2,
                                                    nb_segment = 2,
                                                    #use_memmap_path = './', # Alvaro uncomment this to test
                                                                                            # big big arrays with disk acces
                                                    )
rcg = bl.recordingchannelgroups[0]
spikesorter = SpikeSorter(rcg, initial_state='full_band_signal')


# Apply a chain
spikesorter.ButterworthFilter( f_low = 200.)
print spikesorter.filtered_sigs.shape
print

spikesorter.MedianThresholdDetection(sign= '-', median_thresh = 6,)
#~ spikesorter.StdThresholdDetection(sign= '-', std_thresh = 6,)
#~ spikesorter.ManualThresholdDetection(sign= '-', threshold = -3.5,)
#~ spikesorter.MTEODetection(k_inc=1,k_max=5, median_thresh = 6.,)

print spikesorter.spike_index_array.shape
print spikesorter.spike_index_array[0].shape
print


#~ spikesorter.AlignWaveformOnDetection(left_sweep = 1*pq.ms , right_sweep = 2*pq.ms)
spikesorter.AlignWaveformOnPeak(left_sweep = 1*pq.ms , right_sweep = 2*pq.ms, sign = '-')


print spikesorter.seg_spike_slices
print spikesorter.spike_waveforms.shape
print
## spikesorter.run_step(PcaFeature   , n_components = 3)
#~ spikesorter.PcaFeature(n_components = 3)
#~ spikesorter.IcaFeature(n_components = 3)
#~ spikesorter.AllPeak(sign = '-')
#~ spikesorter.PeakToValley()
#~ spikesorter.HaarWaveletFeature(n_components = 3, level = 4, std_restrict = 3.)
spikesorter.CombineFeature(use_peak = True, use_peak_to_valley = True, n_pca = 3, n_ica = 3, n_haar = 3, sign = '-')

print spikesorter.waveform_features.shape
print spikesorter.feature_names
print
#~ spikesorter.SklearnGaussianMixtureEm(n_cluster = 12, n_iter = 500 )
#~ spikesorter.SklearnKMeans(n_cluster = 16)
spikesorter.SklearnMiniBatchKMeans(n_cluster = 16)
#~ spikesorter.SklearnMeanShift()
print spikesorter.spike_clusters.shape
print spikesorter.cluster_names




# Plot signals
from matplotlib import pyplot
from matplotlib.cm import get_cmap

#colors = 'rybcm'
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
    #~ ax2 =  fig2.add_subplot(nrc, 1,c+1, sharex = ax2)
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

