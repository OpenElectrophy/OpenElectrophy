"""
A serie of tools for playing with threshold and peaks detection taht take in
account multi channel problem.
For instance:
  * detecting the next following biggest peak on multi channel.
  * merging dectetion of all channels
  * playing with consistency of threshold accros channel
  * ...


"""

import numpy as np

import numexpr



def threshold_detection_multi_channel_multi_segment( signals, 
                                thresholds, sign,
                                consistent_across_channels, consistent_across_segments,
                                sweep_size, merge_method = 'keep_biggest_peak',):
    """
    
    
    Arguments:
        * signals: an array (channel x segment) of array (signal)
        * threholds: an array of threshold for each (channel x segment)
        * sign: the sign of the peak (not the threshold!!)
        * consistent_across_channels: 
    
    
    """
    if consistent_across_channels:
        thresholds[:] = np.mean(thresholds, axis=0)[np.newaxis,:]
        
    if consistent_across_segments:
        thresholds[:] = np.mean(thresholds, axis=1)[:, np.newaxis]
    
    # Detection
    all_pos_spikes = np.empty(signals.shape, dtype = object)
    for c, s in np.ndindex(signals.shape):
        pos_spike = get_all_crossing_threshold( signals[c, s],
                                            thresholds[c, s], sign)
        all_pos_spikes[c, s] = pos_spike
    
    # Window cleaning
    spike_index_array = np.empty(signals.shape[1], dtype = object)
    for s in range(signals.shape[1]):
        spike_index_array[s] = merge_inter_channel_spike_index(
                                    all_pos_spikes[:,s],
                                    signals[:, s],
                                    sweep_size,
                                    sign,
                                    method = merge_method)
    
    return spike_index_array
    
    




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


def merge_inter_channel_spike_index(spike_indexes, signals, sweep_size, sign, method = 'keep_biggest_peak'):
    """
    A spike can be detected in several electrode.
    This is an inter electrode clean.
    
    spike_indexes is array of size trdoness that contain array of spike index
    
    """
    if method == 'noclean':
        all = np.unique(np.concatenate(spike_indexes.tolist()))
        return all
    
    if method == 'fast':
        # not fast but dirty
        all = np.unique(np.concatenate(spike_indexes.tolist()))
        for i, ind in enumerate(all):
            all[abs(all - ind)<=sweep_size] = ind
        return np.unique(all)
    
    
    if method == 'keep_biggest_peak':
        #TODO : something like in OE2
        all = np.unique(np.concatenate(spike_indexes.tolist()))
        
        peaks = get_following_peak_multi_channel(all, signals, sign, method = 'biggest_amplitude')
        for i, ind in enumerate(peaks):
            peaks[abs(peaks - ind)<=sweep_size] = ind
        
        return np.unique(peaks)
    
    
    

def get_following_peak(ind_spike, sig, sign):
    """
    Give the first following peak after a point on one signal.
    
    Params:
        * ind_spike: index where are detected spike (corssing threshold)
        * sig: a numpy array.
        * sign: signa of peak '-' or '+'
    
    """
    sig1 = sig[:-2]
    sig2 = sig[1:-1]
    sig3 = sig[2:]
    if sign == '+':
        all_peaks, = np.where(numexpr.evaluate( '(sig1<=sig2) & ( sig2>sig3)'))
    elif sign == '-':
        all_peaks, = np.where(numexpr.evaluate( '(sig1>=sig2) & ( sig2<sig3)'))
    
    ind_peaks  = -np.ones(ind_spike.size, dtype = 'i')
    for i, ind in enumerate(ind_spike):
        possible = all_peaks[all_peaks>ind]
        if possible.size>0:
            ind_peaks[i] = possible[0]
    
    return ind_peaks


def get_following_peak_multi_channel(ind_spike, sigs, sign, method = 'biggest_amplitude'):
    """
    Give the first following peak on multisignal.
    
    Params:
        * ind_spike: index where are detected spike (corssing threshold)
        * sigs: a array numpy array.
        * sign: signa of peak '-' or '+'
        * method: 'biggest_amplitude' or 'closer'
    
    """
    
    multi_peaks =[ ]
    amplitudes = [ ]
    for c, sig in enumerate(sigs):
        multi_peaks.append(get_following_peak(ind_spike, sig, sign))
    multi_peaks = np.array(multi_peaks)
    
    ind_peaks = -np.ones(ind_spike.size, dtype = 'i')
    for i, ind in enumerate(ind_spike):
        if method == 'closer':
            ind_peaks = multi_peak[:,i].min()
        elif method == 'biggest_amplitude':
            if np.all(multi_peaks[:,i] == -1):
                ind_peaks[i] = -1
                continue
            
            peak_values = [ ]
            for c, sig in enumerate(sigs):
                if multi_peaks[c,i] != -1:
                    peak_values.append(sig[multi_peaks[c,i]])
                else:
                    peak_values.append(0)
            
            if sign == '+':
                biggest = np.argmax(peak_values)
            elif sign == '-':
                biggest = np.argmin(peak_values)
            ind_peaks[i] = multi_peaks[biggest,i]
            
    
    return ind_peaks
    
    
    