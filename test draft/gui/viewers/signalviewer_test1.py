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
    s.set_start_stop(analogsignals[0].t_start.magnitude-2,analogsignals[0].t_stop.magnitude+2)
    
    #~ w1 = SignalViewer(analogsignals = analogsignals, spiketrains_on_signals = spiketrains_on_signals)
    w1 = SignalViewer(analogsignals = analogsignals, spiketrains_on_signals = None, xsize = 2)
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
    
    #~ app.exec_()
    sys.exit(app.exec_())


def test2():
    paramGlobal = pg.parametertree.Parameter.create( name='Global options', type='group',
                                                    children = [ {'name': 'xsize', 'type': 'logfloat', 'value': 10., 'step': 0.1},
                                                                        {'name': 'ylims', 'type': 'range', 'value': [-10., 10.] },
                                                                        {'name': 'background_color', 'type': 'color', 'value': 'k' },
                                                                    ])    
    
    app = QApplication([ ])
    w = SignalViewerParameters(analogsignals = analogsignals, paramGlobal = paramGlobal)
    w.show()
    sys.exit(app.exec_())

def test3():
    app = QApplication([ ])
    
    w1 = SignalViewer(analogsignals = analogsignals, spiketrains_on_signals = None, xsize = 2, with_time_seeker = True)
    w1.show()
    sys.exit(app.exec_())

if __name__ == '__main__' :
    #~ test1()
    #~ test2()
    test3()
