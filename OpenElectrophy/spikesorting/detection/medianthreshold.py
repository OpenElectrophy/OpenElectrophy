

import numpy as np
import quantities as pq

from .tools import threshold_detection_multi_channel_multi_segment


class MedianThresholdDetection(object):
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
                        merge_method = 'fast',
                        sweep_clean_size = 0.8*pq.ms,
                        ):
        sps = spikesorter
        
        sweep_size = int((sps.sig_sampling_rate*sweep_clean_size).simplified)
        
        # Threshold estimation
        thresholds = np.zeros(sps.filtered_sigs.shape, dtype = float)
        for c, s in np.ndindex(sps.filtered_sigs.shape):
            sig = sps.filtered_sigs[c, s]
            thresholds[c, s] = abs(median_thresh) * np.median(abs(sig)) / .6745
        if sign == '-':
            thresholds = -thresholds
        
        # Detect
        sps.spike_index_array = threshold_detection_multi_channel_multi_segment(
                                sps.filtered_sigs, thresholds, sign, 
                                consistent_across_channels,consistent_across_segments,
                                sweep_size, merge_method = merge_method,)


