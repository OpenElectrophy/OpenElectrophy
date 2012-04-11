

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
        spikesorter.segmentToSpikesMembership[spikesorter.segments[seg]] = slice(start, stop)
        start = stop
    n_spike = start
    
    spikesorter.spikeWaveforms = np.empty((n_spike, trodness, wisze), dtype = float)
