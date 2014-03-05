import sys
sys.path.append('../../..')

from PyQt4.QtCore import *
from PyQt4.QtGui import *


from OpenElectrophy.gui.oscillationdetection import OscillationDetection
from OpenElectrophy import *
from OpenElectrophy.gui.guiutil.picklesettings import PickleSettings

bl = TryItIO().read_block(nb_segment=1, duration = 10)
neoana = bl.segments[0].analogsignals[0]



url = 'sqlite:///test_oscillationdetection.sqlite'
dbinfo = open_db(url = url, use_global_session = True, myglobals = globals(),)
session = dbinfo.Session()

ana = OEBase.from_neo(neoana, mapped_classes = dbinfo.mapped_classes)

def test1():

    
    app = QApplication([ ])
    settings = PickleSettings(applicationname = 'testOE3')
    w = OscillationDetection(analogsignal = ana, settings =settings, session = session, mapped_classes = dbinfo.mapped_classes)
    w.show()
    app.exec_()

if __name__ == '__main__' :
    test1()
