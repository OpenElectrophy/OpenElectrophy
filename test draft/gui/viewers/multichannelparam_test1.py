import sys
sys.path = [ '../../..' ] + sys.path

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from OpenElectrophy.gui.viewers import *
from OpenElectrophy.gui.viewers.multichannelparam import *



param_by_channel = [ 
                {'name': 'channel_name', 'type': 'str', 'value': '','readonly' : True},
                {'name': 'channel_index', 'type': 'str', 'value': '','readonly' : True},
                {'name': 'color', 'type': 'color', 'value': "FF0"},
                {'name': 'gain', 'type': 'float', 'value': 1, 'step': 0.1},
                {'name': 'offset', 'type': 'float', 'value': 0., 'step': 0.1},
                {'name': 'visible', 'type': 'bool', 'value': True},
            ]

nb = 32


all_channel_params = [ ]
for i in range(nb):
    all_channel_params.append({'name': 'Channel {}'.format(i), 'type': 'group', 'children': param_by_channel })
all_params = pg.parametertree.Parameter.create(name='Channel', type='group', children=all_channel_params)


def test1():
    app = QApplication([ ])
    w1 = MultiChannelParam(all_params = all_params, param_by_channel = param_by_channel)
    w1.show()

    w2 = pg.parametertree.ParameterTree()
    w2.show()
    w2.setParameters(all_params, showTop=True)
    
    
    app.exec_()
    

if __name__ == '__main__' :
    test1()
