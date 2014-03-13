import numpy as np

from sklearn.cluster import KMeans


from .tools import apply_descending_sort_with_waveform

class SklearnKMeans(object):
    """
    This is just a wrapper to the most popular sorting algo : k-means
    The use sklearn implementation.
    
    See: http://scikit-learn.sourceforge.net/dev/modules/generated/sklearn.cluster.KMeans.html
    
    Arguments: are the same as original sklearn KMeans
    
    See also:
        sklearn propose also MiniBatchKMeans with is faster for big datasets.
    
    """
    
    
    name = 'K-Means'
    params = [  {'name': 'n_cluster', 'type': 'int', 'value': 8},
                            {'name': 'init', 'type': 'list', 'value': 'k-means++', 'values':['k-means++', 'random']},
                            {'name': 'n_init', 'type': 'int', 'value': 10},
                            {'name': 'max_iter', 'type': 'int', 'value': 300},
                            {'name': 'descending_sort_with_waveform', 'type': 'bool', 'value': True},
                            ]

    
    def run(self, spikesorter, n_cluster =8 ,  init='k-means++', n_init=10,
                            max_iter=300, descending_sort_with_waveform = True):
        sps = spikesorter
        
        classifier = KMeans( n_clusters = n_cluster , init = init, 
                                            n_init = n_init, max_iter = max_iter)
        
        classifier.fit( sps.waveform_features)
        sps.spike_clusters = classifier.labels_
        
        sps.cluster_names = dict( [ (i, 'cluster #{}'.format(i))
                                    for i in np.unique(sps.spike_clusters) ] )

        if descending_sort_with_waveform:
            apply_descending_sort_with_waveform(sps)





