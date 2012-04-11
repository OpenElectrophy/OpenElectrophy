

import numpy as np

from .tools import (get_all_crossing_threshold, window_cleaning_in_segment)

class MedianThresholdDetection:
    """
    This medthod detect spikes with estimation of the threshold
    with a median of the signal.
    
    The threshold is calculated as
        median_thresh * median(abs(signal)/.6745) 
    """
    name = 'Median threshold detection'
     
    def run(self, spikesorter, sign = '-', median_thresh = 5.,
                        consistent_across_channels = False,
                        consistent_across_segments = True,
                        reject_other_spike_in_sweep = None,
                        ):
        s = spikesorter
        
        # Use 'sign' to set sign of threshold
        median_thresh = abs(median_thresh)
        
        # Threshold
        thresholds = np.zeros(s.fullBandAnaSig.shape, dtype = float)
        for rc, seg in np.ndindex(s.fullBandAnaSig.shape):
            #~ print rc, seg
            sig = s.filteredBandAnaSig[ rc, seg]
            thresholds[rc, seg] = median_thresh * np.median(abs(sig)) / .6745
        
        if consistent_across_channels:
            thresholds[:] = np.mean(thresholds, axis=0)[np.newaxis,:]
            
        if consistent_across_segments:
            thresholds[:] = np.mean(thresholds, axis=1)[:, np.newaxis]
        
        if sign == '-':
            thresholds = -thresholds
        
        # Detection
        all_pos_spikes = np.empty(s.fullBandAnaSig.shape, dtype = object)
        for rc, seg in np.ndindex(s.fullBandAnaSig.shape):
            pos_spike = get_all_crossing_threshold( s.filteredBandAnaSig[ rc, seg], thresholds[rc, seg], sign)
            all_pos_spikes[rc, seg] = pos_spike
        
        # Window cleaning
        s.spikeIndexArray = np.empty(len(s.segments), dtype = object)
        if reject_other_spike_in_sweep:
            win_size = int(s.signalSamplingRate*reject_other_spike_in_sweep)
            for seg in range(s.fullBandAnaSig.shape[1]):
                s.spikeIndexArray[seg] = window_cleaning_in_segment(all_pos_spikes[:,seg] , s.filteredBandAnaSig[:, seg], win_size)
        else:
            for seg in range(s.fullBandAnaSig.shape[1]):
                pos = np.unique(np.concatenate(all_pos_spikes[:,seg].tolist() ))
                pos.sort()
                s.spikeIndexArray[seg] = pos
            
            
            
        
        
        
        


