import sys
sys.path = [ '../../..' ] + sys.path

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from OpenElectrophy.gui.spikesorting import FeaturesParallelPlot, FeaturesWilsonPlot, Features3D, FeaturesEvolutionInTime, FeaturesNDViewer




from create_spike_sorter import *


def test1():
    app = QApplication([ ])
    #~ w1 = FeaturesParallelPlot(spikesorter = spikesorter)
    #~ w1.refresh()
    #~ w1.show()

    #~ w2 = FeaturesWilsonPlot(spikesorter = spikesorter)
    #~ w2.refresh()
    #~ w2.show()

    #~ w3 = Features3D(spikesorter = spikesorter)
    #~ w3.refresh()
    #~ w3.show()
    
    #~ w4 = FeaturesEvolutionInTime(spikesorter = spikesorter)
    #~ w4.refresh()
    #~ w4.show()
    
    w5 = FeaturesNDViewer(spikesorter = spikesorter)
    w5.refresh()
    w5.show()
    
    

    app.exec_()

if __name__ == '__main__' :
    test1()
