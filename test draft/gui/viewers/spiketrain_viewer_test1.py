import sys
sys.path = [ '../../..' ] + sys.path

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import numpy as np
import quantities as pq
import neo


from OpenElectrophy.gui.viewers.spiketrainviewer import *

from create_segment import *

def test1():
    
    
    app = QApplication([ ])
    
    s = TimeSeeker()
    s.show()
    s.set_start_stop(analogsignals[0].t_start.magnitude-2,analogsignals[0].t_stop.magnitude+2)
    
    
    w1 = SpikeTrainViewer(spiketrains = seg.spiketrains)
    w1.show()
    
    s.time_changed.connect(w1.seek)
    s.fast_time_changed.connect(w1.fast_seek)
    
    s.seek(0.)
    
    sys.exit(app.exec_())





if __name__ == '__main__' :
    test1()
