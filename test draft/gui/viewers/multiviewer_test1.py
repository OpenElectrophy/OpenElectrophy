import sys
sys.path = [ '../../..' ] + sys.path

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import numpy as np
import quantities as pq
import neo

from OpenElectrophy.gui.viewers.multiviewer import *

from create_segment import *

def test1():
    app = QApplication([ ])
    w1 = MultiViewer()
    w1.add_analogsignals(analogsignals = analogsignals)
    w1.show()
    app.exec_()


if __name__ == '__main__' :
    test1()
