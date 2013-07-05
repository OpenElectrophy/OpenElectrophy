import numpy as np

from sklearn import decomposition

class IcaFeature(object):
    """
    ICA = Independant component decomposition.
    Use sklearn module for that.
    
    
    
    """
    
    name = 'Ica Feature'
    params = [ {'name': 'n_components', 'type': 'int', 'value': 3},
                            ]
    
    def run (self, spikesorter, n_components = 3):
        sps = spikesorter
        
        wf = sps.spike_waveforms

        wf2 = wf.reshape( wf.shape[0], -1)
        
        sps.waveform_features, sps.feature_names = perform_ica(wf2,n_components)
    

def perform_ica(wf2,n_components):
    ica = decomposition.FastICA(n_components=n_components)
    ica.fit(wf2)
    features = ica.transform(wf2)
    names = np.array([ 'ica {}'.format(n) for n in range(n_components) ], dtype = 'U')
        
    return features, names
