# -*- coding: utf-8 -*-

"""
**generate_model with integration of information of time (ISI density)**

Generate a model with the integration of the ISI density which should fit to the generated data.

Inputs: 
  * data is composed of all the unlabelled points.
  * nprior is the a priori number of elements in the mixture
  
Outputs:
  * covs
  * thetas
  * labels
  * mixture
  * S
  * sigmas
  
mixture is a stochastic variable which calculate the loglike probability.
S contains the means of the distribution of the InterSpike Interval (ISI).
sigmas contains the covariances of the distribution of the ISI.

"""

from pymc import flib
import pymc as pm
import pymc.distributions as dist
import numpy as np

def generate_mcmc_model_isi(dict_data,nprior):	
    '''
    Model used for as dimension as you want.
    generate_model_isi(data,nprior)
    Inputs: 
        - data is composed of all the unlabelled points.
        - nprior is the a priori number of elements in the mixture
    Outputs:
        - covs is a vector containing the covariances of all the gaussians in the model
        - thetas is a vector containing the means of all the gaussians in the model
        - labels is a vector containing the labels of all the data
        - mixture is a stochastic variable which calculate the loglike probability.
        - S is a vector containing all the means of the Interspike Interval (ISI) distributions.
        - sigmas is a vector containing all the covariances of the ISI distributions.
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
        
        #ISI
        sigma = pm.Uniform('sigma_%d' %j, lower = 0.1, upper = 3)
        s = pm.Uniform('s_%d' %j, lower = 0.005, upper =3)
        
        covs.append(cov)
        thetas.append(theta)
        sigmas.append(sigma)
        S.append(s)
        
    alpha0 = 1.*np.ones(nprior) / nprior

    labels=dist.Categorical('labels', p=alpha0,size=features.shape[0])

    @pm.stochastic(observed=True)
    def mixture(value = dict_data, thetas = thetas, covs = covs, labels = labels,sigmas = sigmas, S = S):
        '''
        Return the loglike value of the gaussians parameters and the parameters of the ISI distributions
        '''		
        loglike = 0.
        
        for j, (theta, cov) in enumerate(zip(thetas, covs)):
            
            sigma = sigmas[j]
            s = S[j]
            
            cluster_points = labels == j

            this_time = dict_data['time_vector'][cluster_points]
            this_features = features[cluster_points]
            
            isi = np.diff(this_time)

            ch = np.linalg.cholesky(cov)

            loglike += pm.mv_normal_chol_like(this_features, theta, ch) + pm.lognormal_like(isi, mu = s, tau = sigma)
        
        return loglike
        
    dict_stochastics={'covs':covs,'thetas':thetas,'labels':labels,'mixture':mixture,'S':S,'sigmas':sigmas}
    
    return dict_stochastics

