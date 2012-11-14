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
        self.set_start_stop_auto()
        
        self.add_analogsignals( analogsignals = self.seg.analogsignals )
        self.add_timefreqs( analogsignals = self.seg.analogsignals)
        
        self.change_xsize(xsize)
        
    def change_xsize(self, xsize = None):
        if xsize is None:
            xsize = self.xsize_changer.value()
        else:
            self.xsize_changer.setValue(xsize)
        for subviewer in self.subviewers:
            subviewer.viewer.xsize = xsize
    
    def set_start_stop_auto(self):
        t_start = np.inf*pq.s
        t_stop = -np.inf*pq.s
        for anasig in self.seg.analogsignals:
            t_start = min(anasig.t_start, t_start)
            t_stop = max(anasig.t_stop, t_stop)
        
        eps = (t_stop-t_start).magnitude/20.
        self.timeseeker.set_start_stop(t_start= t_start.magnitude-eps, t_stop = t_stop.magnitude+eps)
        self.timeseeker.seek(t_start.magnitude)
        