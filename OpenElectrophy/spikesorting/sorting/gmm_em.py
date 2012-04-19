
import numpy as np

import sklearn
from sklearn.mixture import GMM


class SklearnGaussianMixtureEm:
    """
    Gaussian Mixture classification based on expectation maximization (EM) algirithm.
    Use sklearn GMM
    
    
    """
    
    
    name = 'GMM EM'
    
    
    def run(self, spikesorter, n_cluster = 4, n_iter = 20):
        s = spikesorter
        # FIXME whiten
        
        if sklearn.__version__ == '0.10':
            classifier = GMM(n_components=n_cluster, cvtype='full')
        elif sklearn.__version__ == '0.11':
            classifier = GMM(n_components=n_cluster, covariance_type='full')
        # cvtype is sklearn 0.10
        # covariance_type is for sklearn 0.11
        
        classifier.fit( s.spikeWaveformFeatures , n_iter = n_iter)
        s.spikeClusters = classifier.predict(s.spikeWaveformFeatures)
        
        s.clusterNames = dict( [ (i, 'cluster #{}'.format(i)) for i in np.unique(s.spikeClusters) ] )






