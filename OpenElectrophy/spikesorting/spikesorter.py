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
#~ from matplotlib.colors import ColorConverter
#~ import string
from . import color_utils

#~ import string

from ..core import OEBase, open_db
import neo


class SpikeSorter(object):
    """
    This is a hight level object for spike sorting.
    
    Arguments:
        * the only args is one neo.RecordingChannelGroup (see neo schema)
          This should include everything and every cases:
             1. One or several segment.
             2. Detected spike or only signal or already sorted spiketrain, ...
             
    We deliberatly choose a state vision of the spike sorting pipeline because sorting is
    not one pipeline but several possible pipeline (and nested).
    

    NbRC : number of neo.RecordingChannel inside this neo.RecordingChannelGroup
    NbSeg : numer of neo.Segment inside neo.Block
    NbSpk : number tatal of detected spikes
    NbClus : number of cluster
    
    So SpikeSorter is defined by its attributes and attributes can be grouped in category:
    
        1. **Attributes for filtering and detection**:
            
            ..notes::
                Theses following attributes are accecible by (segment) or (channel, segment).
                This fit the well the neo representation for spike sorting.
            
            * **full_band_sigs** : 2D numpy array of objects that points towards neo.AnalogSignal
                                             shape = (NbRC, NbSeg) 
            * **sig_sampling_rate** sampling_rate of signals (both filtered and full band)
            * **filtered_sigs** : 2D numpy array of objects that points towards neo.AnalogSignal
                                            shape = (NbRC, NbSeg)
            * **spike_index_array** : 1D np.array of object that point themself to np.array of indices, int64
                                                    shape = (NbSeg,)
                                                    Each array can be seen as the spike times but in sample units.
        
        2. **Attributes for waveforms, features, and cluster**:
            ..notes::
                For efficiency reasons, theses following attributes are big and comptact arrays of waveforms
                or features even if spikes belong to differents segments. This explain the reason
                of the attribute *seg_spike_slices*
        
            * **seg_spike_slices** : a dict of slices. Key is segment number, value is slice
                                                along the main axis. Example with 3 segment and 20 spikes { 0 : slice(0,7), 1: slice(7:14), 2: slice(14,20) }
            * **spike_waveforms** : 3D np.array (dtype float) that concatenate all detected spikes waveform
                                                  shape = (NbSpk, trodness, nb_point)
                                                  (this can be sliced by self.seg_spike_slices for splitting back to original neo.Segment)
            * **wf_sampling_rate**: samplingrate of theses waveform
            * **left_sweep** : nb point on left for that sweep
            * **right_sweep** : nb point on right for that sweep
            .. notes::
                self.spike_waveforms.shape[2] = self.left_sweep+ 1 + self.right_sweep
            * **waveform_features** :  2D np.array (dtype=float) to handle typical PCA or wavelet projecttion
                                                      shape = (NbSpk, ndimension)
                                                      (this can be sliced by self.seg_spike_slices for splitting back to original neo.Segment)
            * **feature_names** : an np.array (dtype = unicode) that handle label of each feature
                                                ex: ['pca1', 'pca2', 'pca3', 'pca4'] or ['max_amplitude', 'peak_to valley', ]
                                                shape = (ndimension, )
            * **spike_clusters** : 1D np.array (dtype in) to handle wich spijke belong to wich cluster
            * **cluster_names** : a dict of possible clusters ( keys = unique(self.spike_clusters) )
        
        3. **Attributes to handle the futur of spike sorting world = probalistic clustering**
            * **spike_clusters_probabilistic** : A 2D that give for each spike the probality to belong to a cluster
                                                                  shape = ( NbSpk, NbClus)
                                                                  This attr is quite speculative at the moment.
        
        4. **Attributes util when init and save**:
            * **seg_t_start** : a quantity vector that define t_start for each segment.
                                        shape: (NbSeg, )
            * **seg_t_stop** : see seg_t_start
            * **wf_units** : units for the waveforms
            
        5. **Attributes are for plotting**:
            * **cluster_colors** : a dict  (keys = unique(self.spike_clusters)  and value = colors are a tuple of (r,g,b)
            * **displayed_subset_size** : undensify big cluster for plotting
            * **cluster_displayed_subset** : a dict (keys = unique(self.spike_clusters) and value = vector of selected indexes
            * **selected_spikes** : a vector bool to deal with spikes that are selected shpae = (NbSpk,)
        

    
    ..Notes:
        SpikeSorter include some magics. (because __getattr__ and __setattr__).
        In short when one attribute is updated other attributes could also
        be automagicaly but naturaly updated. Ex: if SpikeSorter.spike_index_array
        is changed SpikeSorter.spike_waveforms and SpikeSorter.waveform_features
        are reset to None.
    
    The main idea is to apply a chain of methods to get detected and classifiyed spikes.
    This chain depend of course of the initial state.
    
    This one possible chain for the case *from full band signal to detected spikes*::
        
        spikesorter = SpikeSorter(rcg)
        spikesorter.ButterworthFilter( f_low = 200.)
        spikesorter.MedianThresholdDetection(sign= '-', median_thresh = 6.,)
        spikesorter.AlignWaveformOnPeak(left_sweep = 1*pq.ms , right_sweep = 2*pq.ms, sign = '-')
        spikesorter.PcaFeature(n_components = 4)
        spikesorter.SklearnKMeans(n_cluster = 3)
    
    
    This is a shorter chain for the case *Spike are already detected and wevefroms aligned*::
    
        spikesorter = SpikeSorter(rcg)
        spikesorter.PcaFeature(n_components = 4)
        spikesorter.HaarWaveletFeature(n_cluster = 3)
    
    See OpenElectropy.spikesorting.methods to get all possible methods.
    
    
    ..notes::
        SpikeSorter also contains attributes for plotting. So in the GUI all displaying widget
        take as only entry a SpikeSorter object.
        
    .. notes::
        SpikeSorter can also be used inside an interactive console like ipython.
    
    
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
        
        self.rcs = rcg.recordingchannels
        self.segs = rcg.block.segments
        
        
        self.history=[ ]
        
        self.full_band_sigs=None
        self.sig_sampling_rate = None
        self.filtered_sigs=None
        #~ self.spike_index_array = None
        self.set_attr_no_check( 'spike_index_array', None)
        
        self.seg_spike_slices = { }
        self.spike_waveforms = None
        self.wf_sampling_rate = None
        self.left_sweep = None
        self.right_sweep = None
        self.waveform_features = None
        self.feature_names = None
        
        self.spike_clusters = None
        self.cluster_names = { }
        self.spike_clusters_probabilistic = None
        
        self.seg_t_start = None
        self.seg_t_stop = None
        self.wf_units = None
        
        self.cluster_colors = { }
        self.displayed_subset_size = 100
        self.cluster_displayed_subset = { }
        self.selected_spikes = None
        self.active_cluster = { }
        
        self.interspike_noise_median = None
        
        #~ self.__setattr__ = self.__setattr__after
        
        self.initialize_from_rcg(rcg)
    

    
    aliases = { 'recordingchannels'  : 'rcs',
                'segments' : 'segs',
                'recordingchannelgroup' : 'rcg',
                }
    
    interdependent_attributes = ['full_band_sigs', 'filtered_sigs', 'spike_index_array', 
                                                    'seg_spike_slices', 'spike_waveforms', 'waveform_features', 
                                                    'spike_clusters', 
                                                    ]
    
    def __setattr__(self, name, value):
        """
        Do aliases and check changes
        """
        name = self.aliases.get(name, name)
        object.__setattr__(self, name, value)
        if name in self.interdependent_attributes:
            self.check_change_on_attributes(name)
        

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

    def set_attr_no_check(self , name, val):
        object.__setattr__(self, name, val)

    def check_change_on_attributes(self, name):
        """
        This a home made dependency checking.
        """
        # Alvaro and Bartosz: if one day you read theses lines please do better.
        
        if not hasattr(self, name):
            # we are in __init__
            return 
        
        if name == 'spike_index_array':
            object.__setattr__(self, 'spike_waveforms', None)
            object.__setattr__(self, 'waveform_features', None)
            if self.spike_index_array is None:
                nb_spikes = 0
            else:
                nb_spikes = np.sum([len(pos) for pos in self.spike_index_array])
            self.spike_clusters = np.zeros(nb_spikes, dtype = int)
            self.init_seg_spike_slices()
            object.__setattr__(self, 'interspike_noise_median', None)
        elif name == 'spike_waveforms':
            object.__setattr__(self, 'waveform_features', None)
            object.__setattr__(self, 'interspike_noise_median', None)
            self.recompute_cluster_center()
        elif name == 'spike_clusters':
            self.cluster_names = { }
            self.refresh_cluster_names()
            self.recompute_cluster_center()
        #~ self.selected_spikes is None

    def init_seg_spike_slices(self):
        if self.spike_index_array is None: 
            return
        #~ print 'init_seg_spike_slices',
        start = 0
        self.seg_spike_slices = { }
        for s, ind in enumerate(self.spike_index_array):
            stop = start + ind.size
            self.seg_spike_slices[s] = slice(start, stop)
            start = stop
        #~ print 'init_seg_spike_slices',self.nb_spikes, self.seg_spike_slices
        self.selected_spikes = np.zeros(self.nb_spikes, dtype = bool)


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
    
    def get_seg_from_num(self, num):
        """
        From absolut spike num get seg num
        """
        for s, sl in self.seg_spike_slices.items():
            if  num>=sl.start and num<sl.stop:
                return s
        
        
    
    def get_spike_times(self, s, c, units = 's'):
        """
        Transform spike_index_array (index of spike on signal) to times for ONE cluster in ONE segment.
        :params s: segment index
        :params c: cluster
        """
        if self.spike_index_array is not None:
            slice = self.seg_spike_slices[s]
            clusters_in_seg = self.spike_clusters[slice]
            spike_indexes = self.spike_index_array[s]
            if self.sig_sampling_rate is not None:
                sr = self.sig_sampling_rate.rescale('Hz').magnitude
            else:
                sr = self.wf_sampling_rate.rescale('Hz').magnitude
            t_start = self.seg_t_start[s].magnitude
            spike_times = spike_indexes[clusters_in_seg == c]/sr+t_start
            if units is not None:
                spike_times = (spike_times * pq.s).rescale(units)
            return spike_times
    
    def get_spike_waveforms(self, s, c):
        if self.spike_waveforms is not None:
            sl = self.seg_spike_slices[s]
            clusters_in_seg = self.spike_clusters[sl]
            all_wf = self.spike_waveforms[sl, :, :]
            wf = all_wf[clusters_in_seg == c]
            return wf
        
    def get_spike_features(self, s, c):
        if self.spike_waveforms is not None:
            sl = self.seg_spike_slices[s]
            clusters_in_seg = self.spike_clusters[sl]
            all_features = self.spike_features[sl, :, :]
            f = all_features[clusters_in_seg == c]
            return f
    
    def initialize_from_rcg(self,recordingChannelGroup):
        """
        Initialize SpikeSorter from a neo.RecordingChannelGroup
        
        Rules:
            * The number of RecordingChannel define the trodness
            * If RecordingChannels have AnalogSIgnals *full_band_sigs*, *filtered_sigs* and 
              *sig_sampling_rate* are initialized. So spikes can be detected or re-detected.
            * If RecordingChannels have SpikeTrains so all other attributes are initialized.
               In that case spikes can be (re-)featured and (re-)clustered
            * seg_t_start and seg_t_stop are taken for AnologSignals if exist otherwise
               from SpikeTrain.
        """
        
        # t_start and t_stop for each segments
        self.seg_t_start = np.nan*np.zeros(len(self.segs))*pq.s
        self.seg_t_stop = np.nan*np.zeros(len(self.segs))*pq.s
        self.wf_units = None
        
        # Signals
        self.full_band_sigs = None
        self.filtered_sigs = None
        self.sig_sampling_rate = None
        if len(self.rcs[0].analogsignals) == len(self.segs):
            self.full_band_sigs= np.empty( (len(self.rcs), len(self.segs)), dtype = object)
            for j, seg in enumerate(self.segs):
                self.seg_t_start[j] = self.rcs[0].analogsignals[j].t_start.rescale('s')
                self.seg_t_stop[j] = self.rcs[0].analogsignals[j].t_stop.rescale('s')
                for i, rc in enumerate(self.rcs):
                    self.full_band_sigs[i,j] = self.rcs[i].analogsignals[j].magnitude
                    
            self.sig_sampling_rate = float(self.rcs[0].analogsignals[0].sampling_rate.rescale('Hz').magnitude)*pq.Hz
            self.filtered_sigs = self.full_band_sigs.copy()
            self.wf_units = self.rcs[0].analogsignals[0].units
        
        cluster_names = { }
        if len(self.rcg.units)>0:
            self.seg_spike_slices = { }
            #~ self.spike_index_array = np.empty((len(self.segs)), dtype = object)
            index_array = np.empty((len(self.segs)), dtype = object)
            pos = 0
            clusters = [ ]
            waveforms = [ ]
            features = [ ]
            for s, seg in enumerate(self.segs):
                nb_spike_in_segs = 0
                spike_index =  [ ]
                for u, unit in enumerate(self.rcg.units):
                    cluster_names[u] = unit.name
                    #~ print 'u', u, unit.name, len(seg.spiketrains)
                    #~ sptr = seg.spiketrains[u]
                    # LE bug est dans to_neo car pas de spiketrain unit
                    sptr = None
                    for sptr2 in seg.spiketrains:
                        #~ print sptr2.unit, unit
                        #~ print 'init', u,  sptr2.OEinstance.id, unit.OEinstance.id
                        if sptr2.unit == unit:
                            sptr = sptr2
                            break
                    
                    assert sptr is not None
                    
                    
                    if np.isnan(self.seg_t_start[s]):
                        self.seg_t_start[s] = sptr.t_start.rescale('s')
                        self.seg_t_stop[s] = sptr.t_stop.rescale('s')
                    else:
                        if sptr.t_start<self.seg_t_start[s]: 
                            self.seg_t_start[s] = sptr.t_start.rescale('s')
                        if sptr.t_stop>self.seg_t_stop[s]:
                            self.seg_t_stop[s] = sptr.t_stop.rescale('s')
                    
                    
                    nb_spike_in_segs += sptr.size
                    clusters.append(np.ones(sptr.size, dtype = int)*u)
                    
                    # FIXME : this is ugly
                    if self.full_band_sigs is not None:
                        ana = self.rcs[0].analogsignals[s]
                        spike_index.append(np.array((sptr.rescale('s') - ana.t_start.rescale('s'))* ana.sampling_rate.rescale('Hz'), dtype = 'i8'))
                    elif sptr.sampling_rate is not None:
                        spike_index.append(np.array((sptr.rescale('s') - sptr.t_start.rescale('s'))* sptr.sampling_rate.rescale('Hz'), dtype = 'i8'))
                    
                    if sptr.waveforms is not None :
                        
                        waveforms.append(sptr.waveforms.magnitude)
                        self.wf_sampling_rate = sptr.sampling_rate
                        self.left_sweep = int((sptr.left_sweep*sptr.sampling_rate).simplified.magnitude)
                        self.right_sweep = sptr.waveforms.shape[2]-1-self.left_sweep
                        if self.wf_units is None:
                           self.wf_units =  sptr.waveforms.units
                    if 'waveform_features' in sptr.annotations:
                        features.append(sptr.annotations['waveform_features'])
                    
                    if 'color' in unit.annotations is not None and unit.annotations['color'] is not None and\
                            unit.annotations['color'] !='':
                        #~ hexcolor = unit.annotations['color'].replace('#', '')
                        #~ color = [ ]
                        #~ for i in range(3):
                            #~ color.append(float(string.atoi('0x'+hexcolor[i*2:i*2+2], 16))/255.)
                        #~ self.cluster_colors[u] = color
                        self.cluster_colors[u] = color_utils.html_to_mplRGB(unit.annotations['color'])
                        
                    
                self.seg_spike_slices[s] = slice(pos, pos+nb_spike_in_segs)
                pos += nb_spike_in_segs
                #~ self.spike_index_array[s] = np.concatenate(spike_index)
                index_array[s] = np.concatenate(spike_index)
            
            self.spike_index_array = index_array
            self.spike_clusters = np.concatenate(clusters)
            #this reset names so
            self.cluster_names = cluster_names

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
        # spike_index_array first
        for i in range(len(self.segs)):
            sl = self.seg_spike_slices[i]
            ind = (self.spike_clusters[sl] == c)
            self.spike_index_array[i] = self.spike_index_array[i][self.spike_clusters[sl] != c]
        
        keep = self.spike_clusters != c
        if self.spike_waveforms is not None:
            object.__setattr__(self, 'spike_waveforms', self.spike_waveforms[keep,:,:])
        if self.waveform_features is not None:
            object.__setattr__(self, 'waveform_features', self.waveform_features[keep,:])
        object.__setattr__(self, 'spike_clusters', self.spike_clusters[keep])
        
        self.init_seg_spike_slices()


   
    def add_one_spike(self, s, time, c = 0):
        if self.filtered_sigs is None:
            raise Exception('No signals')
        index = int(((time*pq.s - self.seg_t_start[s])*self.sig_sampling_rate).simplified.magnitude)
        i1 = index-self.left_sweep
        i2 = index+self.right_sweep+1
        if i1<0 or i2>= self.filtered_sigs[0,s].size:
            return
        
        # waveform of this new spike
        wf = [ ]
        for i in range(self.trodness):
            wf.append(self.filtered_sigs[i,s][i1:i2])
        wf = np.array( [wf])
        
        self.spike_index_array[s] = np.concatenate( (self.spike_index_array[s], [index]))
        
        # tricky insertion at the good place
        if self.spike_waveforms is not None:
            all_wf = [ ]
            for i in range(s):
                all_wf.append(self.spike_waveforms[self.seg_spike_slices[i]])
            all_wf.append(self.spike_waveforms[self.seg_spike_slices[s]])
            all_wf.append(wf)
            self.spike_waveforms = np.concatenate(all_wf)
        
        if self.spike_clusters is not None:
            all_sc = [ ]
            for i in range(s):
                all_sc.append(self.spike_clusters[self.seg_spike_slices[i]])
            all_sc.append(self.spike_clusters[self.seg_spike_slices[s]])
            all_sc.append([c])
            for i in range(s+1, len(self.segs)):
                all_sc.append(self.spike_clusters[self.seg_spike_slices[i]])
            self.spike_clusters = np.concatenate(all_sc)
            
        self.init_seg_spike_slices()
    




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
        self.refresh_colors(reset = False)
    
    
    #####
    ##  Stat utiliities
    def recompute_interspike_noise(self, n  = 1000, maxiter = 5):
        """
        this take small chunk of signal btween spike same size as waveform to estimate the noise.
        """
        
        self.interspike_noise= np.empty( (len(self.rcs), len(self.segs)), dtype = object)
        
        sr = self.sig_sampling_rate
        swl = self.left_sweep
        swr = self.right_sweep
        wsize = swl + swr + 1
        trodness = len(self.rcs)
        
        def isnear(a,b, dist):
            return np.array([ np.any(abs(b-e)<dist) for e in a ], dtype = bool)
        
        noise_chunk  = np.empty((n, trodness, wsize), dtype = float)
        ind = 0
        for s, seg in enumerate(self.segs):
            n_by_seg = max(n//len(self.segs),2)
            
            rand_size = self.full_band_sigs[0,s].size-wsize-1
            #take random pos
            pos = np.random.randint(rand_size, size = n_by_seg)+swl
            for iter in range(maxiter):
                # check is is not overlapping with spikes
                #~ print iter
                near = isnear(pos, self.spike_index_array[s], wsize*2)
                if np.sum(near)==0: break
                pos[near] = np.random.randint(rand_size, size =  np.sum(near))+swl
            pos = pos[~near]
            
            for p in pos:
                for i in range(len(self.rcs)):
                    noise_chunk[ind, i, :] = self.filtered_sigs[i,s][p-swl: p+swr+1]
                ind += 1
        
        noise_chunk = noise_chunk[:ind]
        
        self.interspike_noise_median = np.median(noise_chunk, axis = 0)
        self.interspike_noise_mad = np.median(np.abs(noise_chunk-self.interspike_noise_median), axis = 0)/  .6745
        
    
    def recompute_cluster_center(self):
        self.median_centers = { }
        self.mean_centers = { }
        self.mad_deviation = { }
        self.std_deviation = { }
        
        if self.spike_waveforms is None: return
        print 'recompute_cluster_center'
        for c in self.cluster_names:
            ind = c==self.spike_clusters
            self.median_centers[c]= np.median(self.spike_waveforms[ind,:,:], axis=0)
            self.mean_centers[c]= np.mean(self.spike_waveforms[ind,:,:], axis=0)
            self.mad_deviation[c]= np.median(np.abs(self.spike_waveforms[ind,:,:]-self.median_centers[c]), axis = 0)/  .6745
            self.std_deviation[c]= np.std(self.spike_waveforms[ind,:,:], axis=0)

    
    ####
    ## Plot utilities
    def check_display_attributes(self):
        self.refresh_cluster_names(reset = False)
        self.refresh_colors(reset = False)
        #self.refresh_displayed_subset(self.displayed_subset_size)
        if self.selected_spikes is None and self.nb_spikes is not None:
            self.selected_spikes = np.zeros( (self.nb_spikes), dtype = bool)
        if self.selected_spikes is not None and self.nb_spikes is not None and \
             self.selected_spikes.size != self.nb_spikes:
            self.selected_spikes = np.zeros( (self.nb_spikes), dtype = bool)
        for c in self.cluster_names.keys():
            if c not in self.active_cluster.keys():
                self.active_cluster[c] = True
            if c not in self.cluster_displayed_subset:
                self.random_display_subset(c)
        

    def refresh_cluster_names(self,  reset = False):
        if self.spike_clusters is None:
            self.cluster_names = { }
            return
        clusters = np.unique(self.spike_clusters)
        for c in np.setdiff1d(self.cluster_names.keys(), clusters):
            self.cluster_names.pop(c)
        
        if reset:
            self.cluster_names = { }
        
        for c in clusters:
            if c not in self.cluster_names:
                if c!=-1:
                    self.cluster_names[c] = 'cluster #{}'.format(c)
                else:
                    self.cluster_names[-1] = 'trash'

    def refresh_colors(self, reset = True):
        self.refresh_cluster_names(reset = reset)# TODO : why this
        if self.spike_clusters is  None:
            self.cluster_colors = { }
            return
        
        clusters = self.cluster_names.keys()
        for c in np.setdiff1d(self.cluster_colors.keys(), clusters):
            self.cluster_colors.pop(c)
        
        if reset:
            self.cluster_colors = { }

        cmap = get_cmap('jet' , len(self.cluster_names)+3)
        for i , c in enumerate(self.cluster_names.keys()):
            if c in self.cluster_colors: continue
            #~ self.cluster_colors[c] = ColorConverter().to_rgb( cmap(i+2) )
            self.cluster_colors[c] = color_utils.mpl_to_mplRGB( cmap(i+2) )
        #~ self.cluster_colors[-1] = ColorConverter().to_rgb( 'k' ) #trash
        self.cluster_colors[-1] = color_utils.mpl_to_mplRGB( 'k' ) #trash
        
    
    def refresh_displayed_subset(self, displayed_subset_size = 100):
        self.displayed_subset_size = displayed_subset_size
        if self.spike_clusters is None: return
        self.cluster_displayed_subset = { }
        for i , c in enumerate(self.cluster_names.keys()):
            if  self.active_cluster[c]:
                self.random_display_subset(c)
            else:
                self.cluster_displayed_subset[c]  = np.array([ ], dtype = int)
    
    def on_clusters_activation_changed(self):
        for c, activ in self.active_cluster.items():
            if activ and c not in self.cluster_displayed_subset:
                self.random_display_subset(c)
            elif activ and self.cluster_displayed_subset[c].size ==0:
                self.random_display_subset(c)
            elif not activ and self.cluster_displayed_subset[c].size >0:
                self.cluster_displayed_subset[c]  = np.array([ ], dtype = int)
    
    def random_display_subset(self, c):
        ind, = np.where( self.spike_clusters ==c )
        np.random.shuffle(ind)
        if self.displayed_subset_size < ind.size:
            ind = ind[:self.displayed_subset_size]
        self.cluster_displayed_subset[c]  = ind
    
    def populate_recordingchannelgroup(self,with_waveforms = True,
                                                                        with_features = False,
                                                                        ):
        """
        Populate neo.RecordingChannelGroup  with new sorting.
        It delete previous Unit and SpikeTrain and populate with new ones.
        
        Arguments:
            * with_waveforms : True (default) waveforms of spikes are saved included in SpikeTrain 
            * with_features : True (default) feature_waveforms of spikes are saved included in SpikeTrain 
        
        """
        rcg = self.rcg
        bl = rcg.block
        
        for u, unit in enumerate(rcg.units):
            for s, seg in enumerate(bl.segments):
                for sptr in unit.spiketrains:
                    if list_contains(seg.spiketrains, sptr):
                        list_remove(seg.spiketrains, sptr)
        rcg.units = [ ]
        
        self.refresh_cluster_names()
        self.refresh_colors()
        for c, name in self.cluster_names.items():
            #~ color = '#'
            #~ for e in self.cluster_colors[c]:
                #~ colorhex = str(hex(int(e*255))).replace('0x','')
                #~ if len(colorhex) == 1:
                    #~ colorhex = '0'+colorhex
                #~ color += colorhex
            color = color_utils.mpl_to_html(self.cluster_colors[c])

            unit = neo.Unit(name = name, color = color)
            rcg.units.append(unit)
            for s, seg in enumerate(bl.segments):
                sptr = neo.SpikeTrain(self.get_spike_times(s, c, units = 's'),
                                    t_start = self.seg_t_start[s], t_stop = self.seg_t_stop[s],
                                    color = color)
                if with_waveforms:
                    sptr.waveforms = self.get_spike_waveforms(s, c) * self.wf_units
                    sptr.sampling_rate = self.wf_sampling_rate
                    sptr.left_sweep = (self.left_sweep/self.wf_sampling_rate).rescale('s')
                if with_features:
                    sptr.annotations['waveform_features'] = self.get_spike_features(s, c)
                sptr.sort()
                
                unit.spiketrains.append(sptr)
                seg.spiketrains.append(sptr)
                sptr.unit = unit
                sptr.segment= seg
                
        
        return rcg

    
    def save_in_database(self, session, dbinfo):
        rcg = self.rcg.OEinstance
        bl = rcg.block
        
        
        for u, unit in enumerate(rcg.units):
            for s, seg in enumerate(bl.segments):
                for sptr in unit.spiketrains:
                 #   if sptr in seg.spiketrains:
                        #seg.spiketrains.remove(sptr)
                    if list_contains(seg.spiketrains, sptr):
                        sptr.neoinstance.OEinstance = None
                        list_remove(seg.spiketrains, sptr)
        for u, unit in enumerate(rcg.units):
            unit.neoinstance.OEinstance = None
            session.delete(unit)
        session.commit()
        
        neorcg = self.populate_recordingchannelgroup()
        for u, neounit in enumerate(neorcg.units):
            unit = OEBase.from_neo(neounit, dbinfo.mapped_classes, cascade = False)
            rcg.units.append(unit)
            for s, neoseg in enumerate(neorcg.block.segments):
                neosptr = neounit.spiketrains[s]
                assert neosptr.segment is neoseg, 'bug spiketrain in save'
                sptr = OEBase.from_neo(neosptr, dbinfo.mapped_classes, cascade = False)
                unit.spiketrains.append(sptr)
                neoseg.OEinstance.spiketrains.append(sptr)
                #~ print 'save',u,  sptr.times.size
        session.commit()



# some hack for python list when contain numpy.array
def list_contains(l, e):
    # should be
    # return s in l
    return np.any([ e is e2 for e2 in l ])

def list_remove(l, e):
    # should be
    # l.remove(e)
    ind,  = np.where([ e is e2 for e2 in l ])
    if ind.size>=1:
        l.pop(ind[0])

