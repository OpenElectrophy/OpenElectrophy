import sys
sys.path.append('../../..')

from PyQt4.QtCore import *
from PyQt4.QtGui import *


from OpenElectrophy.gui.guiutil.mypyqtgraph import *

import quantities as pq
import numpy as np
import datetime

params = [
        {'name': 'Integer', 'type': 'int', 'value': 10},
        {'name': 'Float', 'type': 'float', 'value': 10.5, 'step': 0.1},
        {'name': 'String', 'type': 'str', 'value': "hi"},
        {'name': 'ylims', 'type': 'range', 'value': [-5.,5.]},
        {'name': 'xsize', 'type': 'logfloat', 'value': 10.},
        {'name': 'choice', 'type': 'list', 'values': {"one": 1, "two": 2, "three": 3}, 'value': 2},
        
        
        {'name': 'pq1', 'type': 'quantity', 'value': 10.*pq.mV},
        {'name': 'pq2', 'type': 'quantity', 'value': 10.*pq.uV},
        
        ]


def test1():
    app = QApplication([ ])
    w = RangeWidget()
    w.show()
    
    p = Parameter.create(name='params', type='group', children=params)
    t = ParameterTree()
    t.setParameters(p, showTop=False)
    t.show()
    app.exec_()


def test2():
    app = QApplication([ ])
    w = SpinAndSliderWidget()
    w.setValue(50)
    w.show()
    
    p = Parameter.create(name='params', type='group', children=params)
    t = ParameterTree()
    t.setParameters(p, showTop=False)
    t.show()
    app.exec_()


def test3():
    import copy
    # pq cannot be copied
    params.append( {'name': 'subparam', 'type': 'group', 'children': copy.deepcopy(params[:-2])} )
    
    app = QApplication([ ])
    p = Parameter.create(name='params', type='group', children=params)
    t = ParameterTree()
    
    set_dict(p, { 'xsize' : 18. , 'subparam' : {'xsize' : 19.},  }, cascade = True)
    
    t.setParameters(p, showTop=False)
    t.show()
    app.exec_()
    print get_dict_from_group_param(p, cascade = False)

    print get_dict_from_group_param(p, cascade = True)
    #~ print Parameter
    #~ print p.to_dict(cascade = False)
    #~ print p.to_dict(cascade = True)


def test4():
    app = QApplication([ ])
    
    w = QuantityWidget(value = 10*pq.uV)
    w.show()
    
    app.exec_()
    


if __name__ == '__main__':
    #~ test1()
    #~ test2()
    test3()
    #~ test4()

    