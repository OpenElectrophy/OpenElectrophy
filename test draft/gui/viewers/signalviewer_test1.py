import sys
sys.path = [ '../../..' ] + sys.path

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import numpy as np
import quantities as pq
import neo
from OpenElectrophy.gui.viewers import *

from OpenElectrophy.spikesorting import SpikeSorter, generate_block_for_sorting

sig_size = 1e6

fs = 10e3
t = np.arange(1e6)/fs


def test1():
    analogsignals = [ ]
    for i in range(1):
        sig = 5*np.sin(t*np.pi*2*25) + np.random.randn(sig_size)+i*10.
        sig[np.random.randint(sig.size, size = 10e3)] += 15
        analogsignals.append(neo.AnalogSignal(sig, units = 'uV', t_start= -5.*pq.s, sampling_rate = 10*pq.kHz))
    
    
    app = QApplication([ ])
    
    s = TimeSeeker()
    s.show()
    
    
    w1 = SignalViewer(analogsignals = analogsignals)
    w1.show()
    
    s.time_changed.connect(w1.seek)
    s.fast_time_changed.connect(w1.fast_seek)
    
    app.exec_()

if __name__ == '__main__' :
    test1()
