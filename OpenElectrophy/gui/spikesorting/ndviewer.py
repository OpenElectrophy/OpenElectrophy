# -*- coding: utf-8 -*-
"""
.. autoclass: NDViewer

"""
from ..qt import *


import quantities as pq
import numpy as np


from ..guiutil.myguidata import *
from ..guiutil.mymatplotlib import *


import matplotlib
from matplotlib.pyplot import get_cmap
from matplotlib.lines import Line2D
from matplotlib.patches import Polygon, Circle
from matplotlib.widgets import Lasso
from matplotlib.cm import get_cmap
if (matplotlib.__version__ < '1.2'):
    from matplotlib.nxutils import points_inside_poly
else:
    from matplotlib.path import Path as mpl_path



class PlotParameters(DataSet):
    autoscale = BoolItem('autoscale', default = True)
    xlim = FloatRangeItem('xlim', default = [-4.,4])
    ylim = FloatRangeItem('ylim', default = [-4.,4])
    force_orthonormality = BoolItem('force_orthonormality', default = True)
    refresh_interval = FloatItem('Refresh interval (ms)', default = 100.)
    nsteps = IntItem('Nb of steps for tour)', default = 20.)
    display_circle = BoolItem('Display circle', default = True)



class NDViewer(QWidget):
    """
    This is a widget for visulazation of hight dimentional space.
    
    This is similar to GGobi http://www.ggobi.org/publications/.
    
    """
    selection_changed = pyqtSignal()
    
    def __init__(self , parent=None ,
                                settings = None,
                                show_tour = True,
                                show_select_tools = False,
                                ):
        super(NDViewer, self).__init__(parent)
        
        self.settings = settings
        self.show_tour = show_tour
        self.show_select_tools = show_select_tools
        self.plot_parameters = ParamWidget(PlotParameters).to_dict()
        
        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)
        
        h = QHBoxLayout()
        mainLayout.addLayout(h)
        
        self.widgetProjection = QWidget()
        
        v = QVBoxLayout()
        h.addLayout(v)
        self.scrollArea = QScrollArea()
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scrollArea.setWidget(  self.widgetProjection ) 
        self.scrollArea.setMinimumWidth(180)
        v.addWidget( self.scrollArea )
        
        if show_tour:
            self.randButton = QPushButton( QIcon(':/roll.png') , 'Random')
            v.addWidget(self.randButton)
            self.randButton.clicked.connect(self.randomPosition)
            
            self.startRandTourButton = QPushButton( QIcon(':/helicoper_and_roll.png') , 'Random tour', checkable = True)
            v.addWidget(self.startRandTourButton)
            self.startRandTourButton.clicked.connect(self.startStopTour)
            self.timerRandTour = QTimer(interval  = self.plot_parameters['refresh_interval'])
            self.timerRandTour.timeout.connect(self.stepRandTour)

            self.startOptimizedTourButton = QPushButton( QIcon(':/helicoper_and_magic.png') , 'Optimized tour', checkable = True)
            v.addWidget(self.startOptimizedTourButton)
            self.startOptimizedTourButton.clicked.connect(self.startStopTour)
            self.connect(self.startOptimizedTourButton, SIGNAL('clicked()') , self.startStopTour)
            self.timerOptimizedTour = QTimer(interval  = self.plot_parameters['refresh_interval'])
            self.timerOptimizedTour.timeout.connect(self.stepOptimizedTour)
        
        but = QPushButton( QIcon(':/configure.png') , 'Configure')
        v.addWidget(but)
        but.clicked.connect(self.openConfigure)
        
        if show_select_tools:
            h2 = QHBoxLayout()
            groupbox = QGroupBox( 'Selection mode')
            groupbox.setLayout(h2)
            v.addWidget(groupbox)
            
            icons = [
                            ['pickone' , ':/color-picker.png'],
                            ['lasso' , ':/lasso.png'],
                            ['contour' , ':/polygon-editor.png'],
                        ]
            self.selectButton = { }
            for name, icon in icons:
                but = QPushButton(QIcon(icon),'', checkable = True, autoExclusive = True)
                h2.addWidget(but)
                but.clicked.connect(self.changeSelectMode)
                self.selectButton[name] = but
            
            self.clearSelectBut = QPushButton(QIcon(':/view-refresh.png'),'Clear selection')
            v.addWidget(self.clearSelectBut)
            self.clearSelectBut.clicked.connect(self.clearSelection)
        
        self.canvas = SimpleCanvas()
        self.ax = self.canvas.fig.add_axes([0.02, 0.02, .96, .96])
        h.addWidget(self.canvas,2)
        self.canvas.setMinimumWidth(180)
        
        self.ax_circle = None
        self.create_axe_circle()
        
        self.tour_running = False
        
        
        self.dim = 0 #
        self.spins = [ ] # spin widget list
        
        self.toBeDisconnected = [ ] # manage mpl_connect and disconnect
        self.selectMode =  None # actual mode
        self.epsilon = 4. # for pickle event
        self.poly = None # for contour
        
        self.selectionLine = None
        
        self.selection_changed.connect(self.redrawSelection)

    ## draw and redraw ##
    def change_dim(self, ndim):
        
        self.projection = np.zeros( (ndim, 2))
        self.projection[0,0] = 1
        self.projection[1,1] = 1
        
        #spinwidgets
        self.widgetProjection = QWidget()
        self.widgetProjection.updateGeometry()
        g = QGridLayout()
        self.widgetProjection.setLayout(g)
        self.spins = [ ]
        for i in range(ndim):
            d1 = QDoubleSpinBox(value = self.projection[i,0])
            d2 = QDoubleSpinBox(value = self.projection[i,1])
            g.addWidget( QLabel('dim {}'.format(i)), i, 0 )
            g.addWidget( d1, i, 1 )
            g.addWidget( d2, i, 2 )
            for d in [d1, d2]:
                d.valueChanged.connect(self.spinsChanged)
                d.setSingleStep(0.05)
                d.setRange(-1.,1.)
            self.spins.append( [d1, d2] )
        
        self.scrollArea.setWidget(  self.widgetProjection )
        self.scrollArea.update()
        self.dim = ndim
        
    
    def change_point(self, data, data_labels = None, colors = None, subset = None):
        """
        data =       dim 0 elements
                        dim 1 dimension
        data_labels = vector of cluster for colors
        """
        
        if data.shape[1] != self.dim :
            self.change_dim(data.shape[1])
        self.data = data
        
        self.actualSelection = np.zeros(data.shape[0], dtype = bool)
        
        if data_labels is None:
            data_labels = np.zeros( data.shape[0], dtype = 'i')
        self.data_labels = data_labels
        self.all_labels = np.unique(self.data_labels)
        
        if colors is None:
            colors =  [ 'c' , 'g' , 'r' , 'b' , 'k' , 'm' , 'y']*100
        self.colors = colors
        
        if subset is None:
            subset = { }
            for c in self.all_labels:
                ind = self.data_labels ==c
                subset[c] = ind
        self.subset = subset
        
        self.fullRedraw()
        self.refreshSpins()
        
    def fullRedraw(self):
        self.ax.clear()
        for c in self.all_labels:
            ind = self.subset[c]
            proj = np.dot( self.data[ind,:], self.projection ) 
            self.ax.plot( proj[:,0], proj[:,1], #proj[ind,0] , proj[ind,1],
                                                linestyle = 'None',
                                                marker = '.', 
                                                color = self.colors[c],
                                                picker=self.epsilon)
        self.redraw()
        
    def redraw(self):
        if not(self.plot_parameters['autoscale']):
            self.ax.set_xlim( self.plot_parameters['xlim'] )
            self.ax.set_ylim( self.plot_parameters['ylim'] )
        self.canvas.draw()

    def spinsChanged(self,value):
        for i in range(self.projection.shape[0]):
            self.projection[i,0] =self.spins[i][0].value()
            self.projection[i,1] =self.spins[i][1].value()

        if self.plot_parameters['force_orthonormality']:
            m = np.sqrt(np.sum(self.projection**2, axis=0))
            m = m[np.newaxis, :]
            self.projection /= m
            self.refreshSpins()

        self.fullRedraw()
    
    def refreshSpins(self):
        for i in range(self.projection.shape[0]):
            d1, d2 = self.spins[i]
            for d in [d1,d2]:
                d.valueChanged.disconnect(self.spinsChanged)
            d1.setValue(self.projection[i,0])
            d2.setValue(self.projection[i,1])
            
            for d in [d1,d2]:
                d.valueChanged.connect(self.spinsChanged)
        
        if self.plot_parameters['display_circle']:
            self.refreshCircleRadius()
    
    def refreshCircleRadius(self):
        for l in self.radiusLines:
            self.ax_circle.lines.remove(l)
        
        self.radiusLines = [ ]
        for i in range(self.projection.shape[0]):
            l, = self.ax_circle.plot([0,self.projection[i,0]] , [0 , self.projection[i,1]]  , color = 'g')
            self.radiusLines.append(l)
        self.canvas.draw()
    
    def create_axe_circle(self):
        if self.plot_parameters['display_circle']:
            if self.ax_circle is None:
                ax= self.canvas.fig.add_axes([0.04, 0.04, .1, .1])
            else:
                ax = self.ax_circle
            ax.clear()
            ax.set_xticks([ ])
            ax.set_yticks([ ])
            circle = Circle((0,0) , radius = 1. , facecolor = 'w')
            ax.add_patch(circle)
            ax.set_xlim([-1.02,1.02])
            ax.set_ylim([-1.02,1.02])
            
            
            self.ax_circle = ax
            self.canvas.draw()
            self.radiusLines = [ ]
        else:
            if self.ax_circle is not None:
                self.canvas.fig.delaxes(self.ax_circle)
                self.ax_circle = None
    
    
    ## config ##
    def openConfigure(self):
        dia = ParamDialog(PlotParameters, settings = self.settings, settingskey = 'ndviewer/options' ,title = 'Plot parameters',)
        dia.update(self.plot_parameters)
        if dia.exec_():
            self.plot_parameters = dia.to_dict()
            self.timerRandTour.setInterval(self.plot_parameters['refresh_interval'])
            self.timerOptimizedTour.setInterval(self.plot_parameters['refresh_interval'])
            self.create_axe_circle()
            self.fullRedraw()
    
    ## random and tour tour ##
    def randomPosition(self):
        ndim = self.projection.shape[0]
        self.projection = np.random.rand(ndim,2)*2-1.
        if self.plot_parameters['force_orthonormality']:
            m = np.sqrt(np.sum(self.projection**2, axis=0))
            self.projection /= m
        self.refreshSpins( )
        self.fullRedraw( )    
    
    def startStopTour(self):
        if self.sender() == self.startRandTourButton:
            but = self.startRandTourButton
            mode = 'rand'
            self.startOptimizedTourButton.setChecked(False)
            
        elif self.sender() == self.startOptimizedTourButton:
            but = self.startOptimizedTourButton
            mode = 'optimized'
            self.startRandTourButton.setChecked(False)
        
        start = but.isChecked()
        
        if start:
            if self.show_select_tools:
                for name, but in self.selectButton.iteritems():
                    but.setChecked(False)
                    but.setEnabled(False)
                self.clearSelectBut.setEnabled(False)
                self.selectMode =  None
                self.clearSelection()
            
            if mode == 'rand':
                self.timerOptimizedTour.stop()
                self.timerRandTour.start()
                self.actualStep = self.plot_parameters['nsteps'] +1
            elif mode == 'optimized':
                self.timerRandTour.stop()
                self.timerOptimizedTour.start()
                
                self.tour_running = True
        else:
            if self.show_select_tools:
                for name, but in self.selectButton.iteritems():
                    but.setEnabled(True)
                self.clearSelectBut.setEnabled(True)
                self.changeSelectMode()
            
            self.timerRandTour.stop()
            self.timerOptimizedTour.stop()
            self.tour_running = False
        
        self.refreshSpins( )
        self.fullRedraw( )
        
        
    
    def stepRandTour(self):
        nsteps = self.plot_parameters['nsteps']
        ndim = self.projection.shape[0]
        
        if self.actualStep >= nsteps:
            # random for next etap
            nextEtap = np.random.rand(ndim,2)*2-1.
            self.allSteps = np.empty( (ndim , 2 ,  nsteps))
            for i in range(ndim):
                for j in range(2):
                    self.allSteps[i,j , : ] = np.linspace(self.projection[i,j] , nextEtap[i,j] , nsteps)
                
            if self.plot_parameters['force_orthonormality']:
                m = np.sqrt(np.sum(self.allSteps**2, axis=0))
                m = m[np.newaxis, : ,  :]
                self.allSteps /= m
                    
            self.actualStep = 0
            
        self.projection = self.allSteps[:,: ,  self.actualStep] 
        self.actualStep += 1
        self.refreshSpins( )
        self.fullRedraw( )
    


    def stepOptimizedTour(self):
        actual_lda =  ComputeIndexLda(self.projection, self.data, self.data_labels)
        
        nloop = 1
        ndim = self.projection.shape[0]        
        for i in range(nloop):
            delta = (np.random.rand(ndim, 2)*2-1)/20.
            new_proj = self.projection + delta
            # normalize orthonormality
            m = np.sqrt(np.sum(new_proj**2, axis=0))
            m = m[np.newaxis, :]
            new_proj /= m
            
            new_lda = ComputeIndexLda(new_proj, self.data, self.data_labels)
            if new_lda >=actual_lda:
                actual_lda = new_lda
                self.projection = new_proj
        self.refreshSpins()
        self.fullRedraw()


    ## selections ##
    def changeSelection(self, new_selection, emit_signal = False):
        self.actualSelection = new_selection
        if emit_signal:
            self.selection_changed.emit()
        if not self.tour_running:
            self.redrawSelection()
    
    def changeSelectMode(self):
        self.selectMode = None
        for name, but in self.selectButton.iteritems():
            if but.isChecked():
                self.selectMode = name
        for e in self.toBeDisconnected:
            self.canvas.mpl_disconnect(e)
        self.toBeDisconnected = [ ]
        
        self.clearSelection()
    
    def clearSelection(self):
        self.clearArtistSelection()
        
        if self.selectMode =='pickone':
            cid = self.canvas.mpl_connect('pick_event', self.onPick)
            self.toBeDisconnected.append(cid)
            
        elif self.selectMode =='contour':
            cid1 = self.canvas.mpl_connect('button_press_event', self.pressContour)
            cid2 = self.canvas.mpl_connect('button_release_event', self.releaseContour)
            cid3 = self.canvas.mpl_connect('motion_notify_event', self.motionContour)
            self.toBeDisconnected += [cid1, cid2, cid3 ]
            self.poly =None
            self._ind = None
        
        elif self.selectMode =='lasso':
            cid = self.canvas.mpl_connect('button_press_event', self.startLasso)
            self.toBeDisconnected.append(cid)
        
        self.actualSelection[:] = False
        
        self.selection_changed.emit()
        
        
    
    def clearArtistSelection(self):
        if self.poly is not None:
            self.ax.lines.remove(self.line)
            self.ax.patches.remove(self.poly)
            self.poly = None
            self.line = None
            self.redraw()
        
        # should not:
        if hasattr(self,'lasso'):
            self.canvas.widgetlock.release(self.lasso)
            del self.lasso            
        
    def onPick(self , event):
        if isinstance(event.artist, Line2D):
            xdata, ydata = event.artist.get_data()
            x,y = xdata[event.ind[0]], ydata[event.ind[0]]
            self.actualSelection[:] = False
            self.actualSelection[np.argmin( np.sum( (np.dot( self.data, self.projection )-np.array([[ x,y ]]) )**2 , axis=1)) ]  = True
        else:
            self.actualSelection[:] = False
        
        self.selection_changed.emit()

    
    def startLasso(self, event):
        if event.button != 1: return
        
        
        if self.canvas.widgetlock.locked():
            # sometimes there is a bug lassostop is not intercepted!!!
            # so to avoid 2 start
            self.clearArtistSelection()
            return
        if event.inaxes is None: return

        self.lasso = Lasso(event.inaxes, (event.xdata, event.ydata), self.stopLasso)
        # acquire a lock on the widget drawing
        self.canvas.widgetlock(self.lasso)
        
    def stopLasso(self, verts):
        self.actualSelection = inside_poly(np.dot( self.data, self.projection ), verts)

        self.canvas.widgetlock.release(self.lasso)
        del self.lasso
        self.selection_changed.emit()
    
    def pressContour(self, event):
        if event.inaxes==None: return
        if event.button != 1: return
        
        # new contour
        if self.poly is None:
            self.poly = Polygon( [[event.xdata , event.ydata]] , animated=False , alpha = .3 , color = 'g')
            self.ax.add_patch(self.poly)
            self.line, = self.ax.plot([event.xdata] , [event.ydata] , 
                                    color = 'g',
                                    linewidth = 2 ,
                                    marker = 'o' ,
                                    markerfacecolor='g', 
                                    animated=False)
            self.redraw()
            return
        
        
        # event near a point
        xy = np.asarray(self.poly.xy)
        xyt = self.poly.get_transform().transform(xy)
        xt, yt = xyt[:, 0], xyt[:, 1]
        d = np.sqrt((xt-event.x)**2 + (yt-event.y)**2)
        indseq = np.nonzero(np.equal(d, np.amin(d)))[0]
        self._ind = indseq[0]
        if d[self._ind]>=self.epsilon:
            self._ind = None

        
        # new point
        if self._ind is None:
            self.poly.xy = np.array( list(self.poly.xy) +  [[event.xdata , event.ydata]])
            self.line.set_xdata( np.array(list(self.line.get_xdata()) + [ event.xdata]) )
            self.line.set_ydata( np.array(list(self.line.get_ydata()) + [ event.ydata]) )
            self.redraw()

        self.actualSelection = inside_poly(np.dot( self.data, self.projection ), self.poly.xy)
        self.selection_changed.emit()
    
    
    def releaseContour(self , event):
        if event.button != 1: return
        self._ind = None

    def motionContour(self , event):
        if self._ind is None: return
        if event.inaxes is None: return
        if event.button != 1: return
        x,y = event.xdata, event.ydata

        self.poly.xy[self._ind] = x,y
        self.line.set_data(zip(*self.poly.xy))
        self.redraw()

        self.actualSelection = inside_poly(np.dot( self.data, self.projection ), self.poly.xy)
        self.selection_changed.emit()
    
    def redrawSelection(self):
        if self.selectionLine is not None:
            if self.selectionLine in self.ax.lines:
                self.ax.lines.remove(self.selectionLine)
        
        
        if np.sum(self.actualSelection)>1:
            # for big selection only subset are shown
            sel = np.zeros(self.data.shape[0], dtype = bool)
            for c in self.all_labels:
                ind = self.subset[c]
                sel[ind] = True
            sel = sel & self.actualSelection
            proj = np.dot( self.data[sel, :], self.projection )
        else:
            # for small selection also hideen spike are shown
            proj = np.dot( self.data[self.actualSelection, :], self.projection )
        
        self.selectionLine, = self.ax.plot(proj[:,0] , proj[:,1],
                                                                linestyle = 'None',
                                                                markersize = 10,
                                                                marker = 'o' ,
                                                                markerfacecolor='m',
                                                                markeredgecolor='k',
                                                                alpha = .6,
                                                                )
        
        self.redraw()







