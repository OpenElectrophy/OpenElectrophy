
import numpy as np

from sklearn.cluster import KMeans




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
    
    def run(self, spikesorter, n_cluster =8 ,  init='k-means++', n_init=10,
                            max_iter=300, ):
        sps = spikesorter
        
        classifier = KMeans( k = n_cluster , init = init, 
                                            n_init = n_init, max_iter = max_iter)
        
        classifier.fit( sps.waveform_features)
        sps.spike_clusters = classifier.labels_
        
        sps.cluster_names = dict( [ (i, 'cluster #{}'.format(i))
                                    for i in np.unique(sps.spike_clusters) ] )






