

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
    #~ spikesorter.spike_waveforms = np.empty((n_spike, trodness, wisze), dtype = float)
    #~ spikesorter.set_attr_no_check('spike_waveforms',  np.empty((n_spike, trodness, wisze), dtype = float))
    return np.empty((n_spike, trodness, wisze), dtype = float)


def remove_limit_spikes(spikesorter, swl, swr):
    """
    Remove spikes wich waveform cannot be extracted from sig because of limits.
    swl, swr : sweep size in point
    """
    big_mask = [ ]
    for s, seg in enumerate(spikesorter.segs):
        sig_size = spikesorter.filtered_sigs[0,s].size
        ind = spikesorter.spike_index_array[s]
        mask = (ind>swl+1) & (ind<sig_size-swr-3)
        spikesorter.spike_index_array[s] = ind[mask]
        big_mask.append(mask)
    big_mask = np.concatenate(big_mask)
    
    spikesorter.init_seg_spike_slices()
    if spikesorter.spike_clusters is not None:
        spikesorter.set_attr_no_check('spike_clusters', spikesorter.spike_clusters[big_mask])
    if spikesorter.spike_waveforms is not None:
        spikesorter.set_attr_no_check('spike_waveforms', spikesorter.spike_waveforms[big_mask,:])
    if spikesorter.waveform_features is not None:
        spikesorter.set_attr_no_check('waveform_features', spikesorter.waveform_features[big_mask,:])
    #~ spikesorter.check_change_on_attributes('spike_index_array')




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
    all_peaks += 1
    
    ind_peaks  = -np.ones(ind_spike.size, dtype = 'i')
    for i, ind in enumerate(ind_spike):
        possible = all_peaks[all_peaks>=ind]
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
    #~ amplitudes = [ ]
    for c, sig in enumerate(sigs):
        multi_peaks.append(get_following_peak(ind_spike, sig, sign))
    multi_peaks = np.array(multi_peaks)

    
    
    
    if method == 'closer':
        ind_peaks = np.amin(multi_peaks, axis = 0)
    
    elif method == 'biggest_amplitude':
        ind_peaks = -np.ones(ind_spike.size, dtype = 'i')
        for i, ind in enumerate(ind_spike):
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
    