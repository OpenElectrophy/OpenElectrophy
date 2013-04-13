import sys
sys.path = [ '../../..' ] + sys.path

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import numpy as np
import quantities as pq
import neo


from OpenElectrophy.gui.viewers.videoviewer import *
#~ from create_segment import *


def test1():
    
    
    app = QApplication([ ])
    
    s = TimeSeeker(refresh_interval = .1)
    s.show()
    s.set_start_stop(0, 3600)
    
    p = '/media/OS/Documents and Settings/Dell Xps Sam/Videos/' 
    videofiles = [ 
                        p+'Homeland.S01E01.PROPER.VOSTFR.HDTV.XviD-ATeam.avi',
                        p+'Homeland.S01E02.PROPER.VOSTFR.HDTV.XviD-ATeam.avi',
                        p+'Homeland.S01E01.PROPER.VOSTFR.HDTV.XviD-ATeam.avi',
                        p+'Homeland.S01E02.PROPER.VOSTFR.HDTV.XviD-ATeam.avi',
                        p+'Homeland.S01E01.PROPER.VOSTFR.HDTV.XviD-ATeam.avi',
                        p+'Homeland.S01E02.PROPER.VOSTFR.HDTV.XviD-ATeam.avi',
                        p+'Homeland.S01E01.PROPER.VOSTFR.HDTV.XviD-ATeam.avi',
                        p+'Homeland.S01E02.PROPER.VOSTFR.HDTV.XviD-ATeam.avi',
                        p+'Homeland.S01E01.PROPER.VOSTFR.HDTV.XviD-ATeam.avi',
                        p+'Homeland.S01E02.PROPER.VOSTFR.HDTV.XviD-ATeam.avi',
                        
                        #~ p+'The.Following.S01E01.FASTSUB.VOSTFR.720p.HDTV.x264-ADDiCTiON.mkv',
                        #~ p+'Take Shelter - Jeff Nichols (2011).avi',
                        
                        ]
    
    w1 = VideoViewer(videofiles = videofiles)
    w1.show()
    
    s.time_changed.connect(w1.seek)
    s.fast_time_changed.connect(w1.fast_seek)
    
    s.seek(0.)
    
    sys.exit(app.exec_())





if __name__ == '__main__' :
    test1()
