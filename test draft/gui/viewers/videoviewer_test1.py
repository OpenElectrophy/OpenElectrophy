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
    p = '/home/sgarcia/Documents/projet/script_cmo/AMMouly201012_timing_ratons_julie/A1M8P8/'
    videofiles = [ 
                        p+'2012-11-15_session=cond_age=22_group=P_sex=2_animal=A1M8P8_run=allV0_total.avi',
                        p+'2012-11-15_session=cond_age=22_group=P_sex=2_animal=A1M8P8_run=allV1_total.avi',
                        p+'2012-11-15_session=cond_age=22_group=P_sex=2_animal=A1M8P8_run=allV2_total.avi',
                        #~ p+'Bernie_ARZU_.avi',
                        #~ p+'2010-12-17_session=ret1_age=23_group=P_sex=1_animal=M1P1_run=allV0.avi',
                        #~ p+'2010-12-17_session=ret1_age=23_group=P_sex=1_animal=M1P1_run=allV1.avi',
                        #~ p+'2010-12-17_session=ret1_age=23_group=P_sex=1_animal=M1P1_run=allV0.avi',
                        #~ p+'2010-12-17_session=ret1_age=23_group=P_sex=1_animal=M1P1_run=allV0.avi',
                        #~ p+'2010-12-17_session=ret1_age=23_group=P_sex=1_animal=M1P1_run=allV1.avi',
                        #~ p+'2010-12-17_session=ret1_age=23_group=P_sex=1_animal=M1P1_run=allV0.avi',
                        #~ p+'2010-12-17_session=ret1_age=23_group=P_sex=1_animal=M1P1_run=allV0.avi',
                        #~ p+'2010-12-17_session=ret1_age=23_group=P_sex=1_animal=M1P1_run=allV1.avi',
                        #~ p+'2010-12-17_session=ret1_age=23_group=P_sex=1_animal=M1P1_run=allV0.avi',
                        #~ p+'2010-12-17_session=ret1_age=23_group=P_sex=1_animal=M1P1_run=allV0.avi',
                        #~ p+'2010-12-17_session=ret1_age=23_group=P_sex=1_animal=M1P1_run=allV1.avi',
                        #~ p+'2010-12-17_session=ret1_age=23_group=P_sex=1_animal=M1P1_run=allV0.avi',
                        #~ p+'2010-12-17_session=ret1_age=23_group=P_sex=1_animal=M1P1_run=allV0.avi',
                        #~ p+'2010-12-17_session=ret1_age=23_group=P_sex=1_animal=M1P1_run=allV1.avi',
                        #~ p+'2010-12-17_session=ret1_age=23_group=P_sex=1_animal=M1P1_run=allV2.avi',
                        #~ p+'2013-01-26_09h04m37,676424s_animal=R11_phase=H_numphase=3_numodeur=0_V=0.avi',
                        #~ p+'2013-01-26_09h04m37,676424s_animal=R11_phase=H_numphase=3_numodeur=0_V=1.avi',
                        
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
    p = '/home/sgarcia/Documents/projet/script_cmo/AMMouly201012_timing_ratons_julie/A1M8P8/'
    videofiles = [ 
                        p+'2012-11-15_session=cond_age=22_group=P_sex=2_animal=A1M8P8_run=allV0_total.avi',
                        p+'2012-11-15_session=cond_age=22_group=P_sex=2_animal=A1M8P8_run=allV1_total.avi',
                        p+'2012-11-15_session=cond_age=22_group=P_sex=2_animal=A1M8P8_run=allV2_total.avi',
                        ]
    videotimes = [ ]
    for i in range(3):
        filename = p + '2012-11-15_session=cond_age=22_group=P_sex=2_animal=A1M8P8_run=allV{}.tps'.format(i)
        t = np.fromfile(filename, dtype = np.int32).astype(np.float64)/1000.
        videotimes.append(t)
        print t[0]
        print t.shape
    
    
    w1 = VideoViewer(videofiles = videofiles, videotimes = videotimes)
    w1.show()
    
    s.time_changed.connect(w1.seek)
    s.fast_time_changed.connect(w1.fast_seek)
    
    s.seek(0.)
    
    sys.exit(app.exec_())




if __name__ == '__main__' :
    #~ test1()
    test2()
