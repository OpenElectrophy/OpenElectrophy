



import numpy as np

from sklearn.cluster import MeanShift, estimate_bandwidth

from .tools import apply_descending_sort_with_waveform


class SklearnMeanShift(object):
    """
    This use the MeanShift implementation of sklearn.
    
    See: http://scikit-learn.sourceforge.net/dev/modules/generated/sklearn.cluster.MeanShift.html#sklearn.cluster.MeanShift
    
    Arguments: are the same as original sklearn MeanShift.
    
    
    
    ref: Dorin Comaniciu and Peter Meer, Mean Shift: A robust approach toward
        feature space analysis. IEEE Transactions on Pattern Analysis and
        Machine Intelligence. 2002. pp. 603-619.
    
    """
    
    
    name = 'Mean Shift'
    params = [  {'name': 'quantile', 'type': 'float', 'value': 0.2},
                            {'name': 'n_samples', 'type': 'int', 'value': 500},
                            {'name': 'bin_seeding', 'type': 'bool', 'value': True},
                            {'name': 'cluster_all', 'type': 'bool', 'value': False},
                            {'name': 'descending_sort_with_waveform', 'type': 'bool', 'value': True},
                            ]
                            
    def run(self, spikesorter, quantile=0.2, n_samples=500,
                            bin_seeding=True, cluster_all=False,
                            descending_sort_with_waveform = True):
        
        sps = spikesorter
        
        bandwidth = estimate_bandwidth(sps.waveform_features,
                                quantile=quantile, n_samples=n_samples)

        classifier = MeanShift(bandwidth=bandwidth, bin_seeding=bin_seeding,
                                            cluster_all = cluster_all)
        classifier.fit(sps.waveform_features)

        sps.spike_clusters = classifier.labels_
        
        sps.cluster_names = dict( [ (i, 'cluster #{}'.format(i))
                                    for i in np.unique(sps.spike_clusters) ] )

        if descending_sort_with_waveform:
            apply_descending_sort_with_waveform(sps)






