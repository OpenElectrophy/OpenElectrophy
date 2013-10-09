# -*- coding: utf-8 -*-

import numpy as np



def apply_descending_sort_with_waveform(spikesorter):
    """
    This sort cluster number with descending power of waveform.
    So cluster 0 will be the biggest and cluster N the small in amplitude.
    """
    sps = spikesorter
    
    clusters =  np.unique(sps.spike_clusters)
    clusters.sort()
    clusters =  clusters[clusters !=-1]
    powers = [ ]
    for c in clusters:
        #~ ind = c==sps.spike_clusters
        #~ center = np.median(sps.spike_waveforms[ind,:,:], axis=0)
        #~ print c
        center = sps.median_centers[c]
        power = np.sum(center.flatten()**2)
        powers.append(power)
    #~ print powers
    #~ print clusters
    sorted = clusters[np.argsort(powers)[::-1]]
    #~ print sorted
    
    N = int(max(clusters)*100)
    sps.spike_clusters[sps.spike_clusters!=-1] += N
    for old, new in zip(clusters+N,sorted):
        sps.spike_clusters[sps.spike_clusters==old] = new
    
    sps.recompute_cluster_center()

    
