

import numpy as np

import numexpr



def initialize_waveform(spikesorter, wisze):
    """
    Initialize in spikesorter object:
        * spike_waveforms given a win_size
        * seg_spike_slices
    
    """
    trodness = len(spikesorter.rcs)
    spikesorter.init_seg_spike_slices()
    n_spike = np.sum( [ ind.size for ind in spikesorter.spike_index_array])
    spikesorter.spike_waveforms = np.empty((n_spike, trodness, wisze), dtype = float)


def remove_limit_spikes(spikesorter, swl, swr):
    """
    Remove spikes wich waveform cannot be extracted from sig because of limits.
    swl, swr : sweep size in point
    """
    for s, seg in enumerate(spikesorter.segs):
        sig_size = spikesorter.filtered_sigs[0,s].size
        ind = spikesorter.spike_index_array[s]
        mask = (ind>swl+1) & (ind<sig_size-swr-3)
        spikesorter.spike_index_array[s] = ind[mask]
    
    spikesorter.check_change_on_attributes('spike_index_array')
    