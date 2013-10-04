import sys
sys.path = [ '../../..' ] + sys.path

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from OpenElectrophy.gui.spikesorting import SpikeList, UnitList




from create_spike_sorter import *


def test1():
    app = QApplication([ ])
    w1 = SpikeList(spikesorter = spikesorter)
    w1.refresh()
    w1.show()

    w2 = UnitList(spikesorter = spikesorter)
    w2.refresh()
    w2.show()
    w2.spike_selection_changed.connect(w1.on_spike_selection_changed)


    app.exec_()

if __name__ == '__main__' :
    test1()
