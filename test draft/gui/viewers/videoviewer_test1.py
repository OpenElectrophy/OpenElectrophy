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
    
    #~ p = './' 
    p = '/home/samuel/mnt/CRNLDATA/crnldata/cmo/Etudiants/NBuonviso201601_plethysmo_Baptiste/Data/Video/24-03-2016/'
    videofiles = [ 
                        p + '2016-03-24_09h07m22,608395s_animal=R1_phase=E_numphase=3_V=1.avi',
                        p + '2016-03-24_09h07m22,608395s_animal=R1_phase=E_numphase=3_V=2.avi',
                        ]
    
    w1 = VideoViewer(videofiles = videofiles)
    w1.show()
    
    s.time_changed.connect(w1.seek)
    s.fast_time_changed.connect(w1.fast_seek)
    
    s.seek(0.)
    
    sys.exit(app.exec_())

def test2():
    
    
    app = QApplication([ ])
    
    s = TimeSeeker(refresh_interval = .1)
    s.show()
    s.set_start_stop(0, 3600)
    
    #~ p = './' 
    p = '/home/samuel/mnt/CRNLDATA/crnldata/cmo/Etudiants/NBuonviso201601_plethysmo_Baptiste/Data/Video/24-03-2016/'
    videofiles = [ 
                        p + '2016-03-24_09h07m22,608395s_animal=R1_phase=E_numphase=3_V=1.avi',
                        p + '2016-03-24_09h07m22,608395s_animal=R1_phase=E_numphase=3_V=2.avi',
                        ]
    videotimes = [ ]
    for i in range(2):
        filename = p + '2016-03-24_09h07m22,608395s_animal=R1_phase=E_numphase=3_V={}.tps'.format(i+1)
        t = np.fromfile(filename, dtype = np.int32).astype(np.float64)/1000.
        videotimes.append(t)
        print t[0]
        print t.shape
        print t
        
        from matplotlib import pyplot
        fig, ax = pyplot.subplots()
        
        
        
    
    
    w1 = VideoViewer(videofiles = videofiles, videotimes = videotimes)
    w1.show()
    
    s.time_changed.connect(w1.seek)
    s.fast_time_changed.connect(w1.fast_seek)
    
    s.seek(0.)
    
    sys.exit(app.exec_())




if __name__ == '__main__' :
    #~ test1()
    test2()
