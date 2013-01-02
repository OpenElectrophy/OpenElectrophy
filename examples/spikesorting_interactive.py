# -*- coding: utf-8 -*-
"""
Spike sorting with interactive conosle
-----------------------------------------------

If you do not want tu use the UI dialog for spike sorting, the full spike sorting framework is accessible via 
the SpikeSorter class. It can be useful if you do not like to click or if you want to detect spike through batch
for big amount of data or if you are a console expert.

The philosophy for detecting and sorting spike is exactly the same as in the UI:
    * You can apply steps of a tool chain. Example: Filter>detection>waveform>pca>k-mean
    * The spieksorter take a RecordingChannelGroup (= several channel) accross several segment.
    * The trodness is managed by the size of the list of RecordingChannelGroup.
    * You can try concurent methods for each step Example: pca vs ica.



SpikeSorter  also offers intuitive methods like:
 * delete_one_cluster
 * add_one_spike
 * regroup_small_cluster

"""

import sys
sys.path.append('..')

if __name__== '__main__':

    import quantities as pq
    from OpenElectrophy.spikesorting import (generate_block_for_sorting, SpikeSorter)
        
    # read or create datasets
    bl = generate_block_for_sorting(nb_unit = 6,
                                duration = 5.*pq.s,
                                noise_ratio = 0.2,
                                )
    rcg = bl.recordingchannelgroups[0]
    spikesorter = SpikeSorter(rcg)
    
    # display unit before sorting
    for u, unit in enumerate(rcg.units):
        print u, 'unit name', unit.name
        for s, seg in enumerate(rcg.block.segments):
            sptr = seg.spiketrains[u]
            print ' in Segment', s, 'has SpikeTrain with ', sptr.size

    # Apply a chain
    spikesorter.ButterworthFilter( f_low = 200.)
    # equivalent to
    # spikesorter.run_step(ButterworthFilter, f_low = 200.)
    spikesorter.MedianThresholdDetection(sign= '-',median_thresh = 6)
    spikesorter.AlignWaveformOnDetection(left_sweep = 1*pq.ms ,right_sweep = 2*pq.ms)
    spikesorter.PcaFeature(n_components = 6)
    spikesorter.SklearnGaussianMixtureEm(n_cluster = 6, n_iter = 200 )



    print

    # display unit after sorting
    rcg = spikesorter.populate_recordingchannelgroup()
    for u, unit in enumerate(rcg.units):
        print u, 'unit name', unit.name
        for s, seg in enumerate(rcg.block.segments):
            sptr = seg.spiketrains[u]
            print ' in Segment', s, 'has SpikeTrain with ', sptr.size

