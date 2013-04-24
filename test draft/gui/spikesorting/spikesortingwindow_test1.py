import sys
sys.path.append('../../..')

from PyQt4.QtCore import *
from PyQt4.QtGui import *


from OpenElectrophy.gui.spikesorting import SpikeSortingWindow

from create_spike_sorter import *




def test1():
    app = QApplication([ ])
    settings = PickleSettings(applicationname = 'testOE3')
    w = SpikeSortingWindow(spikesorter = spikesorter, settings =settings)
    w.show()
    app.exec_()

    

if __name__ == '__main__' :
    test1()
