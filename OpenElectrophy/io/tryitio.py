# -*- coding: utf-8 -*-
"""

"""
import neo
from neo import (Block, Segment , AnalogSignal, SpikeTrain,
                            EventArray, EpochArray, RecordingChannel, RecordingChannelGroup)
from neo.io.baseio import BaseIO

import numpy as np
import quantities as pq

from .. import spikesorting

class TryItIO(BaseIO):
    is_readable = True
    is_writable = False

    supported_objects  = [ Block, Segment , AnalogSignal, SpikeTrain,
                            EventArray, EpochArray, RecordingChannel, RecordingChannelGroup ]
    readable_objects    = [ Block ]
    writeable_objects   = [ ]
    read_params = {
        Block : [ ('duration', {'value' : 60., 'label' : 'Duration size (s.)'}), 
                    ('nb_segment', {'value' :5, 'label' : 'nb_segment'}),
                    ],
        }
    name               = 'Try OpenElectrophy'
    extensions          = [ ]
    mode = 'fake'
    def __init__(self ) :
        BaseIO.__init__(self)

    def read_block(self,cascade = True, lazy = False,
                                    duration = 60.,
                                    nb_segment = 5,
                                    ):
        
        bl = spikesorting.generate_block_for_sorting(duration = duration*pq.s,
                                                                                nb_segment = 5,)
        
        # add some oscillation
        for seg in bl.segments:
            for ana in seg.analogsignals:
                t = ana.times.magnitude
                f1 = np.linspace(np.random.rand()*60+20. , np.random.rand()*60+20., ana.size)
                f2 = np.linspace(np.random.rand()*1.+.1 , np.random.rand()*1.+.1, ana.size)
                sig = np.sin(2*np.pi*t*f1) * np.sin(np.pi*t*f2+np.random.rand()*np.pi)**2
                sig[t<0] = 0.
                ana += sig * ana.units
                
                
                
        
        return bl

