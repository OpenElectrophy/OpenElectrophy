
import numpy as np

import sklearn
from sklearn.mixture import GMM

from distutils import version



class SklearnGaussianMixtureEm(object):
    """
    Gaussian Mixture classification based on expectation maximization (EM) algirithm.
    Use sklearn GMM
    
    
    """
    
    
    name = 'GMM EM'
    
    
    def run(self, spikesorter, n_cluster = 4, n_iter = 20):
        sps = spikesorter
        # FIXME whiten
        
        if version.LooseVersion(sklearn.__version__) <= '0.10':
            classifier = GMM(n_components=n_cluster, cvtype='full')
            classifier.fit( sps.waveform_features , n_iter = n_iter)
        else:
            classifier = GMM(n_components=n_cluster, covariance_type='full', n_iter = n_iter)
            classifier.fit( sps.waveform_features)
        
        sps.spike_clusters = classifier.predict(sps.waveform_features)
        
        sps.cluster_names = dict( [ (i, 'cluster #{}'.format(i))
                                    for i in np.unique(sps.spike_clusters) ] )






