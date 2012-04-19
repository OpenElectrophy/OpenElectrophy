# -*- coding: utf-8 -*-
"""
This implements a high level object for spike sorting.

It is contructed to manipulate to neo object, 
see here for details: http://packages.python.org/neo/usecases.html

The main idea is we have a set of state during the spike sorting
and spiksorter methods can switch the obejct from one state to the other.

Current states are:
  1. Full band raw signals
  2. Filtered signals
  3. Detected spike times
  4. Aligned spike waveforms
  5. Projected spike waveforms
  6. Cluster definition/estimation
  7. Spikes (all) attributed to clusters
  [8. Spike are attributed probalistically to clusters] Experimental

Traditional work flow was: 
  * full band: 1->2->3->4->5->7
  * filtered band: 2->3->4->5->7
  * from detected spikes: 4->5->7
  
New methods can switch from arbitrary states. Examples:
  * Franke: 2->7
  * STO method: 1->4
  * Wood: 1->8
  * MCMC: 5->8(->7)

Each class from the spike sorting framework must take the spikesorter as input,
implement a single method that switches from one state to another.
A typical computing class must:
  * declare doc for ref (bibliographic)
  * give initial and final states
  * propose a single computing method that takes the SpikeSorter itself as input

Of course all OE0.2 methods can be clearly reimplemented here:
  * filtering 1->2
  * detection 2->3
  * extraction 3->4
  * ...

At creation time, spikesorter must be initialized with a given state.

All spike sorting steps can be traced and applied directly to another RecordingChannelGroup

SpikeSorter must be well adapted both to script and GUI.




Worst memory scenario
------------------------------------
I want to filter, detect extract and sort all at once this:

128 electrode
10 kHz sampling
24h recording
4 unit (=neuron) per channel
each unit have a rate of 10 hz

Theses are th bigest and need to be on disk (memmap or hdf5) :
fullBandAnaSig with dtype (float32) = 4*128*10e3*3600*24/1.e9 = 442 Go 
filteredBandAnaSig with dtype (float32) = 4*128*10e3*3600*24/1.e9 = 442 Go 

Theses can be in memory I think:
spikeIndexArray (int64) = 8 * 128*10*3600*24/1.e9 = .88 Go
spikeWaveformFeatures(float32) = 4 * 128*10*3600*24*30/1.e9 = 1.7 Go
spikeClusters ( int32)  = 4*128*10*3600*24/1.e9 = .44 Go

This I do not know memory :
spikeWaveforms (float32) = 4 * 128*10*3600*24*30/1.e9 = 13 Go


So disk need is about 1To.
And memory nedd is about 16Go.

Note that some algo do filtering+detection9+extraction on the fly so you do not need filteredBandAnaSig (442 Go)




"""

import copy
import datetime
import numpy as np

from methods import all_methods
all_method_names = dict([ (method.__name__, method) for method in all_methods ])


