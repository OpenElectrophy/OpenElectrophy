import sys
sys.path = [ '../../..' ] + sys.path

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from OpenElectrophy.gui.viewers import *
from OpenElectrophy.gui.viewers.tools import ViewerBase




def test1():
    app = QApplication([ ])
    
    s =TimeSeeker()
    s.show()
    
    w1 =ViewerBase()
    w1.show()

    s.time_changed.connect(w1.seek)
    s.fast_time_changed.connect(w1.fast_seek)
    
    app.exec_()

if __name__ == '__main__' :
    test1()
