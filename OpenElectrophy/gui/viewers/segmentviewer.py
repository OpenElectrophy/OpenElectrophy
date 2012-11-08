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
    def __init__(self, parent  = None, segment = None):
        super(SegmentViewer, self).__init__(parent = parent)
        
        self.seg = segment
        
        self.add_analogsignals( analogsignals = self.seg.analogsignals , name = 'Signals')
