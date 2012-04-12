

# TO BE REMOVE
import sys
sys.path.append('../..')
#


import quantities as pq
from spikesorting import *
import numpy as np

# generate dataset
bl = generate_block_for_sorting(nb_unit = 6,
                                                    duration = 5.*pq.s,
                                                    noise_ratio = 0.2,
                                                    #use_memmap_path = './', # Alvaro uncomment this to test
                                                                                            # big big arrays with disk acces
                                                    )
recordingChannelGroup = bl.recordingchannelgroups[0]
spikesorter = SpikeSorter(recordingChannelGroup, initialState='fullBandSignal')


# Apply a chain
spikesorter.runStep( ButterworthFilter, f_low = 200.)
print spikesorter.filteredBandAnaSig.shape
print
spikesorter.filteredBandAnaSig = spikesorter.fullBandAnaSig
spikesorter.runStep( MedianThresholdDetection,sign= '-', median_thresh = 6,
                                                sweep_clean_method = 'fast',
                                                sweep_clean_size = 0.8*pq.ms,
                                                consistent_across_channels = True,
                                                consistent_across_segments = True,
                                                )

print spikesorter.spikeIndexArray.shape
print spikesorter.spikeIndexArray[0].shape
print
spikesorter.runStep(AlignWaveformOnPeak   , left_sweep = 2*pq.ms , right_sweep = 3*pq.ms)
#~ spikesorter.runStep(AlignWaveformOnDetection   , left_sweep = 1*pq.ms , right_sweep = 2*pq.ms)

print spikesorter.segmentToSpikesMembership
print spikesorter.spikeWaveforms.shape
print
spikesorter.runStep(PcaFeature   , n_components = 3)
print spikesorter.spikeWaveformFeatures.shape
print spikesorter.featureNames
print
spikesorter.runStep(SklearnGaussianMixtureEm   ,n_cluster = 12, n_iter = 200 )
print spikesorter.spikeClusters.shape
print spikesorter.clusterNames




# Plot signals
from matplotlib import pyplot
from matplotlib.cm import get_cmap

#colors = 'rybcm'
cmap = get_cmap('jet' , 10)
colors = [ ]
for i in range(10):
    colors.append(cmap(i+2) )


fig1 = pyplot.figure()
nseg = len(spikesorter.segments)
nrc = len(spikesorter.recordingChannels)
for s in range(nseg):
    ax = None
    for c in range(nrc):
        ax = fig1.add_subplot(nrc,nseg,c*nseg+s+1, sharex = ax)
        ax.plot(spikesorter.filteredBandAnaSig[c,s], color = 'k')
        #~ ax.plot(spikesorter.fullBandAnaSig[c,s], color = 'k')
        
        
        pos_on_sig = spikesorter.spikeIndexArray[s]
        seg_slice = spikesorter.segmentToSpikesMembership[s]
        clusters = spikesorter.spikeClusters[seg_slice]
        
        for cluster in spikesorter.clusterNames.keys():
            mask = clusters == cluster
            #~ print cluster
            ax.plot(pos_on_sig[mask], spikesorter.filteredBandAnaSig[c,s][pos_on_sig[mask]],
                                color = colors[cluster%len(colors)], ls = 'None', marker = 'o')




# Plot waveform and features
fig2 = pyplot.figure()
ax2s = [ ];ax2 = None;
for c in range(nrc):
    ax2 =  fig2.add_subplot(nrc, 1,c+1, sharex = ax2)
    ax2s.append(ax2)
fig3 = pyplot.figure()
ax3 = fig3.add_subplot(1,1,1)
clusters = spikesorter.spikeClusters
for cluster in spikesorter.clusterNames.keys():
    color = colors[cluster%len(colors)]
    mask = clusters == cluster
    for c in range(nrc):
        wf = spikesorter.spikeWaveforms[mask, c, :]
        m = np.mean(wf, axis=0)
        sd = np.std(wf, axis=0)
        ax2s[c].plot(m,color = color )
        ax2s[c].fill_between(np.arange(m.size), m-sd,m+sd, alpha = .01, color = color )
        ax3.plot(spikesorter.spikeWaveformFeatures[mask, 0], spikesorter.spikeWaveformFeatures[mask, 1],
                                ls = 'None', marker = '.', color = color)

pyplot.show()

