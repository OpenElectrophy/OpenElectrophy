import sys
sys.path.append('../..')

from PyQt4.QtCore import *
from PyQt4.QtGui import *


from OpenElectrophy import *
from OpenElectrophy.gui.opendb import OpenDB, CreateDB
from OpenElectrophy.gui.guiutil import *
from OpenElectrophy.gui.guiutil.picklesettings import PickleSettings


import quantities as pq
import numpy as np




def test1():
    """open existing db"""

    app = QApplication([ ])
    
    settings = PickleSettings(applicationname = 'testOE3')
    
    w = OpenDB(settings = settings)
    w.exec_()
    
    print w.get_opendb_kargs()


def test2():
    """create new db"""

    app = QApplication([ ])
    
    settings = PickleSettings(applicationname = 'testOE3')
    
    w = CreateDB(settings = settings)
    w.exec_()
    w.create_a_new_db()
    


if __name__ == '__main__' :
    test1()
    #~ test2()



