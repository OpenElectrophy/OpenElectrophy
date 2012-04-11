

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


def window_cleaning_in_segment(pos_spikes, signals, win_size):
    
    
    cleaned = pos_spikes
    
    return cleaned
    
    
    
    
    
    
    
    