import numpy as np
from scipy import stats
import pywt


class HaarWaveletFeature(object):
    """
    This method use a harra wavelet for decomposition of the waveform and 
    perform a KS coefficient to select best feature.
    
    Introduced by Quiroga in 2004.
    
    This code is taken from 
    `wave_clus <http://www.vis.caltech.edu/~rodri/Wave_clus/Wave_clus_home.htm>`_ 
    matlab package release under GPL by Quiroga.
    
    You can have the original version in the file wave_features_wc.m

    
    """
    
    name = 'Haar wavelet Feature'
    params = [ {'name': 'n_components', 'type': 'int', 'value': 3},
                                {'name': 'level', 'type': 'int', 'value': 4},
                                {'name': 'std_restrict', 'type': 'float', 'value': 3.},
                            ]

    
    def run (self, spikesorter, n_components = 3, level = 4, std_restrict = 3.,):

        sps = spikesorter
        
        wf = sps.spike_waveforms
        wf2 = wf.reshape( wf.shape[0], -1)
        
        sps.waveform_features, sps.feature_names = perform_haar_wavelet(wf2,n_components,level, std_restrict)
    

def perform_haar_wavelet(wf2,n_components, level, std_restrict):

    coeffs = [ ]
    for i in range(wf2.shape[0]):
        coeff = np.concatenate(pywt.wavedec(wf2[i,:] , 'haar' ,mode = 'sym', level = level))
        if i ==0:
            coeffs = np.empty((wf2.shape[0] , coeff.shape[0]))
        coeffs[i,:] = coeff

    keep = np.sum(coeffs==0. , axis=0) != wf2.shape[0]
    coeffs = coeffs[:,keep]
    # calcul tes ks for all coeff
    ks_score = np.zeros((coeffs.shape[1]))
    for j in range(coeffs.shape[1]):
        # keep only coeff inside m +- restrict std
        s = np.std(coeffs[:,j], axis=0)*std_restrict
        m = np.mean(coeffs[:,j], axis=0)
        ind_selected = (coeffs[:,j]>=m-s) & (coeffs[:,j]<=m+s)
        if np.sum(ind_selected) >= 10:
            x = coeffs[ind_selected, j]
            zscored = (x-np.mean(x))/np.std(x)
            D, pvalue = stats.kstest( zscored,'norm')
            ks_score[j] = D
            
    
    # keep only the best ones
    ind_sorted = np.argsort(ks_score)[::-1]
    ind_sorted = ind_sorted[:n_components]
    
    features = coeffs[:, ind_sorted]
    

    
    names = np.array([ 'wt {}'.format(n) for n in range(features.shape[1]) ], dtype = 'U')
        
    return features, names
