import sys
sys.path.append('../..')

from PyQt4.QtCore import *
from PyQt4.QtGui import *


from OpenElectrophy import *
from OpenElectrophy.gui.opendb import OpenDB
from OpenElectrophy.gui.guiutil import *
from OpenElectrophy.gui.guiutil.picklesettings import PickleSettings


import quantities as pq
import numpy as np




def test1():


    app = QApplication([ ])
    
    settings = PickleSettings(applicationname = 'testOE3')
    
    w = OpenDB(settings = settings)
    w.exec_()
    
    print w.get_kargs()



if __name__ == '__main__' :
    test1()