def ComputeIndexLda(proj, data, data_labels): 
# takken from page 31 of book on GGOBI
# diane cook "integrative and dynamic graphics for data analysis
    ndim = proj.shape[0]
    
    A = np.matrix(proj, dtype = data.dtype)
    B = np.matrix(np.zeros((ndim, ndim)), dtype = data.dtype)
    W = np.matrix(np.zeros((ndim, ndim)), dtype = data.dtype)
    #~ grand_mean = np.mean(data , axis = 0).astype(np.matrix)
    grand_mean = np.mean(data , axis = 0)
    for c in np.unique(data_labels):
        ind = data_labels ==c
        #~ group_mean = np.mean(data[ind, :], axis = 0).astype(np.matrix)
        group_mean = np.mean(data[ind, :], axis = 0)
        d = group_mean - grand_mean
        #~ B += ind[ind].size*np.dot(d[:,np.newaxis], d[np.newaxis, :])
        B += np.sum(ind)*np.dot(d[:,np.newaxis], d[np.newaxis, :])
        
        # find better:
        d = data[ind, :] - group_mean
        for j in range(d.shape[0]):
            W+=np.dot(d[j,:, np.newaxis], d[j,np.newaxis,:])
        
    lda = 1 -  np.linalg.det(A.T*W*A) / np.linalg.det(A.T*(W+B)*A)
    return lda

def inside_poly(data, vertices):
    if(matplotlib.__version__ < '1.2'):
        return points_inside_poly(data, vertices)
    return mpl_path(vertices).contains_points(data)

