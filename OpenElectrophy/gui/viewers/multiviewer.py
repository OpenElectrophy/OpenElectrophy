# -*- coding: utf-8 -*-
"""
Widget for viewing segment and/or block.
"""

from .tools import *

from .signalviewer import *
from .timefreqviewer import *
from .epochviewer import *
from .eventviewer import *
from .eventlist import *
from .spiketrainviewer import *
try:
    from .videoviewer import *
except ImportError:
    pass
    

class SubViewer(object):
    def __init__(self, 
                            viewer = None,
                            name  = None,
                            t_start_correction = 0.,
                            sampling_rate_factor =1,
                            ):
        self.viewer = viewer
        self.name = name
        self.t_start_correction = t_start_correction
        self.sampling_rate_factor = sampling_rate_factor

        self.dock = QDockWidget(name)
        self.dock.setObjectName(name)
        self.dock.setWidget(self.viewer)
        
        if self.t_start_correction ==0. and self.sampling_rate_factor == 1.:
            self.corrected = False
        else:
            self.corrected = True
        
        

class MultiViewer(QMainWindow):
    """
    this is a QMainWindow with docks for viewing:
       * AnalogSignals
       * EpochArray
       * EventArrays
       * timefrequency for AnalogSignals
       * video stream
    
    This add the possibility of time correction bewteen dock.
    For instance, it is possible re synchronize 2 series of AnalogSignal coming from 2 
    acquisition systems knowing the time drift and the offset.
    
    Note that this is often the case when video + signal.
    
    
    """
    def __init__(self, parent  = None):
        super(MultiViewer, self).__init__(parent = parent)
        
        self.setDockNestingEnabled(True) 
        
        self.timeseeker = TimeSeeker()
        dock = QDockWidget('Time',self)
        dock.setObjectName( 'Time')
        dock.setWidget(self.timeseeker)
        self.addDockWidget(Qt.TopDockWidgetArea, dock)

        self.timeseeker.time_changed.connect(self.seek_all)
        self.timeseeker.fast_time_changed.connect(self.fast_seek_all)
        
        self.subviewers = [ ]
        
        


    def add_analogsignals(self, analogsignals = [ ], name = 'AnalogSignals',
                                t_start_correction = 0., sampling_rate_factor = 1., **kargs):
        
        subviewer = SubViewer(viewer = SignalViewer(analogsignals = analogsignals, **kargs),
                                                    name = name,
                                                    t_start_correction = t_start_correction,
                                                    sampling_rate_factor = sampling_rate_factor,
                                                    )
        self.addDockWidget(Qt.BottomDockWidgetArea, subviewer.dock, Qt.Vertical)
        self.subviewers.append(subviewer)

    def add_timefreqs(self, analogsignals = [ ], name = 'Time Frequency Maps',
                                t_start_correction = 0., sampling_rate_factor = 1., **kargs):
        
        subviewer = SubViewer(viewer = TimeFreqViewer(analogsignals = analogsignals, **kargs),
                                                    name = name,
                                                    t_start_correction = t_start_correction,
                                                    sampling_rate_factor = sampling_rate_factor,
                                                    )
        self.addDockWidget(Qt.BottomDockWidgetArea, subviewer.dock, Qt.Vertical)
        self.subviewers.append(subviewer)
    
    def add_epochs(self, epocharrays = [ ], name = 'Epoch Arrays',
                                t_start_correction = 0., sampling_rate_factor = 1., **kargs):
        subviewer = SubViewer(viewer = EpochViewer(epocharrays = epocharrays, **kargs),
                                                    name = name,
                                                    t_start_correction = t_start_correction,
                                                    sampling_rate_factor = sampling_rate_factor,
                                                    )
        self.addDockWidget(Qt.BottomDockWidgetArea, subviewer.dock, Qt.Vertical)
        self.subviewers.append(subviewer)

    def add_events(self, eventarrays = [ ], name = 'Event Arrays',
                                t_start_correction = 0., sampling_rate_factor = 1., **kargs):
        subviewer = SubViewer(viewer = EventViewer(eventarrays = eventarrays, **kargs),
                                                    name = name,
                                                    t_start_correction = t_start_correction,
                                                    sampling_rate_factor = sampling_rate_factor,
                                                    )
        self.addDockWidget(Qt.BottomDockWidgetArea, subviewer.dock, Qt.Vertical)
        self.subviewers.append(subviewer)
        
    def add_eventlist(self, eventarrays = [ ], name = 'Event or Epoch list',
                                t_start_correction = 0., sampling_rate_factor = 1., **kargs):
        subviewer = SubViewer(viewer = EventList(eventarrays = eventarrays, **kargs),
                                                    name = name,
                                                    t_start_correction = t_start_correction,
                                                    sampling_rate_factor = sampling_rate_factor,
                                                    )
        self.addDockWidget(Qt.BottomDockWidgetArea, subviewer.dock, Qt.Horizontal)
        self.subviewers.append(subviewer)
        subviewer.viewer.time_changed.connect(self.timeseeker.seek)
        

    
    def add_spiketrains(self, spiketrains = [ ], name = 'SpikeTrains',
                                t_start_correction = 0., sampling_rate_factor = 1., **kargs):
        subviewer = SubViewer(viewer = SpikeTrainViewer(spiketrains = spiketrains, **kargs),
                                                    name = name,
                                                    t_start_correction = t_start_correction,
                                                    sampling_rate_factor = sampling_rate_factor,
                                                    )
        self.addDockWidget(Qt.BottomDockWidgetArea, subviewer.dock, Qt.Vertical)
        self.subviewers.append(subviewer)    
    
    def add_videos(self, videofiles = [],   name = 'Videos',
                                t_start_correction = 0., sampling_rate_factor = 1., **kargs):
        subviewer = SubViewer(viewer = VideoViewer(videofiles = videofiles, **kargs),
                                                    name = name,
                                                    t_start_correction = t_start_correction,
                                                    sampling_rate_factor = sampling_rate_factor,
                                                    )
        self.addDockWidget(Qt.BottomDockWidgetArea, subviewer.dock, Qt.Vertical)
        self.subviewers.append(subviewer)    
    
    

    
    def seek_all(self, t, fast = False):
        for v in self.subviewers:
            if not v.dock.isVisible():
                continue
            if fast:
                f = v.viewer.fast_seek
            else:
                f = v.viewer.seek
            if v.corrected:
                f(t*v.sampling_rate_factor+v.t_start_correction)
            else:
                f(t)
        
    
    def fast_seek_all(self, t):
        self.seek_all(t, fast = True)

