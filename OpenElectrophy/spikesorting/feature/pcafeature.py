
import numpy as np

from sklearn import decomposition

class PcaFeature(object):
    """
    Very classic PCA projection.
    Use sklearn module for that.
    
    
    
    """
    
    name = 'Pca Feature'
    params = [ {'name': 'n_components', 'type': 'int', 'value': 4},
                            ]
    
    mpl_plots = [ 'plot_components', 'plot_explain_variance_ratio']
    
    def run (self, spikesorter, n_components = 3):
        sps = spikesorter
        
        wf = sps.spike_waveforms
        wf2 = wf.reshape( wf.shape[0], -1)
        
        names = [ 'pca {}'.format(n) for n in range(n_components) ]
        sps.feature_names = np.array(names, dtype = 'U')
        sps.waveform_features, sps.feature_names, self.pca = perform_pca(wf2,n_components)
    
    def plot_components(self, fig, sps):
        wf = sps.spike_waveforms
        wf2 = wf.reshape( wf.shape[0], -1)
        pca = self.pca
        
        n = self.pca.n_components
        m = pca.mean_
        fact = 5.
        ax = None
        for i in range(n):
            ax = fig.add_subplot(n,1,i+1, sharex = ax, sharey = ax)
            comp= pca.components_[i,:]
            ax.plot(pca.mean_, color = 'k', lw = 2)
            ax.fill_between(np.arange(m.size),m+fact*comp,m-fact*comp, alpha = .2, color = 'k')
            ax.set_ylabel('C{} {:.1f}%'.format(i, pca.explained_variance_ratio_[i]*100.))
            for j in range(wf.shape[1]):
                ax.axvline(j*wf.shape[2], color = 'r', ls = '-')
        
    
    def plot_explain_variance_ratio(self, fig, sps):
        pca = self.pca
        ax = fig.add_subplot(111)
        ax.plot(np.cumsum(pca.explained_variance_ratio_))
        ax.set_ylim(0,1.05)
            
        

def perform_pca(wf2,n_components):

    pca = decomposition.PCA(n_components=n_components, whiten=False)
    features = pca.fit_transform(wf2)
    names = np.array([ 'pca {}'.format(n) for n in range(n_components) ], dtype = 'U')
        
    return features, names, pca
