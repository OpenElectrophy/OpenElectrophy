import sys
sys.path = [ '../../..' ] + sys.path

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import numpy as np
import quantities as pq
import neo


from OpenElectrophy.gui.viewers.signalviewer import *

from create_segment import *

def test1():
    
    
    app = QApplication([ ])
    
    s = TimeSeeker()
    s.show()
    s.change_start_stop(t_start= -25., t_stop = analogsignals[0].t_stop.magnitude)
    
    w1 = SignalViewerQwt(analogsignals = analogsignals, spiketrains_on_signals = spiketrains_on_signals)
    #~ w1 = SignalViewerQwt(analogsignals = analogsignals, spiketrains_on_signals = None)
    w1.show()

    #~ w2 = SignalViewerMpl(analogsignals = analogsignals)
    #~ w2.show()
    
    
    
    s.time_changed.connect(w1.seek)
    s.fast_time_changed.connect(w1.fast_seek)
    #~ s.fast_time_changed.connect(w1.seek)

    #~ s.time_changed.connect(w2.seek)
    #~ s.fast_time_changed.connect(w2.fast_seek)
    #~ s.fast_time_changed.connect(w2.seek)
    
    
    s.seek(0.)
    
    app.exec_()




if __name__ == '__main__' :
    test1()
