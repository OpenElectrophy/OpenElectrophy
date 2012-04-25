
import numpy as np
import pymc as pm
import MetropolisCategorical
import generate_model_2d


class GaussianMixtureMCMC(object):
    """
    Gaussian Mixture classification using Markov Chain Monte Carlo method with a Metropolis Hastin algorithm.
    
    Use PyMC python module
    
    """
    
    name = 'GMM MCMC'
    
    def run(self, spikesorter, n_cluster = 1, n_iter = 800, n_burn=500, thin=1,verbose=0):
        
        sps = spikesorter
        
        covs, thetas, labels,mixture = generate_model_2d.generate_model(sps.waveform_features,nprior,dim)
        
        #Creation of the model
        sampler = pm.MCMC([mixture,covs,thetas,labels])
        sampler.use_step_method(MetropolisCategorical.MetropolisCategorical,labels,nb_gauss=n_cluster, nb_draw = 40) 
        sampler.sample(iter=n_iter,burn=n_burn,thin=thin,verbose=verbose)
        
        sps.spike_clusters=sampler.trace('labels')[-1]
        sps.cluster_names = dict( [ (i, 'cluster #{}'.format(i))
                                    for i in np.unique(sps.spike_clusters) ] )
