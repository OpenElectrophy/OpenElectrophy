import sys
sys.path = [ '../../..' ] + sys.path

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import numpy as np
import quantities as pq
import neo

from OpenElectrophy.gui.viewers.segmentviewer import *

from create_segment import *

def test1():
    app = QApplication([ ])
    w1 = SegmentViewer(segment = seg, xsize = 15)
    w1.show()
    app.exec_()


def test2():
    #~ seg = neo.Spike2IO(filename = 'Rat9_11_08_21_10-00-00.SMR').read_segment()
    seg = neo.Spike2IO(filename = 'R28-C4-B.SMR').read_segment()
    #~ seg = neo.MicromedIO(filename = 'EEG_1503.TRC').read_segment()
    
    app = QApplication([ ])
    w1 = SegmentViewer(segment = seg, xsize = 15)
    w1.show()
    app.exec_()


if __name__ == '__main__' :
    #~ test1()
    test2()
