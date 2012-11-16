# -*- coding: utf-8 -*-
"""
Signal viewers
"""


from tools import *



from matplotlib.cm import get_cmap
from matplotlib.colors import ColorConverter



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
        

class EpochViewer(ViewerBase):
    """
    """
    def __init__(self, parent = None,
                            epocharrays = [ ],xsize=5.):
        super(EpochViewer,self).__init__(parent)
        
        self.mainlayout = QHBoxLayout()
        self.setLayout(self.mainlayout)
        
        viewBox = OptionsViewBox()
        viewBox.clicked.connect(self.open_configure_dialog)
        self.graphicsview  = pg.GraphicsView()
        self.mainlayout.addWidget(self.graphicsview)
        self.plot = pg.PlotItem(viewBox = viewBox)
        self.graphicsview.setCentralItem(self.plot)

        
        self.paramGlobal = pg.parametertree.Parameter.create( name='Global options', type='group',
                                                    children = [ {'name': 'xsize', 'type': 'logfloat', 'value': 10., 'step': 0.1},
                                                                        {'name': 'background_color', 'type': 'color', 'value': 'k' },
                                                                    ])
        
        # inialize
        self.clear_all()
        self.set_epocharrays(epocharrays)
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

    def set_epocharrays(self, epocharrays):
        self.clear_all()
        self.epocharrays = epocharrays
        self.epocharrays_items = [ [ ] for ea in self.epocharrays]
        
        self.epochViewerParameters = EpochViewerParameters(paramGlobal = self.paramGlobal, epocharrays = epocharrays, parent= self)
        self.epochViewerParameters.setWindowFlags(Qt.Window)
        self.paramEpochs = self.epochViewerParameters.paramEpochs
        
        for p in self.paramEpochs:
            p.sigTreeStateChanged.connect(self.refresh)
    
    def open_configure_dialog(self):
        self.epochViewerParameters.setWindowFlags(Qt.Window)
        self.epochViewerParameters.show()
    
    def refresh(self, fast = False):
        color = self.paramGlobal.param('background_color').value()
        self.graphicsview.setBackground(color)
        
        
        t_start, t_stop = self.t-self.xsize/3. , self.t+self.xsize*2/3.

        #~ text = pg.TextItem(html='<div style="text-align: center"><span style="color: #FFF;">This is the</span><br><span style="color: #FF0; font-size: 16pt;">PEAK</span></div>', anchor=(-0.3,1.3), border='w', fill=(0, 0, 255, 100))
        #~ plot.addItem(text)
        #~ plot.addItem(text)
        #~ text.setPos(0, y.max())
        
        
        
        #~ for e, epocharray in enumerate(self.epocharrays):
            #~ for item in self.epocharrays_range_item[e]:
                #~ self.plot.del_item(item)
            #~ self.epocharrays_range_item[e] = [ ]
            #~ t = epocharray.times
            #~ d = epocharray.durations
            #~ ind = ( (t>=t_start) & (t<t_stop) ) | ( (t+d>=t_start) & (t+d<t_stop) ) | ( (t<=t_start) & (t+d>t_stop))
            #~ for i in where(ind)[0]:
                #~ item = make.rectangle(t[i], e, t[i] + d[i], e+.9, title=epocharray.name)

        for e, epocharray in enumerate(self.epocharrays):
            for item in self.epocharrays_items[e]:
                self.plot.removeItem(item)
            self.epocharrays_items[e] = [ ]
            t = epocharray.times
            d = epocharray.durations
            ind = ( (t>=t_start) & (t<t_stop) ) | ( (t+d>=t_start) & (t+d<t_stop) ) | ( (t<=t_start) & (t+d>t_stop))
            for i in np.where(ind)[0]:
                #~ item = make.rectangle(t[i], e, t[i] + d[i], e+.9, title=epocharray.name)
                #~ item = pg.TextItem('yep',  color='g', html=None, anchor=(0, 1), border='b', fill='r')
                #~ print t[i], e
                #~ item = QGraphicsRectItem(t[i], e, t[i] + d[i], e+.9)
                #~ item.setBrush(pg.mkBrush('r'))
                color = self.paramEpochs[e].param('color').value()
                color2 = QColor(color)
                color2.setAlpha(130)
                item = RectItem([t[i], e, d[i], .9],  border = color, fill = color2)
                
                
                item.setPos(t[i], e)
                self.plot.addItem(item)
                self.epocharrays_items[e].append(item)



        
        self.vline.setPos(self.t)
        self.plot.setXRange( t_start, t_stop)
        self.plot.setYRange( 0, len(self.epocharrays))
        self.is_refreshing = False




