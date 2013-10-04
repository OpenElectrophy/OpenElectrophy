# -*- coding: utf-8 -*-
import numpy as np

import sklearn
from sklearn.mixture import GMM

from distutils import version

from .tools import apply_descending_sort_with_waveform


class SklearnGaussianMixtureEm(object):
    """
    Gaussian Mixture classification based on expectation maximization (EM) algirithm.
    Use sklearn GMM
    
    
    """
    
    
    name = 'GMM EM'
    params = [  {'name': 'n_cluster', 'type': 'int', 'value': 4},
                            {'name': 'n_iter', 'type': 'int', 'value': 20},
                            {'name': 'descending_sort_with_waveform', 'type': 'bool', 'value': True},
                            ]
    
    
    def run(self, spikesorter, n_cluster = 4, n_iter = 20,
                        descending_sort_with_waveform = True):
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
        
        if descending_sort_with_waveform:
            apply_descending_sort_with_waveform(sps)
        
        
        








