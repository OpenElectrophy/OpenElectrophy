# -*- coding: utf-8 -*-
"""
Signal viewers
"""


from .tools import *



from matplotlib.cm import get_cmap
from matplotlib.colors import ColorConverter

class OptionsViewBox(pg.ViewBox):
    clicked = pyqtSignal()
    def __init__(self, *args, **kwds):
        pg.ViewBox.__init__(self, *args, **kwds)
    def mouseClickEvent(self, ev):
        self.clicked.emit()
    def mouseDragEvent(self, ev):
        ev.ignore()
    def wheelEvent(self, ev):
        ev.ignore()



param_global = [
    {'name': 'xsize', 'type': 'logfloat', 'value': 10., 'step': 0.1},
    {'name': 'background_color', 'type': 'color', 'value': 'k' },    
    ]

param_by_channel = [ 
                #~ {'name': 'name', 'type': 'str', 'value': '','readonly' : True},
                {'name': 'color', 'type': 'color', 'value': "FF0"},
                {'name': 'visible', 'type': 'bool', 'value': True},
            ] 





class SpikeTrainViewer(ViewerBase):
    """
    """
    def __init__(self, parent = None,
                            spiketrains = [ ],xsize=5.):
        super(SpikeTrainViewer,self).__init__(parent)
        
        self.mainlayout = QHBoxLayout()
        self.setLayout(self.mainlayout)
        
        viewBox = OptionsViewBox()
        viewBox.clicked.connect(self.open_configure_dialog)
        self.graphicsview  = pg.GraphicsView()
        self.mainlayout.addWidget(self.graphicsview)
        self.plot = pg.PlotItem(viewBox = viewBox)
        self.graphicsview.setCentralItem(self.plot)

        
        self.paramGlobal = pg.parametertree.Parameter.create( name='Global options', type='group',
                                                    children = param_global)
        
        # inialize
        self.clear_all()
        self.set_spiketrains(spiketrains)
        self.set_xsize(xsize)
        
        self.paramGlobal.sigTreeStateChanged.connect(self.refresh)
        
    
    def get_xsize(self):
        return self.paramGlobal.param('xsize').value()
    def set_xsize(self, xsize):
        self.paramGlobal.param('xsize').setValue(xsize)
    xsize = property(get_xsize, set_xsize)

    def clear_all(self):
        self.plot.clear()
        self.vline = pg.InfiniteLine(angle = 90, movable = False, pen = 'g')
        self.plot.addItem(self.vline)
        self.epocharray_curves = [ ]

    def set_spiketrains(self, spiketrains):
        self.clear_all()
        self.spiketrains = spiketrains
        
        all = [ ]
        for i, sptr in enumerate(self.spiketrains):
            if 'channel_index' in sptr.annotations:
                name = 'SpikeTrain {} name={} channel_index={}'.format(i, sptr.name, sptr.annotations['channel_index'])
            else:
                name = 'SpikeTrain {} name={}'.format(i, sptr.name)
            all.append({ 'name': name, 'type' : 'group', 'children' : param_by_channel})
        self.paramSpikeTrains = pg.parametertree.Parameter.create(name='SpikeTrains', type='group', children=all)
        
        self.scatters = [ ]
        for i, sptr in enumerate(self.spiketrains):
            color = sptr.annotations.get('color', None)
            if color is not None:
                self.paramSpikeTrains.children()[i].param('color').setValue(color)
            else:
                color = self.paramSpikeTrains.children()[i].param('color').value()


            s = pg.ScatterPlotItem(x=[], y=[], symbol = 's',
                                            pen=None, brush=color, size=10, pxMode = True)
            self.plot.addItem(s)
            self.scatters.append(s)
        
        self.allParams = pg.parametertree.Parameter.create(name = 'all param', type = 'group', children = [self.paramGlobal,self.paramSpikeTrains  ])
        
        self.paramControler = SpikeTrainViewerControler(viewer = self)
        
        #~ self.paramSpikeTrains.sigTreeStateChanged.connect(self.refresh)
        self.paramSpikeTrains.sigTreeStateChanged.connect(self.refreshColors)
        self.proxy = pg.SignalProxy(self.allParams.sigTreeStateChanged, rateLimit=5, delay=0.1, slot=self.refresh)
        
    
    def open_configure_dialog(self):
        self.paramControler.setWindowFlags(Qt.Window)
        self.paramControler.show()

    def refreshColors(self):
        for i, sptr in enumerate(self.spiketrains):
            p = self.paramSpikeTrains.children()[i]
            color = p.param('color').value()
            self.scatters[i].setBrush(color)
        
    def refresh(self, fast = False):
        color = self.paramGlobal.param('background_color').value()
        self.graphicsview.setBackground(color)
        
        t_start, t_stop = self.t-self.xsize/3. , self.t+self.xsize*2/3.
        
        for i, sptr in enumerate(self.spiketrains):
            times = sptr.magnitude
            x = times[(times>t_start) & (times<=t_stop)]
            #~ print x
            y = np.ones(x.size)*i
            self.scatters[i].setData(x, y)
        
        self.vline.setPos(self.t)
        self.plot.setXRange( t_start, t_stop)
        self.plot.setYRange( 0, len(self.spiketrains))
        self.is_refreshing = False




class SpikeTrainViewerControler(QWidget):
    def __init__(self, parent = None, viewer = None):
        super(SpikeTrainViewerControler, self).__init__(parent)


        self.viewer = viewer

        #layout
        self.mainlayout = QVBoxLayout()
        self.setLayout(self.mainlayout)
        
        t = u'Options for EpochArrays'
        self.setWindowTitle(t)
        self.mainlayout.addWidget(QLabel('<b>'+t+'<\b>'))
        
        h = QHBoxLayout()
        self.mainlayout.addLayout(h)
        
        self.treeParamEpoch = pg.parametertree.ParameterTree()
        self.treeParamEpoch.header().hide()
        h.addWidget(self.treeParamEpoch)
        self.treeParamEpoch.setParameters(self.viewer.paramSpikeTrains, showTop=True)
        
        
        v = QVBoxLayout()
        h.addLayout(v)
        
        self.treeParamGlobal = pg.parametertree.ParameterTree()
        self.treeParamGlobal.header().hide()
        v.addWidget(self.treeParamGlobal)
        self.treeParamGlobal.setParameters(self.viewer.paramGlobal, showTop=True)
        
        v.addWidget(QLabel(self.tr('<b>Automatic color:<\b>'),self))
        but = QPushButton('Progressive')
        but.clicked.connect(self.automatic_color)
        v.addWidget(but)


    
    def automatic_color(self):
        n = len(self.viewer.spiketrains)
        cmap = get_cmap('jet' , n)
        for i, p in enumerate(self.viewer.paramSpikeTrains.children()):
            color = [ int(c*255) for c in ColorConverter().to_rgb(cmap(i)) ] 
            p.param('color').setValue(color)
       
            

