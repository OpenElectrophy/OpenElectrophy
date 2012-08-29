import sys
sys.path.append('../../..')

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from OpenElectrophy.gui.spikesorting import FeaturesParallelPlot, FeaturesWilsonPlot




from create_spike_sorter import *


def test1():
    app = QApplication([ ])
    w1 = FeaturesParallelPlot(spikesorter = spikesorter)
    w1.refresh()
    w1.show()

    w2 = FeaturesWilsonPlot(spikesorter = spikesorter)
    w2.refresh()
    w2.show()



    app.exec_()

if __name__ == '__main__' :
    test1()
