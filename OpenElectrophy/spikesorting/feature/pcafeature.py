
import numpy as np

from sklearn import decomposition

class PcaFeature:
    """
    Very classic PCA projection.
    Use sklearn module for that.
    
    
    
    """
    
    name = 'Pca Feature'
    
    def run (self, spikesorter, n_components = 3):
        s = spikesorter
        
        wf = s.spikeWaveforms

        wf2 = wf.reshape( wf.shape[0], -1)
        
        pca = decomposition.PCA(n_components=n_components)
        s.spikeWaveformFeatures = pca.fit_transform(wf2)
        
        names = [ 'pca {}'.format(n) for n in range(n_components) ]
        s.featureNames = np.array(names, dtype = 'U')
        
    