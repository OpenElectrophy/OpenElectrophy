# -*- coding: utf-8 -*-
"""
Theses widget display individual spike on signals.
Widget based on: viewers.signalviewer

"""





from .base import *

from ..viewers import SignalViewer, TimeSeeker, XSizeChanger, YLimsChanger

import pyqtgraph as pg

class MyViewBox(pg.ViewBox):
    clicked = pyqtSignal()
    def __init__(self, *args, **kwds):
        pg.ViewBox.__init__(self, *args, **kwds)
    def mouseClickEvent(self, ev):
        self.clicked.emit()
    def mouseDragEvent(self, ev):
        ev.ignore()
    def wheelEvent(self, ev):
        ev.ignore()
        #~ print 'wheel'


class SignalAndSpike(SpikeSortingWidgetBase):
    
    refresh_on = [  ]
    icon_name = 'analogsignal.png'
    
    sig_name = None
    
    def __init__(self,**kargs):
        super(SignalAndSpike, self).__init__(**kargs)
        
        self.auto_zoom_x = True
        
        sps = self.spikesorter
        self.timerSeeker = TimeSeeker(show_play = False)
        
        self.sigs = getattr(self.spikesorter, self.sig_name)
        
        self.view = pg.GraphicsView()
        l = pg.GraphicsLayout()
        self.view.setCentralItem(l)
        self.mainLayout.addWidget(self.view)
        
        
        
        self.plots = [ ]
        self.curves = [ ]
        # TODO make auto scale off
        for i in range(sps.trodness):
            l.nextRow()
            viewBox = MyViewBox()
            plot = l.addPlot(viewBox = viewBox)
            self.plots.append(plot)
            plot.hideButtons()
            curve = plot.plot([np.nan], [np.nan], pen = 'w')
            self.curves.append(curve)
            viewBox.disableAutoRange()
            if i!=sps.trodness-1:
                plot.hideAxis('bottom')
        self.scatters = [ {} for i in range(sps.trodness) ]
        
        # fixme: fast seek or not ?
        #~ self.timerSeeker.time_changed.connect(self.seek)
        self.timerSeeker.fast_time_changed.connect(self.seek)
        

        self.time_by_seg = np.zeros(len(sps.segs), dtype = float)
        for s,seg in enumerate(sps.segs):
            self.time_by_seg[s]= sps.segs[s].analogsignals[0].t_start.magnitude
        
        
        self.mainLayout.addWidget(self.timerSeeker)
        
        #Seg selection
        tb = self.toolbar = QToolBar()
        self.mainLayout.addWidget(self.toolbar)
        
        but = QPushButton('<')
        but.clicked.connect(self.prev_segment)
        tb.addWidget(but)
        self.combo = QComboBox()
        tb.addWidget(self.combo)
        self.combo.addItems([ 'Segment {}'.format(i) for i in range(len(sps.segs)) ])
        but = QPushButton('>')
        but.clicked.connect(self.next_segment)
        tb.addWidget(but)
        self.num_seg = 0
        self.combo.currentIndexChanged.connect(self.refresh)
        tb.addSeparator()
        
        # winsize
        self.xsize = .5
        tb.addWidget(QLabel(u'X size (s)'))
        self.xsize_changer = XSizeChanger(xsize = self.xsize, xzoom_limits = (0.001, 10.),orientation  = Qt.Horizontal,)
        self.xsize_changer.set_targets([self] )
        tb.addWidget(self.xsize_changer)
        tb.addSeparator()
        self.xsize_changer.xsize_changed.connect(self.refresh, type = Qt.QueuedConnection)
        
        
        # ylims
        self.ylims = [0.,0.]
        for sig in self.sigs.reshape(-1).tolist():
            self.ylims[0] = min(self.ylims[0], sig.min())
            self.ylims[1] = max(self.ylims[1], sig.max())
        
        tb.addWidget(QLabel(u'Y limits'))
        self.ylims_changer = YLimsChanger(orientation  = Qt.Horizontal,)
        self.ylims_changer.set_ylims(self.ylims)
        self.ylims_changer.set_targets( [self] )
        tb.addWidget(self.ylims_changer)
        tb.addSeparator()
        self.ylims_changer.ylims_changed.connect(self.refresh, type = Qt.QueuedConnection)
        

    def seek(self, t):
        sps = self.spikesorter
        s =  self.combo.currentIndex()
        self.time_by_seg[s] = t
        sr = sps.sig_sampling_rate.rescale('Hz').magnitude
        
        t1,t2 = t-self.xsize/3. , t+self.xsize*2/3.
        
        # Chunk of signal
        ind_start = int(np.rint((t1-sps.seg_t_start[s].rescale('s').magnitude)*sr))
        ind_stop = int(np.rint((t2-sps.seg_t_start[s].rescale('s').magnitude)*sr))
        if ind_start<0:
            ind_start=0
            t1 = sps.seg_t_start[s].magnitude
        if ind_stop>self.sigs[0,s].size:
            ind_stop=self.sigs[0,s].size
            t2 = sps.seg_t_stop[s].magnitude
        
        t_vect = np.arange(0,ind_stop-ind_start, dtype='f')/sr+t1
        
        pos = sps.spike_index_array[s]
        for i in range(sps.trodness):
            if t_vect.size:
                self.curves[i].setData(t_vect, self.sigs[i,s][ind_start:ind_stop])
            else:
                self.curves[i].setData( [np.nan], [np.nan])
        
        # Spikes
        sl = sps.seg_spike_slices[s]
        pos = sps.spike_index_array[s]
        inwindow = (pos>ind_start) & (pos<ind_stop)
        pos = pos[inwindow]
        for c in sps.cluster_names.keys():
            clusters = sps.spike_clusters[sl][inwindow]
            ind = pos[clusters == c]
            r,g,b = sps.cluster_colors[c]
            #~ print r,g,b
            color = QColor( r*255,g*255,b*255  )
            #~ color = QColor('red')
            for i, scatter in enumerate(self.scatters):
                if c in scatter:
                    scatter[c].setData(t_vect[ind-ind_start], self.sigs[i,s][ind])
                else:
                    scatter[c] = pg.ScatterPlotItem(x=t_vect[ind-ind_start], y=self.sigs[i,s][ind], 
                                                                    pen=None, brush=color, size=10, pxMode = True)
                    self.plots[i].addItem(scatter[c])

        for plot in self.plots:
            plot.setXRange( t1, t2, padding = 0.0)
            plot.setYRange( *self.ylims , padding = 0.0)

        
        
    
    def refresh(self):
        sps = self.spikesorter
        s =  self.combo.currentIndex()
        
        t_start = sps.seg_t_start[s]
        t_stop = sps.seg_t_stop[s]
        self.timerSeeker.set_start_stop(t_start.magnitude-.05,t_stop.magnitude+.05, seek = False)
        self.timerSeeker.seek(self.time_by_seg[s])
        
        for c in sps.cluster_names.keys():
            r,g,b = sps.cluster_colors[c]
            color = QColor( r*255,g*255,b*255  )
            for i, scatter in enumerate(self.scatters):
                if c in scatter:
                    scatter[c].setBrush(color)
                    
            
            
        
        
        #~ spiketrains = [ ]
        #~ if sps.spike_index_array is not None:
            #~ sl = sps.seg_spike_slices[s]
            #~ pos = sps.spike_index_array[s]
            
            #~ times_and_colors = [ ]
            #~ if sps.spike_clusters is None:
                #~ times_and_colors.append( (pos/sps.sig_sampling_rate+t_start  , 'red') )
            #~ else:
                #~ for c in sps.cluster_names.keys():
                    #~ ind = sps.spike_clusters[sl] == c
                    #~ times = pos[ind]/sps.sig_sampling_rate+t_start
                    #~ times_and_colors.append( (pos[ind]/sps.sig_sampling_rate+t_start  , list(sps.cluster_colors[c])) )
            
            #~ for times, color in times_and_colors:
                #~ spiketrains.append(neo.SpikeTrain(times, t_start = t_start, t_stop = t_stop, color = color))
            
            #~ sel = sps.selected_spikes[sl]
            #~ spiketrains.append(neo.SpikeTrain(pos[sel]/sps.sig_sampling_rate+t_start, t_start = t_start, t_stop = t_stop, color = 'magenta', markersize = 12))

            #~ if self.auto_zoom_x and np.sum(sel)==1:
                #~ self.xsize_changer.set_xsize(0.05)
                #~ self.timerSeeker.seek((pos[sel]/sps.sig_sampling_rate+t_start).simplified.magnitude)

            
            
            
        
        #~ for i in range(sps.trodness):
            #~ viewer = self.viewers[i]
            #~ viewer.clear_all()
            #~ # sigs
            #~ ana = neo.AnalogSignal(self.sigs[i,s], units ='', t_start = t_start,
                                    #~ sampling_rate = sps.sig_sampling_rate)
            #~ viewer.set_analosignals([ana])
            
            #~ viewer.set_spiketrains_on_signals([ spiketrains ])
            #~ viewer.refresh()
            
            

    def on_spike_selection_changed(self):
        # selected spikes are done like a standard spiketrains with magenta color
        self.refresh()
    
    def prev_segment(self):
        self.change_segment(self.num_seg - 1)
        
    def next_segment(self):
        self.change_segment(self.num_seg + 1)

    def change_segment(self, n):
        sps = self.spikesorter
        self.num_seg  =  n
        if self.num_seg<0:
            self.num_seg = len(sps.segs)-1
        if self.num_seg==len(sps.segs):
            self.num_seg = 0
        self.combo.setCurrentIndex(self.num_seg)
        
        
    


