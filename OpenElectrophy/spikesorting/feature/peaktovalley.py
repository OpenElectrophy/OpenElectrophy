
import numpy as np


class PeakToValley(object):
    """
    This method extracts only the peak and following valley
    of each waveform.
    This method mimics old habits in some lab.
    
    In case of mono-electrode the output dimension is 1. So you can't plot
    features in 3D space nor in N-D space.
    
    """
    
    name = 'Peak to valley'
    params = [ ]
    
    def run (self, spikesorter):
        sps = spikesorter
        
        wf = sps.spike_waveforms
        
        sps.waveform_features, sps.feature_names = perform_peak_to_valley(wf)
    

def perform_peak_to_valley(wf):
    n = wf.shape[1]
    peaks1 = np.concatenate([ np.amax( wf[:,i,:], axis = 1)[:,np.newaxis] for i in range(n) ], axis = 1)
    peaks2 = np.concatenate([ np.amin( wf[:,i,:], axis = 1)[:,np.newaxis] for i in range(n) ], axis = 1)
    features = peaks2 - peaks1
    names = np.array([ 'peak2valley {}'.format(i) for i in range(n) ], dtype = 'U')
    
    return features, names
