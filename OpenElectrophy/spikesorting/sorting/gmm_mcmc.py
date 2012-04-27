
import quantities as pq
import numpy as np
import pymc as pm
import MetropolisCategorical
import generate_mcmc_model as gen

class GaussianMixtureMCMC(object):
    """
    Gaussian Mixture classification using Markov Chain Monte Carlo method with a Metropolis Hasting algorithm.
    
    Use PyMC python module
    
    Inputs:
        n_cluster: number of cluster estimated (large numbers slow down the algorithm convergence)
        n_iter: number of MCMC iteration
        n_burn: number of iteration rejected (assuming convergence is not reached)
        thin: number of step between two recordings of sampled values
        adapt_cluster_weights: if True (default) favors the creation of empty clusters and thus try to find the best number
            of cluster ( <=n_cluster )
        use_ISI: if True (default) takes into account ISI distribution of clusters by fitting it to a lognormal distribution 
            (in particular it avoids short ISIs)
        nb_draw: number of label draws between two other stochastic variable draws (Gaussian or ISI parameters for example)
    
    """
    
    name = 'GMM MCMC'
    
    def run(self, spikesorter, n_cluster = 1, n_iter = 800, n_burn=500, thin=1,verbose=0,adapt_cluster_weights=True,use_ISI=True,nb_draw=40):
        
        sps = spikesorter

        dict_data={'features':sps.waveform_features}

        if use_ISI:
            time_vector=np.empty(sps.waveform_features.shape[0])
            time_shift=0.*pq.s
            for s, ind in enumerate(sps.spike_index_array):
                time_vector[sps.seg_spike_slices[s]]=1.*ind/sps.sig_sampling_rate+time_shift
                time_shift=(time_vector[sps.seg_spike_slices[s]][-1]+1.)*pq.s # shift by the end of last segment
                # this may cause small problems to classify spikes close to the segment edges
                # and assume ISI distribution is stationary accross segments
                while np.min(np.diff(time_vector))==0.0: # this prevents null ISI (mixture's loglike evaluation would fail) 
                    time_vector[np.r_[False,np.diff(time_vector)==0.]]=time_vector[np.diff(time_vector)==0.]+1e-10
            dict_data['time_vector']=time_vector
        
        # Choose the model
        dict_stochastics=gen.generate_mcmc_model(dict_data,n_cluster,adapt_weights=adapt_cluster_weights,use_ISI=use_ISI)
        
        #Creation of the model
        sampler = pm.MCMC(dict_stochastics.values())
        sampler.use_step_method(MetropolisCategorical.MetropolisCategorical,dict_stochastics['labels'],nb_gauss=n_cluster, nb_draw = nb_draw) 
        sampler.sample(iter=n_iter,burn=n_burn,thin=thin,verbose=verbose)
        
        sps.spike_clusters=sampler.trace('labels')[-1]
        sps.cluster_names = dict( [ (i, 'cluster #{}'.format(i))
                                    for i in np.unique(sps.spike_clusters) ] )