class FullBandSignal(SignalAndSpike):
    name = 'Full band signal'
    refresh_on = [ 'full_band_sigs', 'spike_index_array',  'spike_clusters', ]
    sig_name = 'full_band_sigs'
    

class FilteredBandSignal(SignalAndSpike):
    name = 'Filtered band signal'
    refresh_on = [ 'filtered_sigs', 'spike_index_array',  'spike_clusters', ]
    sig_name = 'filtered_sigs'








class SignalStatistics(SpikeSortingWidgetBase):
    name = 'Signal statistics'
    refresh_on = [ 'filtered_sigs', ]
    icon_name = 'plot-waveform.png'
    
    
    def __init__(self,**kargs):
        super(SignalStatistics, self).__init__(**kargs)
        self.canvas = SimpleCanvasAndTool( )
        #~ self.canvas = SimpleCanvas( )
        self.mainLayout.addWidget(self.canvas)
        self.fig = self.canvas.fig
        
        sps = self.spikesorter
        
        self.axs = [ ]
        ax = None
        for j in range(sps.trodness):
            ax = self.fig.add_subplot(sps.trodness,1,j+1, sharex = ax, sharey = ax)
            self.axs.append(ax)

    
    def refresh(self):
        
        sps = self.spikesorter
        for ax in self.axs:
            ax.clear()
        
        if sps.filtered_sigs is None: return
        
        # stats
        min, max = np.inf, -np.inf
        all_mean = np.zeros( ( len(sps.segs), sps.trodness) ,dtype = 'f')
        all_std = np.zeros( ( len(sps.segs), sps.trodness) ,dtype = 'f')
        all_median = np.zeros( ( len(sps.segs), sps.trodness) ,dtype = 'f')
        for i in range(len(sps.segs)):
            for j in range(sps.trodness):
                mi, ma = sps.filtered_sigs[j,i].min() , sps.filtered_sigs[j,i].max()
                if mi < min : min=mi
                if ma > max: max=ma
                all_mean[i,j] = np.mean(sps.filtered_sigs[j,i]) 
                all_std[i,j] =  np.std(sps.filtered_sigs[j,i])
                all_median[i,j] =np.median(sps.filtered_sigs[j,i])
        
        # histo
        nbins = 1000.
        bins = np.arange(min,max, (max-min)/nbins)
        for j in range(sps.trodness):
            ax = self.axs[j]
            ax.axhline( np.mean(all_mean[:,j]) , color = 'r')
            ax.axhline( np.mean(all_median[:,j]) , color = 'g')
            ax.axhline( np.mean(all_mean[:,j]) + np.sqrt(np.mean(all_std[:,j]**2)) , color = 'r' , linestyle = '--')
            ax.axhline( np.mean(all_mean[:,j]) - np.sqrt(np.mean(all_std[:,j]**2)) , color = 'r' , linestyle = '--')
            
            counts = np.zeros( (bins.shape[0]-1), dtype = 'i')
            for i in range(len(sps.segs)):
                count, _ = np.histogram(sps.filtered_sigs[j,i] , bins = bins)
                counts += count
            ax.plot( counts, bins[:-1])



