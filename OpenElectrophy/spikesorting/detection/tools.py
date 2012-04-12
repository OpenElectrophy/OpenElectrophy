

import numpy as np




def get_all_crossing_threshold(sig, thresh, front):
    """
    Simple crossing threshold detection
    """
    if front == '+':
        pos_spike,  = np.where( (sig[:-1] <= thresh) & ( sig[1:]>thresh) )
    elif front == '-':
        pos_spike,  = np.where( (sig[:-1] >= thresh) & ( sig[1:]<thresh) )
    
    return pos_spike


def sweep_clean_in_segment(spike_indexes, signals, sweep_size, method = 'fast'):
    """
    A spike can be detected in several electrode.
    We need an inter electrode clean.
    
    spike_indexes is array of size trdoness that contain array of spike index
    
    """
    if method == 'noclean':
        all = np.unique(np.concatenate(spike_indexes.tolist()))
        return all
        
    if method == 'fast':
        # fast and dirty
        all = np.unique(np.concatenate(spike_indexes.tolist()))
        for i, ind in enumerate(all):
            all[abs(all - ind)<=sweep_size] = ind
        return np.unique(all)
    
    
    if method == 'keep biggest peak':
        #TODO : something like in OE2
        all = np.unique(np.concatenate(spike_indexes.tolist()))
        return all
    
    
    
    
    
    
    