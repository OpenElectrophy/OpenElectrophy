







import quantities as pq
import numpy as np

from tools import initialize_waveform, get_following_peak, remove_limit_spikes

class AlignWaveformOnDetection(object):
    """
    Align spike waveform on the original signal where detected
    This is fast but other method with interpolation give better results.
    
    
    """
    name = 'Align waveform on detection'


    def run(self, spikesorter, sign = '-', left_sweep = 1*pq.ms, right_sweep = 1*pq.ms):
        sps = spikesorter

        sr = sps.sig_sampling_rate
        swl = int((left_sweep*sr).simplified)
        swr = int((right_sweep*sr).simplified)
        wsize = swl + swr + 1
        trodness = sps.filtered_sigs.shape[0]
        
        # clean
        remove_limit_spikes(spikesorter, swl, swr)
        
        # Initialize
        initialize_waveform(spikesorter, wsize)
        sps.wf_sampling_rate = sps.sig_sampling_rate
        sps.left_sweep =swl
        sps.right_sweep = swr
        
        # take individual waveform
        n = 0
        for s, indexes in enumerate(sps.spike_index_array):
            for ind in indexes :
                for c in range(len(sps.rcs)):
                    sig = sps.filtered_sigs[c, s]
                    sps.spike_waveforms[n,c, :] = sig[ind-swl:ind+swr+1]
                n += 1


