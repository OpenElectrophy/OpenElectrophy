
import numpy as np


class AllPeak(object):
    """
    This method extracts only the peak of each waveform. This method mimics
    old habits in some lab.
    
    In case of mono-electrode the output dimension is 1. So you can't plot
    features in 3D space nor in N-D space.
    
    For tetrodes (dim=4) this is not so bad at the end!!
    
    
    
    """
    
    name = 'Peaks amplitude'
    params = [  {'name': 'sign', 'type': 'list', 'value': '-', 'values' : ['-', '+'] },    
                        ]
    
    def run (self, spikesorter, sign = '-'):
        sps = spikesorter
        
        wf = sps.spike_waveforms
        
        sps.waveform_features, sps.feature_names = perform_peak(wf,sign)
    

def perform_peak(wf, sign):
        
    n = wf.shape[1]
    if sign=='+':
        op = np.amax
    elif sign=='-':
        op = np.amin

    features = np.concatenate([ op( wf[:,i,:], axis = 1)[:,np.newaxis] for i in range(n) ], axis = 1)
    names = np.array([ 'peak {}'.format(i) for i in range(n) ], dtype = 'U')
    
    return features, names
