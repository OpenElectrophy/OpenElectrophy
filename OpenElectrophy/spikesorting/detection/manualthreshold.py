
import numpy as np
import quantities as pq

from .tools import threshold_detection_multi_channel_multi_segment

class ManualThresholdDetection(object):
    """
    This medthod detect spikes with manual threshold.
    The same threshold is applied to all channel and segments.
    
    Note that you can have a negative threshold and sign = '+'.
    
    Arguments:
        * threshold: a manual and absolut threshold (can be negative)
        * sign: signa of the peak
    
    """
    name = 'Manual threshold detection'
    params = [  {'name': 'sign', 'type': 'list', 'value': '-', 'values' : ['-', '+'] },
                            {'name': 'sweep_clean_size', 'type': 'quantity', 'value': 0.8*pq.ms, 'step' : 0.1*pq.ms },
                            ]
                            
    def run(self, spikesorter, sign = '-', threshold = -1.,
                                    merge_method = 'fast', sweep_clean_size = 0.8*pq.ms,):
        sps = spikesorter
        sweep_size = int((sps.sig_sampling_rate*sweep_clean_size).simplified)
        
        thresholds = np.ones(sps.filtered_sigs.shape, dtype = float) * threshold
        
        # Detect
        sps.spike_index_array = threshold_detection_multi_channel_multi_segment(
                                sps.filtered_sigs, thresholds, sign, 
                                False,False,
                                sweep_size, merge_method = merge_method,)



    