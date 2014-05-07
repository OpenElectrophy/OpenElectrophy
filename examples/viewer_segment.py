# -*- coding: utf-8 -*-
"""
Neo segment viewer
-----------------------------------------------

Simple code to open neo.Segment viewer and all related object.

"""

import sys
sys.path.append('..')

if __name__== '__main__':

    
    from OpenElectrophy.gui.viewers import SegmentViewer
    from OpenElectrophy import TryItIO
    from PyQt4.QtGui import QApplication
    app = QApplication([ ])
    
    bl = TryItIO().read(nb_segment=1, duration = 100)[0]
    w = SegmentViewer(segment = bl.segments[0])
    w.show()
    
    app.exec_()
    
