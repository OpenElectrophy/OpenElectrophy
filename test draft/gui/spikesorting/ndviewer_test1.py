import sys
sys.path = [ '../../..' ] + sys.path

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from scipy import cluster

from OpenElectrophy.gui.spikesorting.ndviewer import NDViewer
from OpenElectrophy.gui.guiutil.picklesettings import PickleSettings

import numpy as np

def test1():
    app = QApplication([ ])

    colors = [ 'c' , 'g' , 'r' , 'b' , 'k' , 'm' , 'y']*100
    nstates = 5
    ndim = 8
    n = 40
    
    data = np.zeros((0,ndim), 'f')
    for i in range(ndim):
        d = np.random.randn(n, ndim)
        d = d * (1.+np.random.randn()/4) + np.random.randn()*5
        data = np.concatenate( (data, d), axis =0)    
    
    settings = PickleSettings(applicationname = 'testOE3')
    
    w = NDViewer(
                            settings = settings,
                                show_tour = True,
                                show_select_tools = True,
                            )
    
    codebook , distor =  cluster.vq.kmeans(data , nstates)
    dataLabels, distor = cluster.vq.vq(data , codebook)
    
    w.change_point(data[:,1:5])
    w.change_point(data , dataLabels)
    w.show()

    app.exec_()

if __name__ == '__main__' :
    test1()
