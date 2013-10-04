
import numpy as np

from sklearn.cluster import MiniBatchKMeans

from .tools import apply_descending_sort_with_waveform


class SklearnMiniBatchKMeans(object):
    """
    This is faster method than classic K-mean
    
    See: http://scikit-learn.sourceforge.net/dev/modules/generated/sklearn.cluster.MiniBatchKMeans.html#sklearn.cluster.MiniBatchKMeans
    
    Arguments: are the same as original sklearn MiniBatchKMeans
    
    
    """
    
    
    name = 'Mini batch K-Means'
    params = [  {'name': 'n_cluster', 'type': 'int', 'value': 8},
                            {'name': 'init', 'type': 'list', 'value': 'k-means++', 'values':['k-means++', 'random']},
                            {'name': 'batch_size', 'type': 'int', 'value': 100},
                            {'name': 'max_iter', 'type': 'int', 'value': 300},
                            {'name': 'descending_sort_with_waveform', 'type': 'bool', 'value': True},
                            ]
    
    def run(self, spikesorter, n_cluster =8 ,  init='k-means++', batch_size=100, 
                            max_iter=300, descending_sort_with_waveform = True):
        sps = spikesorter
        
        classifier = MiniBatchKMeans( k = n_cluster , init = init, 
                                            batch_size = batch_size, max_iter = max_iter)
        
        classifier.fit( sps.waveform_features)
        sps.spike_clusters = classifier.labels_
        
        sps.cluster_names = dict( [ (i, 'cluster #{}'.format(i))
                                    for i in np.unique(sps.spike_clusters) ] )

        if descending_sort_with_waveform:
            apply_descending_sort_with_waveform(sps)






