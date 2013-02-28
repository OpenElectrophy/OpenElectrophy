# -*- coding: utf-8 -*-
"""
Widget for viewing segment and/or block.
"""

from tools import *

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
            #~ self.add_timefreqs( analogsignals = self.seg.analogsignals)
        if len(self.seg.spiketrains) > 0:
            self.add_spiketrains(spiketrains = self.seg.spiketrains)
        if len(self.seg.epocharrays) > 0:
            self.add_epochs(epocharrays = self.seg.epocharrays)
        
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
    


