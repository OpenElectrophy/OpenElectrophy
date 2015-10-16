# -*- coding: utf-8 -*-
"""

"""
import neo
from neo import (Block, Segment , AnalogSignal, SpikeTrain,
                            EventArray, EpochArray, RecordingChannel, RecordingChannelGroup)
from neo.io.baseio import BaseIO

import numpy as np
import quantities as pq

import os

import json

def signalToTrig(sig, thresh, front = True, clean = True, check = True):
    """
    Find pulse in a continuous signal.
    
    """
    if front:
        ind1, = np.where( (sig[:-1] <thresh) & (sig[1:]>=thresh) )
        ind2, = np.where( (sig[:-1] >=thresh) & (sig[1:]<thresh) )
    else:
        ind1, = np.where( (sig[:-1] >thresh) & (sig[1:]<=thresh) )
        ind2, = np.where( (sig[:-1] <=thresh) & (sig[1:]>thresh) )
    if clean:
        if ind1.size>=1 and ind2.size>=1 and ind2[0] < ind1[0]:
            ind2 = ind2[1:]
        if ind1.size>=1 and ind2.size>=1 and ind1[-1] > ind2[-1]:
            ind1 = ind1[:-1]
        if ind1.size == 1 and ind2.size==0:
            ind1= np.array([], dtype = int)
        if ind1.size == 0 and ind2.size==1:
            ind2= np.array([], dtype = int)
    if check:
        assert ind1.size == ind2.size, 'Not the same ind1 and ind2 size {} {}'.format(ind1.size, ind2.size)
    return ind1, ind2




class Neurolabscope2IO(BaseIO):
    is_readable = True
    is_writable = False

    supported_objects  = [ Segment , AnalogSignal,
                            EventArray, EpochArray, RecordingChannel, ]
    readable_objects    = [ Segment ]
    writeable_objects   = [ ]
    read_params = {Segment : [ ]}
    name               = 'Neurolabscope2'
    extensions          = [ ]
    mode = 'dir'
    def __init__(self, dirname = None) :
        BaseIO.__init__(self)
        self.dirname = dirname

    def read_segment(self,cascade = True, lazy = False,digital_channels = 'all'):
        json_file = os.path.join(self.dirname, 'info.json')
        info = json.load(open(json_file, 'r'))
        #~ print info
        
        for stream in info['streams']:
            #~ print stream

            if stream['stream_type'] == 'AnalogSignalSharedMemStream':
                reader = neo.RawBinarySignalIO(filename = os.path.join(self.dirname,stream['name']+'.raw'))
                seg = reader.read_segment(sampling_rate = stream['sampling_rate']*pq.Hz,
                                                        t_start = 0.*pq.s,
                                                        unit = pq.V,
                                                        nbchannel = stream['nb_channel'],
                                                        dtype = stream['dtype'],
                                                        )
                for i, anasig in enumerate(seg.analogsignals):
                    anasig.annotations['channel_name'] = anasig.name = stream['channel_names'][i]
                    anasig.channel_index = stream['channel_indexes'][i]
                
                    if 'first_pos' in info and stream['name'] in info['first_pos']:
                        anasig._nls2_first_pos = info['first_pos'][stream['name']]
                     
                    
                
            elif stream['stream_type'] == 'DigitalSignalSharedMemStream':
                dim1 = int(np.ceil(stream['nb_channel']/8.))
                arr = np.memmap(filename = os.path.join(self.dirname,stream['name']+'.raw'), mode = 'r', dtype = np.uint8)
                arr = arr.reshape(-1, dim1)
                if digital_channels == 'all':
                    digital_channels = range(stream['nb_channel'])
                for chan in digital_channels:
                    b = chan//8
                    mask = 1<<(chan%8)
                    sig = (arr[:,b]&mask>0)#.astype(float)
                    
                    thresh = .5
                    #~ print stream['channel_names'][chan]
                    ind1, ind2 = signalToTrig(sig, thresh, front = True, clean = True, check = False)
                    if ind1.size == ind2.size+1:
                        ind2 = np.concatenate( [ind2, ind1[-1:]], axis = 0)
                        
                    ea = neo.EpochArray(times = ind1/float(stream['sampling_rate'])*pq.s,
                                                    durations =(ind2-ind1)/float(stream['sampling_rate'])*pq.s,
                                                    name = stream['channel_names'][chan],
                                                    channel_index = chan)
                    seg.epocharrays.append(ea)
        
        if info['annotations'] is not None:
            seg.annotate(**info['annotations'])
        return seg



