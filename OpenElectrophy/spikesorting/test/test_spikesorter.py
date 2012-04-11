

# TO BE REMOVE
import sys
sys.path.append('../..')

import quantities as pq

from spikesorting import *

bl = generate_block_for_sorting(
                    duration = 1.*pq.s,)
recordingChannelGroup = bl.recordingchannelgroups[0]
spikesorter = SpikeSorter(recordingChannelGroup, initialState='fullBandSignal')

# Apply a chain
spikesorter.runStep( ButterworthFilter, f_low = 300.)
print spikesorter.filteredBandAnaSig.shape
print
spikesorter.runStep( MedianThresholdDetection,sign= '-', median_thresh = 5)
print spikesorter.spikeIndexArray
print spikesorter.spikeIndexArray[0]
print
spikesorter.runStep(AlignWaveformOnPeak   , left_sweep = 2*pq.ms , right_sweep = 5*pq.ms)
print spikesorter.segmentToSpikesMembership
print spikesorter.spikeWaveforms.shape
print
spikesorter.runStep(PcaFeature   , n_components = 5)
print spikesorter.spikeWaveformFeatures.shape
print spikesorter.featureNames
print
spikesorter.runStep(SklearnGaussianMixtureEm   , )
print spikesorter.spikeClusters
print spikesorter.clusterNames




