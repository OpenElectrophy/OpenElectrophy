import sys
sys.path.append('../..')

from PyQt4.QtCore import *
from PyQt4.QtGui import *


from OpenElectrophy.gui.guiutil.myguidata import *
from OpenElectrophy.gui.guiutil.picklesettings import PickleSettings

import quantities as pq
import numpy as np
import datetime


url = 'sqlite:///test_db_1.sqlite'



class Parameters(DataSet):
    parentnum = ChoiceItem('Wich parent to change', ['1','2','3'])
    anint = IntItem('an integer', 5)
    name = StringItem('the name', default = 'sam')
    afloat = FloatItem('a float', np.pi)
    thedatetime = DateTimeItem('the datetime', datetime.datetime.now())
    description = TextItem('description', default ='multiline')
    
    password = PasswordItem('the password', default = 'secret', )
    
    limits = FloatRangeItem('limits' , default = (-.5,.5) )


def test1():
    app = QApplication([ ])
    w = ParamWidget( Parameters, title = 'yep')
    w.show()
    app.exec_()
    for k,v in w.to_dict().items():
        print k,v

def test2():
    """update"""
    app = QApplication([ ])
    w = ParamWidget( Parameters, title = 'yep')
    w.show()
    d = {'name' : 'toto' }
    w.update(d)
    app.exec_()
    for k,v in w.to_dict().items():
        print k,v


def test3():
    """ With settings """
    app = QApplication([ ])
    
    settings = PickleSettings(applicationname = 'testOE3')
    w = ParamWidget( Parameters, title = 'with settings', 
                        settings = settings, settingskey = 'a good dataset')
    w.show()
    app.exec_()

    for k,v in w.to_dict().items():
        print k,v




if __name__ == '__main__':
    test1()
    #~ test2()
    #~ test3()

    