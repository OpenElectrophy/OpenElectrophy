# -*- coding: utf-8 -*-
"""
Event viewers
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


class RectItem(pg.GraphicsWidget):
    def __init__(self, rect, border = 'r', fill = 'g'):
        pg.GraphicsWidget.__init__(self)
        self.rect = rect
        self.border= border
        self.fill= fill
    
    def boundingRect(self):
        return QRectF(0, 0, self.rect[2], self.rect[3])
        
    def paint(self, p, *args):
        p.setPen(pg.mkPen(self.border))
        p.setBrush(pg.mkBrush(self.fill))
        p.drawRect(self.boundingRect())

param_global = [
    {'name': 'xsize', 'type': 'logfloat', 'value': 10., 'step': 0.1},
    {'name': 'background_color', 'type': 'color', 'value': 'k' },    
    ]

param_by_channel = [ 
                #~ {'name': 'name', 'type': 'str', 'value': '','readonly' : True},
                {'name': 'color', 'type': 'color', 'value': "FF0"},
                {'name': 'visible', 'type': 'bool', 'value': True},
            ] 





class EventViewer(ViewerBase):
    """
    """
    def __init__(self, parent = None,
                            eventarrays = [ ],xsize=5.):
        super(EventViewer,self).__init__(parent)
        
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
        self.set_eventarrays(eventarrays)
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

    def set_eventarrays(self, eventarrays):
        self.clear_all()
        self.eventarrays = eventarrays
        self.eventarrays_items = [ [ ] for ea in self.eventarrays]

        all = [ ]
        for i, ep in enumerate(self.eventarrays):
            if 'channel_index' in ep.annotations:
                name = 'EpochArray {} name={} channel_index={}'.format(i, ep.name, ep.annotations['channel_index'])
            else:
                name = 'EpochArray {} name={}'.format(i, ep.name)
            all.append({ 'name': name, 'type' : 'group', 'children' : param_by_channel})
        self.paramEpochs = pg.parametertree.Parameter.create(name='EventArrays', type='group', children=all)
        
        for i, ep in enumerate(self.eventarrays):
            color = ep.annotations.get('color', None)
            if color is not None:
                self.paramEpochs.children()[i].param('color').setValue(color)
        
        
        self.allParams = pg.parametertree.Parameter.create(name = 'all param', type = 'group', children = [self.paramGlobal,self.paramEpochs  ])
        
        self.paramControler = EpochViewerControler(viewer = self)
        
        #~ self.paramEpochs.sigTreeStateChanged.connect(self.refresh)
        self.proxy = pg.SignalProxy(self.allParams.sigTreeStateChanged, rateLimit=5, delay=0.1, slot=self.refresh)
    
    def open_configure_dialog(self):
        self.paramControler.setWindowFlags(Qt.Window)
        self.paramControler.show()
    
    def refresh(self, fast = False):
        color = self.paramGlobal.param('background_color').value()
        self.graphicsview.setBackground(color)
        
        t_start, t_stop = self.t-self.xsize/3. , self.t+self.xsize*2/3.
        
        n = len(self.eventarrays)
        for e, epocharray in enumerate(self.eventarrays):
            for item in self.eventarrays_items[e]:
                self.plot.removeItem(item)
            self.eventarrays_items[e] = [ ]
            t = epocharray.times
            ind = ( (t>=t_start) & (t<t_stop) )
            for i in np.where(ind)[0]:
                color = self.paramEpochs.children()[e].param('color').value()
                color2 = QColor(color)
                color2.setAlpha(130)
                item = RectItem([t[i], n-e-1, 0., .9],  border = color, fill = color2)
                item.setPos(t[i], n-e-1)
                self.plot.addItem(item)
                self.eventarrays_items[e].append(item)
        
        self.vline.setPos(self.t)
        self.plot.setXRange( t_start, t_stop)
        self.plot.setYRange( 0, len(self.eventarrays))
        self.is_refreshing = False




class EpochViewerControler(QWidget):
    def __init__(self, parent = None, viewer = None):
        super(EpochViewerControler, self).__init__(parent)


        self.viewer = viewer

        #layout
        self.mainlayout = QVBoxLayout()
        self.setLayout(self.mainlayout)
        
        t = u'Options for EventArrays'
        self.setWindowTitle(t)
        self.mainlayout.addWidget(QLabel('<b>'+t+'<\b>'))
        
        h = QHBoxLayout()
        self.mainlayout.addLayout(h)
        
        self.treeParamEpoch = pg.parametertree.ParameterTree()
        self.treeParamEpoch.header().hide()
        h.addWidget(self.treeParamEpoch)
        self.treeParamEpoch.setParameters(self.viewer.paramEpochs, showTop=True)
        
        
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
        n = len(self.viewer.eventarrays)
        cmap = get_cmap('jet' , n)
        for i, pEpoch in enumerate(self.viewer.paramEpochs.children()):
            color = [ int(c*255) for c in ColorConverter().to_rgb(cmap(i)) ] 
            pEpoch.param('color').setValue(color)
       
            

