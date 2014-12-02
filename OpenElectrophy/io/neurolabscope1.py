# -*- coding: utf-8 -*-
"""

"""
import neo
from neo import (Block, Segment , AnalogSignal, SpikeTrain,
                            EventArray, EpochArray, RecordingChannel, RecordingChannelGroup)
from neo.io.baseio import BaseIO

import numpy as np
import quantities as pq

import datetime

import os

import json

import re



class Neurolabscope1IO(BaseIO):
    is_readable = True
    is_writable = False

    supported_objects  = [ Segment , AnalogSignal,
                            RecordingChannel, ]
    readable_objects    = [ Segment ]
    writeable_objects   = [ ]
    read_params = {Segment : [ ]}
    name               = 'Neurolabscope1'
    extensions          = [ ]
    mode = 'file'
    def __init__(self, filename = None) :
        BaseIO.__init__(self, filename)
    
    
    def read_segment(self,cascade = True, lazy = False,):

        name = os.path.basename(self.filename)

        r = re.findall('(\d+)\-(\d+)\-(\d+) (\d+)h(\d+)m(\d+) ([\S ]+)',name[:-4])
        if len(r) <1 :
            raise('erreur nomenclature')
            return
        YY , MM , DD , hh, mm , ss, fields  =r[0]
        rec_edatetime = datetime.datetime(int(YY),int(MM),int(DD),int(hh),int(mm),int(ss))
        
        annotations = {}
        for f in fields.split('_') :
            if len(f.split('=')) == 2 :
                field, value = f.split('=')
                annotations[field] = value
        
        sr = float(annotations.pop('fs'))
        dt = np.dtype(annotations.pop('dtype'))
        nbchannel = int(annotations.pop('numChannel'))
        reader = neo.RawBinarySignalIO(filename =self.filename)
        seg = reader.read_segment(sampling_rate =sr*pq.Hz,
                                                t_start = 0.*pq.s,
                                                unit = pq.V,
                                                nbchannel = nbchannel,
                                                dtype = dt,
                                                )
        
        seg.rec_edatetime = rec_edatetime
        seg.annotate(**annotations)
        
        return seg



