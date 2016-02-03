# -*- coding: utf-8 -*-
"""
Widget for viewing segment and/or block.
"""

from .tools import *

from .multiviewer import MultiViewer



class SegmentViewer(MultiViewer):
    """
    SegmentViewer is a simplified multiviewer initilaized by
    a neo.segment.
    """
    def __init__(self, parent  = None, segment = None, xsize = 10.):
        super(SegmentViewer, self).__init__(parent = parent)
        
        self.xsize_changer = SpinAndSliderWidget()
        
        self.timeseeker.toolbar.addWidget(QLabel('xsize:'))
        self.timeseeker.toolbar.addWidget(self.xsize_changer)
        self.xsize_changer.sigChanged.connect(self.change_xsize)
        
        self.seg = segment
        self.timeseeker.set_start_stop(*find_best_start_stop(segment =segment))
        self.timeseeker.seek(self.timeseeker.t_start)
        
        if len(self.seg.analogsignals) > 0:
            self.add_analogsignals( analogsignals = self.seg.analogsignals )
            
            all_sr = np.array([ s.sampling_rate for s in self.seg.analogsignals ], dtype = object)
            for i,sr in enumerate(np.unique(all_sr)):
                # timefreq viewer accept sig with same sr
                ind,  = np.where(all_sr==sr)
                anasigs = [ self.seg.analogsignals[sel] for sel in ind]
                self.add_timefreqs( analogsignals = anasigs, name = 'Time Frequency Maps {}'.format(i),max_visible_on_open = 4)
                viewer = self.subviewers[-1]
                viewer.dock.setVisible(False)
                
                    
                
        
        if len(self.seg.spiketrains) > 0:
            self.add_spiketrains(spiketrains = self.seg.spiketrains)
        if len(self.seg.epocharrays) > 0:
            self.add_epochs(epocharrays = self.seg.epocharrays)
        if len(self.seg.eventarrays) > 0:
            self.add_events(eventarrays = self.seg.eventarrays)
        ev_ep = self.seg.epocharrays+self.seg.eventarrays
        if len(ev_ep)>0:
            self.add_eventlist(eventarrays = ev_ep)
        
        self.change_xsize(xsize)
        
    def change_xsize(self, xsize = None):
        if xsize is None:
            xsize = self.xsize_changer.value()
        else:
            self.xsize_changer.setValue(xsize)
        for subviewer in self.subviewers:
            #~ print subviewer.name
            if subviewer.dock.isVisible():
                subviewer.viewer.xsize = xsize
    


