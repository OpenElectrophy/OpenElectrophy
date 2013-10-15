







import quantities as pq
import numpy as np

from tools import initialize_waveform, remove_limit_spikes

class AlignWaveformOnDetection(object):
    """
    Align spike waveform on the original signal where detected
    This mimic what online spikesorter do : spike are alingned at detection point!!
    
    If the detection point is the crossing threshold the alignement is quite bad
    resulting in big jitter noise. If the detection point is the peak the method
    is equivalent to peak alignement.

    This method is fast but other method with interpolation in between samples
    will give really better results.
    
    """
    name = 'Align waveform on detection'
    params = [  
                            #~ {'name': 'sign', 'type': 'list', 'value': '-', 'values' : ['-', '+'] },
                            {'name': 'left_sweep', 'type': 'quantity', 'value': 1.*pq.ms, 'step' : 100*pq.us },
                            {'name': 'right_sweep', 'type': 'quantity', 'value': 1.*pq.ms,'step' : 100*pq.us },
                            
                            {'name': 'waveform_from', 'type': 'list' , 'values' : ['filtered signals', 'full band signals'] },

                            ]


    #~ def run(self, spikesorter, sign = '-', left_sweep = 1*pq.ms, right_sweep = 1*pq.ms):
    def run(self, spikesorter, left_sweep = 1*pq.ms, right_sweep = 1*pq.ms, waveform_from = 'filtered signals'):
        sps = spikesorter

        sr = sps.sig_sampling_rate
        swl = int((left_sweep*sr).simplified)
        swr = int((right_sweep*sr).simplified)
        wsize = swl + swr + 1
        trodness = sps.filtered_sigs.shape[0]
        
        # clean
        remove_limit_spikes(spikesorter, swl, swr)
        
        # Initialize
        spike_waveforms= initialize_waveform(spikesorter, wsize)
        sps.wf_sampling_rate = sps.sig_sampling_rate
        sps.left_sweep =swl
        sps.right_sweep = swr
        
        # take individual waveform
        n = 0
        for s, indexes in enumerate(sps.spike_index_array):
            for ind in indexes :
                for c in range(len(sps.rcs)):
                    if waveform_from=='filtered signals':
                        sig = sps.filtered_sigs[c, s]
                    elif waveform_from=='full band signals':
                        sig = sps.full_band_sigs[c, s]
                    spike_waveforms[n,c, :] = sig[ind-swl:ind+swr+1]
                n += 1
        
        sps.spike_waveforms = spike_waveforms
        
        


