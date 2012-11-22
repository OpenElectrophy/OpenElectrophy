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

global covs_save,sigmas_save,S_save,theta_save

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
    
    global theta_save
    
    features=dict_data['features']

    # Initializations
    prior_mean = features.mean(0)
    c0 = np.cov(features.T)
    thetas = []
    covs = []
    sigmas = []
    S = []

    for j in range(nprior):# for all the mixtures
    
        # !!! InverseWishart has been temporarily removed from PYMC, thus cov now follow a Wishart distribution 
        cov = pm.Wishart('C_%d' % j, n=features.shape[1]+2 , Tau=c0 ) # to get a  symetric and semidefinite positive matrix for the covariance
        theta = pm.MvNormalCov('theta_%d' % j, mu=prior_mean, C=cov) #theta is the mean
        covs.append(cov)
        thetas.append(theta)
        
        #ISI
        if use_ISI:
            sigma = pm.Uniform('sigma_%d' %j, lower = 0., upper = 10)
            s = pm.Uniform('s_%d' %j, lower = -8., upper =2.)
            sigmas.append(sigma)
            S.append(s)
        else:
            S=None
            sigmas=None

    print nprior
    #~ rand_init=np.random.randint(nprior,size=features.shape[0])
    alpha0 = 1.*np.ones(nprior) / nprior
    #~ print rand_init
    if adapt_weights:
        beta0 = 1.*np.ones(nprior-1) / nprior
        weights = pm.Dirichlet('weights', theta=alpha0,value=beta0)
        labels=dist.Categorical('labels', p=weights,size=features.shape[0],rseed=True)
    else:
        labels=dist.Categorical('labels', p=alpha0,size=features.shape[0],rseed=True)
    
    theta_save=thetas
    
    @pm.stochastic(observed=True,dtype=object)
    def mixture(value = dict_data, thetas = thetas, covs = covs, labels = labels,sigmas = sigmas, S = S):
        '''
        Return the loglike value of the gaussians parameters and of the parameters of the ISI distributions
        '''		
        loglike = 0.
        
        print "a"

        global theta_save
        
        print (thetas!=theta_save)
        if (thetas!=theta_save).any():

            print "b"
            for j, (theta, cov) in enumerate(zip(thetas, covs)):
                
                cluster_points = labels == j
                this_features = value['features'][cluster_points]

                ch = np.linalg.cholesky(cov)
                loglike += pm.mv_normal_chol_like(this_features, theta, ch)

                if sigmas is not None:
                    this_time = value['time_vector'][cluster_points]
                    isi = np.diff(this_time)
                    if isi.size>0:
                        loglike += pm.lognormal_like(isi, mu = S[j], tau = sigmas[j])
                        
            theta_save=thetas

        else:
            
            for j, (theta, cov) in enumerate(zip(thetas, covs)):
                
                cluster_points = labels == j
                this_features = value['features'][cluster_points]

                ch = np.linalg.cholesky(cov)
                loglike += pm.mv_normal_chol_like(this_features, theta, ch)

                if sigmas is not None:
                    this_time = value['time_vector'][cluster_points]
                    isi = np.diff(this_time)
                    if isi.size>0:
                        loglike += pm.lognormal_like(isi, mu = S[j], tau = sigmas[j])

        
        #~ print "mixture ! ", loglike
        
            
        return loglike
            
    dict_stochastics={'covs':covs,'thetas':thetas,'labels':labels,'mixture':mixture}

    if adapt_weights:
        dict_stochastics['weights']=weights

    if use_ISI:
        dict_stochastics['S']=S
        dict_stochastics['sigmas']=sigmas

    return dict_stochastics

