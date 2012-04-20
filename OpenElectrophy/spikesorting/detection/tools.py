

import numpy as np

import numexpr


def get_all_crossing_threshold(sig, thresh, front, use_numexpr = True):
    """
    Simple crossing threshold detection
    
    params:
        * sig: a numpy.array
        * front: {'+' or '-' }
        * use_numexpr is speculative for the moment need more benchmark
    
    """
    sig1 = sig[:-1]
    sig2 = sig[1:]
    
    if use_numexpr:
        if front == '+':
            pos_spike, = np.where(numexpr.evaluate( '(sig1<=thresh) & ( sig2>thresh)'))
        elif front == '-':
            pos_spike, = np.where(numexpr.evaluate( '(sig1>=thresh) & ( sig2<thresh)'))
    else :
        if front == '+':
            pos_spike,  = np.where( (sig1 <= thresh) & ( sig2>thresh) )
        elif front == '-':
            pos_spike,  = np.where( (sig1 >= thresh) & ( sig2<thresh) )

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
    
    
    
    
    
    
    