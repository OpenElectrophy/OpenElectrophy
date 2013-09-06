
import numpy as np

from .pcafeature import perform_pca
from .icafeature import perform_ica
from .allpeak import perform_peak
from .peaktovalley import perform_peak_to_valley
from .haarwavelet import perform_haar_wavelet


class CombineFeature(object):
    """
    You do not known  which feature extraction methods to use ?
    Combine them! The sorter will find the truth but in a slower way.
    Be carefull than for Gaussian methods this do necessary give gaussian
    datasets.
    
    """
    name  = 'Combined feature methods'
    params = [ {'name': 'use_peak', 'type': 'bool', 'value': True},
                            {'name': 'use_peak_to_valley', 'type': 'bool', 'value': True},
                            {'name': 'n_pca', 'type': 'int', 'value': 3},
                            {'name': 'n_ica', 'type': 'int', 'value': 3},
                            {'name': 'n_haar', 'type': 'int', 'value': 3},
                            {'name': 'sign', 'type': 'list', 'value': '-', 'values' : ['-', '+'] },
                            ]
                            


    
    def run (self, spikesorter, 
                    use_peak = True, use_peak_to_valley = True,
                    n_pca = 3, n_ica = 3, n_haar = 3, sign = '-'):

        sps = spikesorter
        wf = sps.spike_waveforms
        wf2 = wf.reshape( wf.shape[0], -1)
        
        all_features = [ ]
        all_names = [ ]
        
        if use_peak:
            features, names  = perform_peak(wf, sign)
            all_features.append(features)
            all_names.append(names)
        
        if use_peak_to_valley:
            features, names  = perform_peak_to_valley(wf)
            all_features.append(features)
            all_names.append(names)
            
        
        if n_pca>0:
            features, names, pca = perform_pca(wf2,n_pca)
            all_features.append(features)
            all_names.append(names)

        if n_ica>0:
            features, names = perform_ica(wf2,n_pca)
            all_features.append(features)
            all_names.append(names)
        
        #~ if n_haar>0:
            #~ level = 4
            #~ std_restrict = 3.
            #~ features, names = perform_haar_wavelet(wf2, n_haar, level, std_restrict)
            #~ all_features.append(features)
            #~ all_names.append(names)

        
        sps.feature_names = np.concatenate( all_names, axis = 0)
        
        sps.waveform_features = np.concatenate( all_features, axis = 1)
        if np.any(np.isnan(sps.waveform_features)):
            print 'nan::::::::::::::::'

