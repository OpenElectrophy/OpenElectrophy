

import numpy as np



def get_following_peak(ind_spike, sign):
    """
    Give the following peak after a point.
    """
    # TODO
    ind_peaks = ind_spike+2
    
    
    return ind_peaks


def initialize_waveform(spikesorter, wisze):
    """
    Initialize in spikesorter object:
        * spikeWaveforms given a win_size
        * segmentToSpikesMembership
    
    """
    trodness = len(spikesorter.recordingChannels)
    
    start = 0
    spikesorter.segmentToSpikesMembership = { }
    for seg, ind in enumerate(spikesorter.spikeIndexArray):
        stop = start + ind.size
        spikesorter.segmentToSpikesMembership[seg] = slice(start, stop)
        start = stop
    n_spike = start
    
    spikesorter.spikeWaveforms = np.empty((n_spike, trodness, wisze), dtype = float)


def remove_limit_spikes(spikesorter, swL, swR):
    """
    Remove spikes wich waveform cannot be extracted from sig because of limits.
    swL, swR : sweep size in point
    """
    for seg, segment in enumerate(spikesorter.segments):
        sig_size = spikesorter.filteredBandAnaSig[0,seg].size
        ind = spikesorter.spikeIndexArray[seg]
        mask = (ind>swL+1) & (ind<sig_size-swR-3)
        spikesorter.spikeIndexArray[seg] = ind[mask]
    