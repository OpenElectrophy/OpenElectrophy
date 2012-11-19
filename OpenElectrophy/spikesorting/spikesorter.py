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
import quantities as pq

from methods import all_methods
all_method_names = dict([ (method.__name__, method) for method in all_methods ])

from matplotlib.cm import get_cmap
from matplotlib.colors import ColorConverter

from ..core import OEBase, open_db
import neo


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
        spikesorter = SpikeSorter(recordingChannelGroup)


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
    def __init__(self,rcg):
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
        # so we need a dictionnary of size NbSeg that have key=segment num and value=a slice
        # to go back from the compact array (spikeWaveforms,spikeWaveformFeatures, spikeClusters, ...)
        # to individual segments
        self.seg_spike_slices = { }
        
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
        self.cluster_names = { } # a dict of possible clusters ( keys = unique(self.spike_clusters) )
        
        # 8. Spike are attributed probalistically to clusters
        self.spike_clusters_probabilistic = None # A 2D that give for each spike the probality to belong to a cluster
                                                                    #shape = ( NbSpk, NbClus)
        
        
        # Theses attributes are for plotting and GUI purpose: colors, random subselection when cluster are too big, ...
        self.cluster_colors = { } # a dict  (keys = unique(self.spike_clusters)  and value = colors are a tuple of (r,g,b)
        self.displayed_subset_size = 100 # undensify big cluster for plotting
        self.cluster_displayed_subset = { } # a dict (keys = unique(self.spike_clusters) and value = vector of selected indexes
        self.selected_spikes = None # a vector bool to deal with spikes that are selected shpae = (NbSpk,)
        
        self.initialize_from_rcg(rcg)
    
    
    aliases = { 'recordingchannels'  : 'rcs',
                'segments' : 'segs',
                'recordingchannelgroup' : 'rcg',
                }
    
    

        
        
        
        
    def __setattr__(self, name, value):
        """
        Do aliases and check changes
        """
        name = self.aliases.get(name, name)
        if name in self.interdependent_attributes:
            self.check_change_on_attributes(name)
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

    interdependent_attributes = ['full_band_sigs', 'filtered_sigs', 'spike_index_array', 
                                                    'seg_spike_slices', 'spike_waveforms', 'waveform_features', 
                                                    'spike_clusters', 
                                                    ]

    def check_change_on_attributes(self, name):
        """
        This a home made dependency checking.
        """
        # Alvaro and Bartosz: if one day you read theses lines please do better.
        
        if not hasattr(self, name):
            # we are in __init__
            return 
        
        if name == 'spike_index_array':
            self.init_seg_spike_slices()
            object.__setattr__(self, 'spike_waveforms', None)
            object.__setattr__(self, 'waveform_features', None)
            self.spike_clusters = np.zeros(self.nb_spikes, dtype = int)
        elif name == 'spike_waveforms':
            object.__setattr__(self, 'waveform_features', None)
        elif name == 'spike_clusters':
            self.cluster_names = { }
            self.refresh_cluster_names()
        #~ self.selected_spikes is None

    def init_seg_spike_slices(self):
        start = 0
        self.seg_spike_slices = { }
        if self.spike_index_array is None: return
        for s, ind in enumerate(self.spike_index_array):
            stop = start + ind.size
            self.seg_spike_slices[s] = slice(start, stop)
            start = stop


    def __repr__(self):
        t = 'SpikeSorter for: {}\n'.format(self.rcg.name)
        t += '-'*5+'\n'
        t += 'Nb segments: {}\n'.format(len(self.segs))
        t += 'Trodnes (nb channel): {}\n'.format(self.trodness)
        
        
        if self.spike_index_array is not None:
            l = [len(pos) for pos in self.spike_index_array]
            t += 'Nb spikes total : {}\n'.format(self.nb_spikes)
            t += ('Nb spikes by segments : '+'{} '*len(self.segs)+'\n').format(*l)
        if self.spike_waveforms is not None:
            t += 'Waveform size : {}  = {} pts (={}+1+{})  \n'.format(
                                                    (self.spike_waveforms.shape[2]/self.wf_sampling_rate).rescale(pq.ms),
                                                    self.spike_waveforms.shape[2], 
                                                    self.left_sweep, self.right_sweep)
        if self.feature_names is not None:
            t += ('Waveforms features : '+"'{}', " *len(self.feature_names)+'\n').format(*self.feature_names.tolist())
        if len(self.cluster_names)>0:
            t += 'Nb of cluster : {}\n'.format(len(self.cluster_names))
            t += 'Spike by cluster : '
            for c, name in self.cluster_names.items():
                t+= "  '{}': {}  -".format(name, np.sum(self.spike_clusters==c))
            t += '\n'
        
        t += '\n'
        return t
        
    
    @property
    def trodness(self):
        return len(self.rcs)
        
    @property
    def nb_spikes(self):
        if self.spike_clusters is not None:
            return self.spike_clusters.size
        if self.spike_waveforms is not None:
            return self.spike_waveforms.shape[0]
        if self.waveform_features is not None:
            return self.waveform_features.shape[0]
        if self.spike_index_array is not None:
            l = [len(pos) for pos in self.spike_index_array]
            return np.sum(l)
        return 0
    
    def get_spike_times(self, s, c, units = 's'):
        """
        Transform spike_index_array (index of spike on signal) to times for ONE cluster in ONE segment.
        :params s: segment index
        :params c: cluster
        """
        slice = self.seg_spike_slices[s]
        clusters_in_seg = self.spike_clusters[slice]
        spike_indexes = self.spike_index_array[s]
        sr = self.sig_sampling_rate.rescale('Hz').magnitude
        t_start = self.rcs[0].analogsignals[s].t_start.rescale('s').magnitude
        spike_times = spike_indexes[clusters_in_seg == c]/sr+t_start
        if units is not None:
            spike_times = (spike_times * pq.s).rescale(units)
            
        return spike_times
        
        
        
        
        
    
    def initialize_from_rcg(self,recordingChannelGroup):
        
        # Signals
        if len(self.rcs[0].analogsignals) == len(self.segs):
            all_sigs= np.empty( (len(self.rcs), len(self.segs)), dtype = object)
            for i, rc in enumerate(self.rcs):
                for j, seg in enumerate(self.segs):
                    all_sigs[i,j] = self.rcs[i].analogsignals[j].magnitude
            self.sig_sampling_rate = self.rcs[0].analogsignals[0].sampling_rate
        else:
            all_sigs = None
        self.full_band_sigs = all_sigs
        self.filtered_sigs = all_sigs
        
        
        if len(self.rcg.units)>0:
            self.seg_spike_slices = { }
            self.spike_index_array = np.empty((len(self.segs)), dtype = object)
            pos = 0
            clusters = [ ]
            waveforms = [ ]
            features = [ ]
            for s, seg in enumerate(self.segs):
                
                nb_spike_in_segs = 0
                spike_index =  [ ]
                for u, unit in enumerate(self.rcg.units):
                    self.cluster_names[u] = unit.name
                    
                    #~ sptr = seg.spiketrains[u]
                    sptr = None
                    for sptr in seg.spiketrains:
                        if sptr.unit == unit:
                            break
                    assert sptr is not None
                    
                    nb_spike_in_segs += sptr.size
                    clusters.append(np.ones(sptr.size, dtype = int)*u)
                    
                    if all_sigs is not None:
                        ana = self.rcs[0].analogsignals[s]
                        spike_index.append(np.array((sptr.rescale('s') - ana.t_start.rescale('s'))* ana.sampling_rate.rescale('Hz'), dtype = 'i8'))
                        #~ print 's', s, 'u', u, spike_index[-1].size
                    
                    if sptr.waveforms is not None :
                        waveforms.append(sptr.waveforms.magnitude)
                        self.wf_sampling_rate = sptr.sampling_rate
                        self.left_sweep = int((sptr.left_sweep*sptr.sampling_rate).simplified.magnitude)
                        self.right_sweep = sptr.waveforms.shape[2]-1-self.left_sweep
                    if 'waveform_features' in sptr.annotations:
                        features.append(sptr.annotations['waveform_features'])
                
                self.seg_spike_slices[s] = slice(pos, pos+nb_spike_in_segs)
                pos += nb_spike_in_segs
                self.spike_index_array[s] = np.concatenate(spike_index)
                #~ print 's',s, self.spike_index_array[s].size
                
            self.spike_clusters = np.concatenate(clusters)
            #~ print self.spike_clusters.size

            if waveforms != []:
                self.spike_waveforms = np.concatenate(waveforms)
            if features != [ ]:
                self.waveform_features = np.concatenate(features)
                for n in self.waveform_features.shape[1]:
                    self.feature_names[n] = 'feature {}'.format(n)
                
    
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

    def purge_history(self):
        self.history = [ ]
        
    def apply_history_to_other(self, other):
        for step in self.history:
            print step
            other.run_step(step['methodInstance'].__class__, **step['arguments'])
    
    ## Manul clustering utilities
    def delete_one_cluster(self, c):
        raise(NotImplementedError)

    def regroup_small_cluster(self, size = 10):
        n = max(self.cluster_names.keys()) +1
        to_pop = [ ]
        for c in self.cluster_names:
            ind = self.spike_clusters == c
            if sum(ind) <size:
                self.spike_clusters[ ind ] = n
                to_pop.append(c)
        for c in to_pop:
            self.cluster_names.pop(c)
        self.cluster_names[n] = u'regrouped small cluster'
        self.refresh_colors()
    
    ####
    ## Plot utilities
    def check_display_attributes(self):
        self.refresh_cluster_names()
        self.refresh_colors()
        #self.refresh_displayed_subset(self.displayed_subset_size)
        if self.selected_spikes is None and self.nb_spikes is not None:
            self.selected_spikes = np.zeros( (self.nb_spikes), dtype = bool)
        if self.selected_spikes is not None and self.nb_spikes is not None and \
             self.selected_spikes.size != self.nb_spikes:
            self.selected_spikes = np.zeros( (self.nb_spikes), dtype = bool)
        for c in self.cluster_names.keys():
            if c not in self.cluster_displayed_subset:
                self.random_display_subset(c)

    def refresh_cluster_names(self):
        if self.spike_clusters is None:
            self.cluster_names = { }
            return
        clusters = np.unique(self.spike_clusters)
        for c in clusters:
            if c not in self.cluster_names:
                if c!=-1:
                    self.cluster_names[c] = 'cluster #{}'.format(c)
                else:
                    self.cluster_names[-1] = 'trash'

    def refresh_colors(self):
        self.refresh_cluster_names()
        self.cluster_colors = { }
        if self.spike_clusters is not None:
            cmap = get_cmap('jet' , len(self.cluster_names)+3)
            for i , c in enumerate(self.cluster_names.keys()):
                self.cluster_colors[c] = ColorConverter().to_rgb( cmap(i+2) )
        self.cluster_colors[-1] = ColorConverter().to_rgb( 'k' ) #trash
    
    def refresh_displayed_subset(self, displayed_subset_size = 100):
        self.displayed_subset_size = displayed_subset_size
        if self.spike_clusters is None: return
        self.cluster_displayed_subset = { }
        for i , c in enumerate(self.cluster_names.keys()):
            self.random_display_subset(c)
            
    def random_display_subset(self, c):
            ind, = np.where( self.spike_clusters ==c )
            np.random.shuffle(ind)
            if self.displayed_subset_size < ind.size:
                ind = ind[:self.displayed_subset_size]
            self.cluster_displayed_subset[c]  = ind
    
    def populate_recordingchannelgroup(self, save_empty = True):
        """
        Populate neo.RecordingChannelGroup  with new sorting.
        """
        rcg = self.rcg
        bl = rcg.block
        
        for u, unit in enumerate(rcg.units):
            for s, seg in enumerate(bl.segments):
                for sptr in unit.spiketrains:
                    #~ if sptr in seg.spiketrains:
                    if contains(seg.spiketrains, sptr):
                        seg.spiketrains.remove(sptr)
        rcg.units = [ ]
        
        self.refresh_cluster_names()
        for c, name in self.cluster_names.items():
            unit = neo.Unit(name = name)
            rcg.units.append(unit)
            for s, seg in enumerate(bl.segments):
                ana = self.rcs[0].analogsignals[s]
                sptr = neo.SpikeTrain(self.get_spike_times(s, c, units = 's'), t_start = ana.t_start, t_stop = ana.t_stop)
                unit.spiketrains.append(sptr)
                seg.spiketrains.append(sptr)
        
        return rcg
    
    def save_in_database(self, session, dbinfo):
        rcg = self.rcg.OEinstance
        bl = rcg.block
        
        for u, unit in enumerate(rcg.units):
            for s, seg in enumerate(bl.segments):
                for sptr in unit.spiketrains:
                    if contains(seg.spiketrains, sptr):
                        seg.spiketrains.remove(sptr)
        for u, unit in enumerate(rcg.units):
            session.delete(unit)
        session.commit()
        
        neorcg = self.populate_recordingchannelgroup()
        for u, neounit in enumerate(neorcg.units):
            unit = OEBase.from_neo(neounit, dbinfo.mapped_classes, cascade = False)
            rcg.units.append(unit)
            for s, neoseg in enumerate(neorcg.block.segments):
                neosptr = neoseg.spiketrains[u]
                sptr = OEBase.from_neo(neosptr, dbinfo.mapped_classes, cascade = False)
                unit.spiketrains.append(sptr)
                neoseg.OEinstance.spiketrains.append(sptr)
        session.commit()

        


def contains(l, s):
    # hack for bug  for :
    #    "SpikeTrain in list" 
    # when SpikeTrain is not
    
    # should be
    # return s in l
    return np.any([ s is s2 for s2 in l ])
    
    
    
    
    
    

