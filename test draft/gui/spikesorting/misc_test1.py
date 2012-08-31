import sys
sys.path = [ '../../..' ] + sys.path

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from OpenElectrophy.gui.spikesorting import Summary




from create_spike_sorter import *


def test1():
    app = QApplication([ ])
    w1 = Summary(spikesorter = spikesorter)
    w1.refresh()
    w1.show()
    app.exec_()

if __name__ == '__main__' :
    test1()
