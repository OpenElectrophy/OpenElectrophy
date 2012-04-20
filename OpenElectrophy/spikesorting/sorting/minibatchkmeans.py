
import numpy as np

from sklearn.cluster import MiniBatchKMeans




class SklearnMiniBatchKMeans(object):
    """
    This is faster method than classic K-mean
    
    See: http://scikit-learn.sourceforge.net/dev/modules/generated/sklearn.cluster.MiniBatchKMeans.html#sklearn.cluster.MiniBatchKMeans
    
    Arguments: are the same as original sklearn MiniBatchKMeans
    
    
    """
    
    
    name = 'Mini batch K-Means'
    def run(self, spikesorter, n_cluster =8 ,  init='k-means++', batch_size=100, 
                            max_iter=300, ):
        sps = spikesorter
        
        classifier = MiniBatchKMeans( k = n_cluster , init = init, 
                                            batch_size = batch_size, max_iter = max_iter)
        
        classifier.fit( sps.waveform_features)
        sps.spike_clusters = classifier.labels_
        
        sps.cluster_names = dict( [ (i, 'cluster #{}'.format(i))
                                    for i in np.unique(sps.spike_clusters) ] )






