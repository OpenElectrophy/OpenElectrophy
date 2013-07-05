import sys
sys.path = [ '../../..' ] + sys.path

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from OpenElectrophy.gui.viewers import *
from OpenElectrophy.gui.viewers.tools import ViewerBase, TimeSeeker






#~ def test1():
    #~ app = QApplication([ ])
    #~ w1 = XSizeChanger()
    #~ w1.show()
    #~ w2 = YLimsChanger()
    #~ w2.show()
    #~ app.exec_()
    

def test2():
    app = QApplication([ ])
    
    s =TimeSeeker(show_label = True)
    s.show()
    
    w1 =ViewerBase()
    w1.show()

    s.time_changed.connect(w1.seek)
    #~ s.time_changed.connect(w1.fast_seek)
    s.fast_time_changed.connect(w1.fast_seek)
    
    app.exec_()


def test3():
    app = QApplication([ ])
    
    s =TimeSeeker(show_label = True)
    s.show()
    
    w1 =ViewerWithXSizeAndYlim()
    w1.show()

    s.time_changed.connect(w1.seek)
    #~ s.time_changed.connect(w1.fast_seek)
    s.fast_time_changed.connect(w1.fast_seek)
    
    app.exec_()





if __name__ == '__main__' :
    #~ test1()
    test2()
    #~ test3()
