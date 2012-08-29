import sys
sys.path.append('../../..')

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from OpenElectrophy.gui.spikesorting import AverageWaveforms, AllWaveforms




from create_spike_sorter import *


def test1():
    app = QApplication([ ])
    w1 = AverageWaveforms(spikesorter = spikesorter)
    w1.refresh()
    w1.show()
    w2 = AllWaveforms(spikesorter = spikesorter)
    w2.refresh()
    w2.show()

    app.exec_()

if __name__ == '__main__' :
    test1()