class EpochViewerParameters(QWidget):
    def __init__(self, parent = None, epocharrays = [ ], paramGlobal = None):
        super(EpochViewerParameters, self).__init__(parent)
        
        param_by_channel = [ 
                        {'name': 'name', 'type': 'str', 'value': '','readonly' : True},
                        {'name': 'color', 'type': 'color', 'value': "FF0"},
                        {'name': 'visible', 'type': 'bool', 'value': True},
                    ] 
        
        self.epocharrays = epocharrays
        self.paramGlobal = paramGlobal
        
        #~ self.all_abs_max = np.array([ np.max(np.abs(anasig.magnitude)) for anasig in self.epocharrays ])
        #~ self.all_abs_max = np.array([ np.abs(np.std(anasig.magnitude)) for anasig in self.epocharrays ])
        
        

        self.mainlayout = QVBoxLayout()
        self.setLayout(self.mainlayout)
        t = u'Options for epocharrays'
        self.setWindowTitle(t)
        self.mainlayout.addWidget(QLabel('<b>'+t+'<\b>'))
        
        h = QHBoxLayout()
        self.mainlayout.addLayout(h)
        
        self.paramRoot = pg.parametertree.Parameter.create(name='epocharrays', type='group', children=[ ])
        self.paramEpochs = [ ]
        for i, anasig in enumerate(self.epocharrays):
            pSignal = pg.parametertree.Parameter.create( name='EpochArray {}'.format(i), type='group', children = param_by_channel)
            for k in ['channel_name', 'channel_index']:
                if k in anasig.annotations:
                    pSignal.param(k).setValue(anasig.annotations[k])
            self.paramEpochs.append(pSignal)
            self.paramRoot.addChild(pSignal)
        
        self.tree2 = pg.parametertree.ParameterTree()
        self.tree2.header().hide()
        h.addWidget(self.tree2, 4)
        self.tree2.setParameters(self.paramRoot, showTop=True)
        self.tree2.setSelectionMode(QAbstractItemView.ExtendedSelection)
        
        for pSignal in self.paramEpochs:
            treeitem = pSignal.items.keys()[0]
            if treeitem is not None:
                treeitem.setExpanded(False)

        
        
        v = QVBoxLayout()
        h.addLayout(v)
        
        self.tree3 = pg.parametertree.ParameterTree()
        self.tree3.header().hide()
        v.addWidget(self.tree3)
        self.tree3.setParameters(self.paramGlobal, showTop=True)

        self.paramSelection = pg.parametertree.Parameter.create( name='Multiple change for selection', type='group',
                                                    children = param_by_channel[2:], tip= u'This options apply on selection EpochArray on left list')
        self.paramSelection.sigTreeStateChanged.connect(self.paramSelectionChanged)
        self.tree1 = pg.parametertree.ParameterTree()
        self.tree1.header().hide()
        v.addWidget(self.tree1)
        self.tree1.setParameters(self.paramSelection, showTop=True)
        

        v.addWidget(QLabel(self.tr('<b>Automatic color:<\b>'),self))
        but = QPushButton('Progressive')
        but.clicked.connect(self.automatic_color)
        v.addWidget(but)


    
    def automatic_color(self):
        n = len(self.epocharrays)
        cmap = get_cmap('jet' , n)
        for i, pEpoch in enumerate(self.paramEpochs):
            color = [ int(c*255) for c in ColorConverter().to_rgb(cmap(i)) ] 
            pEpoch.param('color').setValue(color)
       
            
    def paramSelectionChanged(self, param, changes):
        for pSignal in self.paramEpochs:
            treeitem =  pSignal.items.keys()[0]
            for param, change, data in changes:
                if treeitem in self.tree2.selectedItems():
                    pSignal.param(param.name()).setValue(data)        



