# -*- coding: utf-8 -*-

"""
**generate_model with possible integration of information of time (ISI density) and possible adaptation of cluster weights**

Generate a model with the integration of the ISI density which should fit to the generated data.

Inputs: 
  * dict_data is composed of all the unlabelled points ('features' and 'time_vector').
  * nprior is the a priori number of elements in the mixture
  * adapt_weights: if True, creates the 'weights' stochastic as a parent of 'labels'
  * use_ISI: if True, creates S and sigmas variable to describe ISI as lognormal function for each cluster
  
Outputs, dictionary of stochastics including keys:
  * covs
  * thetas
  * labels
  * mixture
Optional keys:
  * S
  * sigmas
  * weights
  
mixture is a stochastic variable which calculate the loglike probability.
S contains the means of the distribution of the InterSpike Interval (ISI).
sigmas contains the covariances of the distribution of the ISI.

"""

from pymc import flib
import pymc as pm
import pymc.distributions as dist
import numpy as np

def generate_mcmc_model(dict_data,nprior,adapt_weights=False,use_ISI=False):	
    '''
    Model used for as dimension as you want.
    generate_model_isi(data,nprior,adapt_weights=False,use_ISI=False)
    Inputs: 
        - dict_data is composed of all the unlabelled points (mandatory key: 'features', possible key: 'time_vector').
        - nprior is the a priori number of elements in the mixture
        - adapt_weights: if True, creates the 'weights' stochastic as a parent of 'labels'
        - use_ISI: if True, creates S and sigmas variable to describe ISI as lognormal function for each cluster
    Output, a dictionary of stochastic variables:
        - covs is a vector containing the covariances of all the gaussians in the model
        - thetas is a vector containing the means of all the gaussians in the model
        - labels is a vector containing the labels of all the data
        - mixture is a stochastic variable which calculate the loglike probability.
    Optional dictionary keys:
        - S is a vector containing all the means of the Interspike Interval (ISI) distributions.
        - sigmas is a vector containing all the covariances of the ISI distributions.
        - weights is a vector of weight on the labels
    '''
    
    features=dict_data['features']
    
    # Initializations
    prior_mean = features.mean(0)
    sigma0 = np.diag([1., 1.])
    c0 = np.cov(features.T)
    thetas = []
    covs = []
    sigmas = []
    S = []

    for j in range(nprior):# for all the mixtures
    
        cov = pm.InverseWishart('C_%d' % j, n=4 , Tau=c0 ) # to get a  symetric and semidefinite positive matrix for the covariance
        theta = pm.MvNormalCov('theta_%d' % j, mu=prior_mean, C=cov) #theta is the mean
        covs.append(cov)
        thetas.append(theta)
        
        #ISI
        if use_ISI:
            sigma = pm.Uniform('sigma_%d' %j, lower = 0.1, upper = 3)
            s = pm.Uniform('s_%d' %j, lower = 0.005, upper =3)
            sigmas.append(sigma)
            S.append(s)

    alpha0 = 1.*np.ones(nprior) / nprior
    if adapt_weights:
        weights = pm.Dirichlet('weights', theta=alpha0)
        labels=dist.Categorical('labels', p=weights,size=features.shape[0])
    else:
        labels=dist.Categorical('labels', p=alpha0,size=features.shape[0])
    
    @pm.stochastic(observed=True)
    def mixture(value = 1, thetas = thetas, covs = covs, labels = labels,sigmas = sigmas, S = S):
        '''
        Return the loglike value of the gaussians parameters and of the parameters of the ISI distributions
        '''		
        loglike = 0.
        
        for j, (theta, cov) in enumerate(zip(thetas, covs)):
            
            cluster_points = labels == j
            this_features = features[cluster_points]

            ch = np.linalg.cholesky(cov)
            loglike += pm.mv_normal_chol_like(this_features, theta, ch)

            if sigmas is not None:
                sigma = sigmas[j]
                s = S[j]           
                this_time = dict_data['time_vector'][cluster_points]
                isi = np.diff(this_time)
                loglike += pm.lognormal_like(isi, mu = s, tau = sigma)

        return loglike
            
    dict_stochastics={'covs':covs,'thetas':thetas,'labels':labels,'mixture':mixture}

    if adapt_weights:
        dict_stochastics['weights']=weights

    if use_ISI:
        dict_stochastics['S']=S
        dict_stochastics['sigmas']=sigmas
    else:
        S=None
        sigmas=None


    return dict_stochastics

