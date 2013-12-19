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
                                threshold_mode,
                                peak_span = None,
                                combined_sum = True,
                                ):
    #~ print thresholds
    if consistent_across_channels:
        thresholds[:] = np.mean(thresholds, axis=0)[np.newaxis,:]
        
    if consistent_across_segments:
        thresholds[:] = np.mean(thresholds, axis=1)[:, np.newaxis]
    #~ print thresholds.shape
    
    spike_index_array = np.empty(signals.shape[1], dtype = object)
    
    for s in range(signals.shape[1]):
        if combined_sum:
            combined = [ ]
            for c in range(signals.shape[0]):
                sig = np.zeros(signals[c, s].size, dtype = signals[c, s].dtype)
                if sign == '+':
                    ind = signals[c, s]>thresholds[c, s]
                else:
                    ind = signals[c, s]<thresholds[c, s]
                sig[ind] = signals[c, s][ind]
                sig[ind] /= abs(thresholds[c, s])
                combined.append(sig)
            sig_for_detection = np.sum(combined, axis = 0)
            thresh = np.sign(thresholds[0, s])
        else:
            assert signals.shape[0]==1
            sig_for_detection = signals[0, s]
            thresh = thresholds[0, s]
            
        if threshold_mode=='crossing':
            pos_spike = get_all_crossing_threshold(sig_for_detection, thresh, sign)
            #~ pos_spike = get_all_crossing_threshold(combined, 1., '+')
        elif threshold_mode=='peak':
            pos_spike = get_all_peak_over_threshold(sig_for_detection, thresh, sign, peak_span = peak_span)
            #~ pos_spike = get_all_peak_over_threshold(combined, 1., '+', peak_span = peak_span)
        spike_index_array[s] = pos_spike
    return spike_index_array


def get_all_crossing_threshold(sig, thresh, front, use_numexpr = False):
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
            pos_spike, = np.where(numexpr.evaluate( '(sig1<=thresh) & (sig2>thresh)'))
        elif front == '-':
            pos_spike, = np.where(numexpr.evaluate( '(sig1>=thresh) & (sig2<thresh)'))
    else :
        if front == '+':
            pos_spike,  = np.where( (sig1 <= thresh) & ( sig2>thresh) )
        elif front == '-':
            pos_spike,  = np.where( (sig1 >= thresh) & ( sig2<thresh) )
    return pos_spike+1


def get_all_peak_over_threshold(sig, thresh, front, peak_span = 3, use_numexpr = False):
    """
    Simple solution for detectng peak aboe (or below) a threshold
    """
    peak_span = max(peak_span, 3)
    k = (peak_span-1)//2
    sig_center = sig[k:-k]
    
    if use_numexpr:
        if front == '+':
            pos_spike, = np.where(numexpr.evaluate( '(sig1<sig2) & (sig2>thresh) & (sig2>=sig3)'))
        elif front == '-':
            pos_spike, = np.where(numexpr.evaluate( '(sig1>sig2) & (sig2<thresh) & (sig2<=sig3)'))
    else :
        if front == '+':
            peaks = sig_center>thresh
            for i in range(k):
                peaks &= sig_center>sig[i:i+sig_center.size]
                peaks &= sig_center>=sig[peak_span-i-1:peak_span-i-1+sig_center.size]
        elif front == '-':
            peaks = sig_center<thresh
            for i in range(k):
                peaks &= sig_center<sig[i:i+sig_center.size]
                peaks &= sig_center<=sig[peak_span-i-1:peak_span-i-1+sig_center.size]
    ind_peak,  = np.where(peaks)
    ind_peak = ind_peak + k
    return ind_peak
    

    