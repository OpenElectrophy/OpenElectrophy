import sys
sys.path = [ '../../..' ] + sys.path

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import numpy as np
import quantities as pq
import neo


from OpenElectrophy.gui.viewers.timefreqviewer import *

from create_segment import *

def test1():
    
    
    app = QApplication([ ])
    
    s = TimeSeeker(refresh_interval = 0.1)
    s.show()
    #~ print analogsignals[0].t_start, analogsignals[0].t_stop
    s.set_start_stop(t_start= analogsignals[0].t_start.magnitude-2, t_stop = analogsignals[0].t_stop.magnitude+2)
    
    w = TimeFreqViewer(analogsignals = analogsignals, xsize = 12.)
    visibles = np.zeros(len(analogsignals))
    visibles[0] =True
    visibles[-1] =True
    #~ time.sleep(2.)
    w.set_params(visibles = visibles)
    w.show()
    s.time_changed.connect(w.seek)
    s.fast_time_changed.connect(w.fast_seek)

    
    #~ s.seek(0.)
    
    app.exec_()



def test2():
    app = QApplication([ ])
    
    w = TimeFreqViewer(analogsignals = analogsignals, with_time_seeker = True, max_visible_on_open = 1)
    w.show()
    w.xsize = 60.
    app.exec_()



if __name__ == '__main__' :
    test1()
    #~ test2()

