

import quantities as pq
import numpy as np

from tools import initialize_waveform, remove_limit_spikes

from .tools import get_following_peak_multi_channel

class AlignWaveformOnPeak(object):
    """
    Align spike waveform on peak from the original signal.
    
    This method is useless when the detection already give you the peak.
    
    In case of multi electrode you can choose between two options:
       * the peak is the first peak closer to detection point.
       * the peak is the biggest over all electrode following the detection point.
    
    
    """
    name = 'Align waveform on peak'
    params = [  {'name': 'sign', 'type': 'list', 'value': '-', 'values' : ['-', '+'] },
                            {'name': 'left_sweep', 'type': 'quantity', 'value': 1.*pq.ms, 'step' : 100*pq.us },
                            {'name': 'right_sweep', 'type': 'quantity', 'value': 1.*pq.ms,'step' : 100*pq.us },
                            
                            {'name': 'peak_method', 'type': 'list' , 'values' : ['biggest_amplitude', 'closer'] },
                            ]


    def run(self, spikesorter, sign = '-', left_sweep = 1*pq.ms, right_sweep = 1*pq.ms,
                peak_method = 'biggest_amplitude'):
        sps = spikesorter

        sr = sps.sig_sampling_rate
        swl = int((left_sweep*sr).simplified)
        swr = int((right_sweep*sr).simplified)
        #~ print swl, (left_sweep*sr)
        wsize = swl + swr + 1
        trodness = sps.filtered_sigs.shape[0]
        
        # clean
        remove_limit_spikes(spikesorter, swl, swr*3)
        
        # Initialize
        spike_waveforms = initialize_waveform(spikesorter, wsize)
        sps.wf_sampling_rate = sps.sig_sampling_rate
        sps.left_sweep =swl
        sps.right_sweep = swr
        
        
        # take individual waveform
        n = 0
        for s, indexes in enumerate(sps.spike_index_array):
            peak_indexes = get_following_peak_multi_channel(indexes, sps.filtered_sigs[:,s], sign,
                                                    method = peak_method)
            for ind in peak_indexes :
                for c in range(len(sps.rcs)):
                    sig = sps.filtered_sigs[c, s]
                    spike_waveforms[n,c, :] = sig[ind-swl:ind+swr+1]
                n += 1
        
        sps.spike_waveforms = spike_waveforms
        

