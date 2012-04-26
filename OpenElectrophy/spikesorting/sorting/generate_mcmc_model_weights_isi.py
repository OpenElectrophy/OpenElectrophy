# -*- coding: utf-8 -*-

"""
**generate_mcmc_model**

Generate a model in ND which should fit to the generated data.
We make the hypotesis that our data are gaussians.

Inputs: 
  * data is composed of all the unlabelled points.
  * nprior is the a priori number of elements in the mixture
  * dim is the dimension of the data (only for generate_model)
  
Outputs:
  * covs are the parameter covariance matrix of the gaussians 
  * thetas are the means of the gaussians
  * labels is the labelization of the points
  * mixture calculates the loglike probability 


"""

from pymc import flib
import pymc as pm
import pymc.distributions as dist
import numpy as np

def generate_mcmc_model_weights_isi(data,nprior):	
    '''
    Model used for as dimension as you want.
    generate_model(data,nprior,dim)
    Inputs: 
      * data is composed of all the unlabelled points (row: points, columns: coordinates).
      * nprior is the a priori number of elements in the mixture
    We use the law InverseWishart to have a matrix symetric and positive define 
    Outputs:
      * covs is a vector containing the covariances of all the gaussians in the model
      * thetas is a vector containing the means of all the gaussians in the model
      * labels is a vector containing the labels of all the data
      * mixture is a stochastic variable which calculate the loglike probability.
    '''
    
    # Initializations
    dim=data.shape[1]
    sigma0 = np.diag([1., 1.])		
    labels = []
    thetas = []
    covs = []
    prior_mean = data.mean(0)
    c0 = np.cov(data.T)
    
    for i in range(nprior): # for all the mixtures

        cov = pm.InverseWishart('C_%d' % i, n=4 , Tau=c0 ) # to get a  symetric and semidefinite positive matrix for the covariance
        theta = pm.MvNormalCov('theta_%d' % i, mu=prior_mean, C=cov)
        thetas.append(theta)
        covs.append(cov)
    
    alpha0 = 1.*np.ones(nprior) / nprior
    labels=dist.Categorical('labels', p=alpha0,size=len(data))

    @pm.stochastic(observed=True)
    def mixture(value=data, thetas=thetas, covs=covs, labels=labels):
        '''
        Return the loglike value of the gaussians parameters 
        '''
        
        loglike = 0.
        for j, (theta, cov) in enumerate(zip(thetas, covs)):
            this_data=data[labels==j]
            ch = np.linalg.cholesky(cov)# to get a triangular matrix for the covariance
            loglike += pm.mv_normal_chol_like(this_data, theta, ch) 
        
        return loglike
        
    dict_stochastics={'covs':covs,'thetas':thetas,'labels':labels,'mixture':mixture}
    
    return dict_stochastics

