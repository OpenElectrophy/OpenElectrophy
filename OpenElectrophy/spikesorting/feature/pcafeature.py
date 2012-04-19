
import numpy as np

from sklearn import decomposition

class PcaFeature(object):
    """
    Very classic PCA projection.
    Use sklearn module for that.
    
    
    
    """
    
    name = 'Pca Feature'
    
    def run (self, spikesorter, n_components = 3):
        sps = spikesorter
        
        wf = sps.spike_waveforms

        wf2 = wf.reshape( wf.shape[0], -1)
        
        pca = decomposition.PCA(n_components=n_components)
        sps.waveform_features = pca.fit_transform(wf2)
        
        names = [ 'pca {}'.format(n) for n in range(n_components) ]
        sps.feature_names = np.array(names, dtype = 'U')
    
    