class SpikeSorter(object):
    """
    
    
    Example::
        
        import quantitites as pq
        from OpenElectrophy.spikesorting import (generate_block_for_sorting, SpikeSorter)
            
        # read or create datasets
        bl = generate_block_for_sorting(nb_unit = 6,
                                    duration = 5.*pq.s,
                                    noise_ratio = 0.2,
                                    )
        recordingChannelGroup = bl.recordingchannelgroups[0]
        spikesorter = SpikeSorter(recordingChannelGroup,
                                initialState='fullBandSignal')


        # Apply a chain
        spikesorter.ButterworthFilter( f_low = 200.)
        # equivalent to
        # spikesorter.run_step(ButterworthFilter, f_low = 200.)
        
        
        spikesorter.MedianThresholdDetection(sign= '-',
                                            median_thresh = 6,
                                            sweep_clean_method = 'fast',
                                            sweep_clean_size = 0.8*pq.ms,
                                            consistent_across_channels = True,
                                            consistent_across_segments = True,
                                            )
        spikesorter.AlignWaveformOnDetection(left_sweep = 1*pq.ms ,
                                                right_sweep = 2*pq.ms)
        spikesorter.PcaFeature(n_components = 6)
        spikesorter.SklearnGaussianMixtureEm(n_cluster = 12, n_iter = 200 )
    
    """
    def __init__(self,rcg,initial_state='fullBandSignal'):
        """
        
        """
        self.rcg = rcg
        
        # for convinience
        self.rcs = rcg.recordingchannels
        self.segs = rcg.block.segments
        
        
        self.history=[ ]
        
        # Each state comes with its own variables:
        
        # NbRC : number of neo.RecordingChannel inside this neo.RecordingChannelGroup
        # NbSeg : numer of neo.Segment inside neo.Block
        # NbSpk : number tatal of detected spikes
        # NbClus : number of cluster
        
        # 1. Full band raw signals
        self.full_band_sigs=None # 2D numpy array of objects that points towards neo.AnalogSignal
                                            # shape = (NbRC, NbSeg) 
        self.sig_sampling_rate = None
        
        # 2. Filtered signals
        self.filtered_sigs=None # 2D numpy array of objects that points towards neo.AnalogSignal
                                            # shape = (NbRC, NbSeg) 
        # 3. Detected spike times
        self.spike_index_array = None # 1D np.array of object that point themself to np.array of indices, int64
                                                        #shape = (NbSeg,)
        
        # After that point data are concatenated in compact arrays
        # even if they come from different segment for efficiency reason, PCA need arrays compact)
        # so we need a dictionnary of size NbSeg that have key=neo.Segment and value=a slice
        # to go back from the compact array (spikeWaveforms,spikeWaveformFeatures, spikeClusters, ...)
        # to individual segments
        self.seg_spike_slices = None
        
        # 4. Aligned spike waveforms
        self.spike_waveforms = None # 3D np.array (dtype float) that concatenate all detected spikes waveform
                                                         # shape = (NbSpk, trodness, nb_point)
                                                         # this can be sliced by self.spikeMembership for splitting back to original neo.Segment
        self.wf_sampling_rate = None # samplingrate of theses waveform
        self.left_sweep = None # nb point on left for that sweep
        self.right_sweep = None # nb point on right for that sweep (this could be a propertis!)
        # self.spikeWaveforms.shape[2] = self.leftSweep+ 1 + self.rightSweep
        
        
        # 5. Projected spike waveforms
        self.waveform_features = None # 2D np.array (dtype=float) to handle typical PCA or wavelet projecttion
                                                            # shape = (NbSpk, ndimension)
        self.feature_names = None # an np.array (dtype = unicode) that handle label of each feature
                                                    # ex: ['pca1', 'pca2', 'pca3', 'pca4'] or ['max_amplitude', 'peak_to valley', ]
                                                    # shape = (ndimension, )
        
        #6. Cluster definition/estimation/after learning
        # this state is not very precise in our mind now
        # this could be 'list of template waveform' or 'cluster centroid + covariance' of gaussian or ..
        # this is method dependant and to be discuss
        
        # 7. Spikes (all) attributed to clusters
        self.spike_clusters = None # 1D np.array (dtype in) to handle wich spijke belong to wich cluster
                                                    # shape = (NbSpk, )
        self.cluster_names = { } # a dict of possible clusters ( keys = unique(self.spikeClusters)
        
        # 8. Spike are attributed probalistically to clusters
        self.spike_clusters_probabilistic = None # A 2D that give for each spike the probality to belong to a cluster
                                                                    #shape = ( NbSpk, NbClus)
        
        self.initialize_state(rcg,state=initial_state)
        
    
    aliases = { 'recordingchannels'  : 'rcs',
                'segments' : 'segs',
                'recordingchannelgroup' : 'rcg',
                }
    
    def __setattr__(self, name, value):
        """
        Do aliases
        """
        name = self.aliases.get(name, name)
        object.__setattr__(self, name, value)

    def __getattr__(self, name):
        """
        Do aliases
        and auto run step
        
        Ex::
            spikesorter.PcaFeature(n_components = 6)
            #is equivalent to
            spikesorter.run_step(PcaFeature, n_components = 6)
            
        """
        if name in all_method_names:
            class step_caller(object):
                def __init__(self, spikesorter, name):
                    self.method = all_method_names[name]
                    self.spikesorter = spikesorter
                
                def __call__(self, **kargs):
                    self.spikesorter.run_step(self.method, **kargs)
            return step_caller(self, name)
        
        
        if name == "aliases":
            raise AttributeError
        name = self.aliases.get(name, name)
        return object.__getattribute__(self, name)
    
    def initialize_state(self,recordingChannelGroup, state):
        self.state=state
        
        if state=='full_band_signal':
            self.full_band_sigs = np.empty( (len(self.rcs), len(self.segs)),
                                                dtype = object)
            for i, rc in enumerate(self.rcs):
                for j, seg in enumerate(self.segs):
                    self.full_band_sigs[i,j] = self.rcs[i].analogsignals[j].magnitude
            self.sig_sampling_rate = self.rcs[0].analogsignals[0].sampling_rate
            
            
            
        elif state=='filtered_band_signal':
            pass # self.filteredBandAnaSig = TODO...
        # And so on
    
    
    def run_step(self, method, **kargs):
        """
        Arguments:
            * methodClass: one of the class offered by the framework
            * **kargs: parameter specific to that class
        """
        
        method_instance = method()
        
        step = dict(
                        # we keep trace of the instance because some method need
                        # to be continued like  MCMC (10000 loop, a view, 5000 loop a second viwe...)
                        methodInstance = method_instance,
                        
                        arguments = copy.deepcopy(kargs), 
                        starting_time = datetime.datetime.now()
                        )
        
        self.history.append(step)
        
        
        method_instance.run(spikesorter = self, **kargs)
        
        
        step['end_time'] = datetime.datetime.now()
        
        return step

    def purge_histort(self):
        self.history = [ ]
        
    def apply_history_to_other(self, other):
        
        for step in history:
            other.run_step(step['methodInstance'].__class__, **step['arguments'])
            
            
        
        



