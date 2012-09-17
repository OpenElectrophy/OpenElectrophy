import sys
sys.path = [ '../../..' ] + sys.path

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import numpy as np
import quantities as pq
import neo
from OpenElectrophy.gui.viewers import *
from OpenElectrophy.gui.viewers.signalviewer import *

from OpenElectrophy.spikesorting import SpikeSorter, generate_block_for_sorting

#~ sig_size = 3.6e8
sig_size = 1e5
nb_spike =  10e3
fs = 10.e3
t = np.arange(sig_size)/fs



def test1():
    analogsignals = [ ]
    spiketrains_on_signals = [ ]
    for i in range(4):
        sig = 5*np.sin(t*np.pi*2*25) + np.random.randn(sig_size)+i*10.
        spikepos = np.random.randint(sig.size, size =nb_spike)
        sig[spikepos] += 15
        analogsignals.append(neo.AnalogSignal(sig, units = 'uV', t_start= -5.*pq.s, sampling_rate = 10*pq.kHz))
        spiketrains_on_signals.append([ ])
        for i in range(2):
            spiketrains_on_signals[-1].append(neo.SpikeTrain(spikepos[i*nb_spike/2:(i+1)*nb_spike/2]/fs-5., t_start = -5., t_stop = -5.+sig_size/fs, units = 's'))
    
    
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
