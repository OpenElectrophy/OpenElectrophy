
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
    params = [  {'name': 'threshold', 'type': 'float', 'value': 1., 'step' : 0.1},
                            {'name': 'sign', 'type': 'list', 'value': '-', 'values' : ['-', '+'] },

                            {'name': 'threshold_mode', 'type': 'list', 'value': 'peak', 'values' :  ['crossing', 'peak'] },
                            {'name': 'peak_span', 'type': 'quantity', 'value': 0.3*pq.ms, 'step' : 0.01*pq.ms },
                            
                            ]
                            
    def run(self, spikesorter, sign = '-', threshold = -1.,
                                     threshold_mode = 'crossing',peak_span =  0.3*pq.ms,):
        sps = spikesorter
        
        thresholds = np.ones(sps.filtered_sigs.shape, dtype = float) * threshold
        
        peak_span = int((sps.sig_sampling_rate*peak_span).simplified)
        peak_span = (peak_span//2)*2+1
        
        # Detect
        sps.spike_index_array = threshold_detection_multi_channel_multi_segment(
                                sps.filtered_sigs, thresholds, sign, 
                                False,False,
                                threshold_mode, peak_span,
                                combined_sum = sps.filtered_sigs.shape[0]!=1,
                                )
        sps.detection_thresholds = thresholds