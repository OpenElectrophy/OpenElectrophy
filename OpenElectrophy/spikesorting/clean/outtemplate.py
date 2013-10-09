# -*- coding: utf-8 -*-
"""
"""

import quantities as pq
import numpy as np



class OutsideTemplateCleaning(object):
    """
    Clean spike outside the template +/- the deviation X coeff
    
    The template is computed with the median and the deviation with MAD.
    
    2 possibles modes:
         * all sample are taken is account *any_sample*
         * only sample on edge after zeros crossing of median *only_on_edge*
    
    
    
    """
    name = 'Outside Template Cleanning'
    params = [  
                            {'name': 'coeff', 'type': 'float', 'value': 4., 'step' : .1 },
                            {'name': 'which_sample', 'type': 'list' , 'values' : ['any_sample', 'only_on_edge'] },
                            ]


    def run(self, spikesorter, coeff =4., which_sample = 'any_sample'):
        sps = spikesorter
        
        for c in sps.cluster_names.keys():
            if c==-1: continue
            
            ind = sps.spike_clusters==c
            wfs = sps.spike_waveforms[ind,:,:]
            
            limit1 = sps.median_centers[c] - coeff*sps.mad_deviation[c]
            limit2 = sps.median_centers[c] + coeff*sps.mad_deviation[c]
            
            if which_sample == 'only_on_edge':
                # eliminate 
                mask = np.zeros(wfs.shape[2], dtype = bool)
                for i in range(sps.trodness):
                    m = sps.median_centers[c][i,:]
                    c1, = np.where((m[:-1]>0.) & (m[1:]<=0.))
                    c2, = np.where((m[:-1]<0.) & (m[1:]>=0.))
                    crossing = np.unique(np.concatenate( [c1,c2], axis = 0))
                    crossing.sort()
                    crossing_left = crossing[crossing < sps.left_sweep]
                    crossing_right = crossing[crossing > sps.left_sweep]
                    
                    mask[crossing_left[:-2]] = True
                    mask[crossing_right[2:]] = True
                if np.sum(mask)==0: return
                wfs = wfs[:,:,mask]
                limit1 = limit1[:,mask]
                limit2 = limit2[:,mask]
            
            
            wfs = wfs.reshape(wfs.shape[0],-1)
            limit1 = limit1.reshape(-1)
            limit2 = limit2.reshape(-1)
            
            #~ print c
            #~ print ((wfs<limit1) | (wfs>limit2)).shape
            to_remove = np.any((wfs<limit1) | (wfs>limit2), axis = 1)
            #~ print to_remove.shape
            print to_remove
            ind_remove = np.where(ind)[0][to_remove]
            #~ print ind_remove
            
            sps.spike_clusters[ind_remove] = -1
            sps.check_change_on_attributes('spike_clusters')
            
            

        
        
        