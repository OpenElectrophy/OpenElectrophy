import sys
sys.path.append('../../..')

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from OpenElectrophy.gui.spikesorting.toolchain import *

from OpenElectrophy.gui.guiutil.picklesettings import PickleSettings



from create_spike_sorter import *

def test1():
    app = QApplication([ ])
    
    w1 = MultiMethodsParamWidget(methods = features)
    w1.show()
    app.exec_()
    print  w1.get_dict()
    
def test2():
    app = QApplication([ ])

    settings = PickleSettings(applicationname = 'testOE3')
    
    w1 = ToolChainWidget(spikesorter = spikesorter, settings = settings)
    #~ w1.change_toolchain(FromFullBandSignalToClustered, )
    w1.change_toolchain(FromFullBandSignalToDetection)
    
    
    w1.show()
    app.exec_()
    
    
    

if __name__ == '__main__' :
    #~ test1()
    test2()
