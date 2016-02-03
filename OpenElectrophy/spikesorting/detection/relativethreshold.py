

import numpy as np
import quantities as pq

from .tools import threshold_detection_multi_channel_multi_segment


class RelativeThresholdDetection(object):
    """
    This medthod detect spikes by estimating the noise with 2 possibles methods:
       * classical Standart Deviation (STD)
       * Median Absolut Deviation (MAD)  (median(abs(signal-median(x))/.6745) )
    
    The absolut threshold  = relative_thresh * noise_estimation.
    
    There are 2 possibilities:
       * The event is take at threshold corssing
       * The event is take a local maximas above threshold in that case peak_span is used.
    
    When multi channel, this is computed on the sum of all signal after
        remplacement of samples by zeros when samples are under threshold.
    
    
    consistent_across_channels :
        * if False each channel have it own noise estimation
        * if True all channel have the same noise (average) noise estimation.
    
    This code is insipired from C.Pouzat's R code:
    https://github.com/christophe-pouzat/Neuronal-spike-sorting/blob/master/code/sorting.R
    
    
    
    """
    name = 'Signal to noise threshold detection'
    params = [  {'name': 'sign', 'type': 'list', 'value': '-', 'values' : ['-', '+'] },
                            {'name': 'relative_thresh', 'type': 'float', 'value': 4., 'step' : 0.1, 'miminum' : 0.},
                            
                            {'name': 'noise_estimation', 'type': 'list', 'value': 'MAD', 'values' :  ['MAD', 'STD'] },
                            {'name': 'threshold_mode', 'type': 'list', 'value': 'crossing', 'values' :  ['crossing', 'peak'] },
                            {'name': 'peak_span', 'type': 'quantity', 'value': 0.3*pq.ms, 'step' : 0.01*pq.ms },
                            
                            {'name': 'consistent_across_channels', 'type': 'bool', 'value': False, },
                            {'name': 'consistent_across_segments', 'type': 'bool', 'value': True, },
                            
                            ]
     
    def run(self, spikesorter, sign = '-', relative_thresh = 4., 
                        noise_estimation = 'MAD',  threshold_mode = 'crossing',peak_span =  0.3*pq.ms,
                        consistent_across_channels = False,
                        consistent_across_segments = True,
                        ):
        sps = spikesorter
        
        # Threshold estimation
        centers = np.zeros(sps.filtered_sigs.shape, dtype = float)
        noises = np.zeros(sps.filtered_sigs.shape, dtype = float)
        
        for c, s in np.ndindex(sps.filtered_sigs.shape):
            sig = sps.filtered_sigs[c, s]
            if noise_estimation=='MAD':
                centers[c, s] = np.median(sig)
                noises[c, s] = np.median(np.abs(sig-np.median(sig))) / .6745
            elif noise_estimation=='STD':
                centers[c, s] = np.mean(sig)
                noises[c, s] = np.std(sig)
        
        #~ print centers
        #~ print noises
        
        if sign == '+':
            thresholds = centers + noises*abs(relative_thresh) 
        if sign == '-':
            thresholds = centers - noises*abs(relative_thresh) 
        
        print thresholds
        
        peak_span = int((sps.sig_sampling_rate*peak_span).simplified)
        peak_span = (peak_span//2)*2+1
        # Detect
        sps.spike_index_array = threshold_detection_multi_channel_multi_segment(
                                sps.filtered_sigs, thresholds, sign, 
                                consistent_across_channels,consistent_across_segments,
                                threshold_mode, peak_span,
                                combined_sum = sps.filtered_sigs.shape[0]!=1,
                                )
        sps.detection_thresholds = thresholds
        #~ print thresholds



