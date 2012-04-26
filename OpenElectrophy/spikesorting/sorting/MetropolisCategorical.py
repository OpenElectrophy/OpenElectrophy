# -*- coding: utf-8 -*-
"""
**Class MetropolisCategorical(pm.DiscreteMetropolis)**

This class is a specific Discrete Metropolis class for the labels.
Instead of 1 label, nb_draw labels are changed for one iteration of the sampling.

"""

import pymc as pm
import numpy as np
from numpy import ones, log, array
from numpy.random import randint, random
from pymc.Node import ZeroProbability

class MetropolisCategorical(pm.DiscreteMetropolis):
    
    """ This a method that is useful if you want to sample an array element one by one 
    and if you want to take more than one sample in each step
    """
    
    def __init__(self, stochastic, scale=1., proposal_sd=None, proposal_distribution="Poisson", positive=False, verbose=None,tally=True, rej = False, nb_gauss = 2, nb_draw = 40):
        '''
        DiscreteMetropolis class initialization. initialization of the superclass DiscreteMetropolis
        '''
        
        # Initialize superclass
        pm.DiscreteMetropolis.__init__(self, stochastic, scale=scale, proposal_sd=proposal_sd, proposal_distribution=proposal_distribution, verbose=verbose, tally=tally)
        self.len_stoch=len(self.stochastic.value)
        self.nb_gauss=nb_gauss
        self.nb_draw=nb_draw
        self.rej = False
            
    def propose(self):

        '''
        Update each stochastic individually.
        '''
        
        # coeff is an array, it contains a random number between 0 and the size of the stochastic. This number will be the indice of the changed value
        coeff = np.random.randint(0,self.len_stoch-1)

        #new_value is the copy of the distribution, we will change a value of new_value
        new_value=list(self.stochastic.value)
        
        #list_new_coef is the same distribution as stochastic to respect the probability of having a value
        list_new_coeff=pm.distributions.Categorical('list_new_coeff',p=1.*ones(self.nb_gauss)/self.nb_gauss,size=self.len_stoch)

        #We take only one coeff of list_new_coeff to replace one coeff in new_value
        new_value[coeff]=int(list_new_coeff.random()[coeff])
        
        self.stochastic.value=array(new_value)
        
    def step(self):
        """
        The default step method applies if the variable is floating-point
        valued, and is not being proposed from its prior.
        """

        # Probability and likelihood for s's current value:
        for i in range(self.nb_draw):

            if self.verbose>1:
                print
                print self._id + ' getting initial logp.'
            

            if self.proposal_distribution == "Prior":
                logp = self.loglike
            else:
                logp = self.logp_plus_loglike

            if self.verbose>1:
                print self._id + ' proposing.'

            # Sample a candidate value
            self.propose()
            
            # Probability and likelihood for s's proposed value:
            try:
                if self.proposal_distribution == "Prior":
                    logp_p = self.loglike
                    # Check for weirdness before accepting jump
                    self.stochastic.logp
                else:
                    logp_p = self.logp_plus_loglike

            except ZeroProbability:

                # Reject proposal
                if self.verbose>1:
                    print self._id + ' rejecting due to ZeroProbability.'
                self.reject()

                # Increment rejected count
                self.rejected += 1

                if self.verbose>1:
                    print self._id + ' returning.'
                return

            if self.verbose>1:
                print 'logp_p - logp: ', logp_p - logp

            HF = self.hastings_factor()

            # Evaluate acceptance ratio
            
            if log(random()) > logp_p - logp + HF:
                
                # Revert s if fail
                self.reject()
                self.rej = True
                
                # Increment rejected count
                self.rejected += 1
                if self.verbose > 1:
                    print self._id + ' rejecting'
            else:
                # Increment accepted count
                self.rej = False
                self.accepted += 1

                if self.verbose > 1:
                    print self._id + ' accepting'

            if self.verbose > 1:
                print self._id + ' returning.'