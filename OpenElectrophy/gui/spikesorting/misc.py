# -*- coding: utf-8 -*-
"""
"""





from .base import *

from mpl_toolkits.mplot3d import Axes3D
from matplotlib.gridspec import GridSpec

from .ndviewer import NDViewer
from ...tools import correlogram


class Summary(SpikeSortingWidgetBase):
    name = 'Summary'
    refresh_on = [  'waveform_features', 'feature_names', ]# TODO
    icon_name = 'TODO.png'
    
    def __init__(self,**kargs):
        super(Summary, self).__init__(**kargs)
        
        sps = self.spikesorter
        
        self.label = QLabel('<b>Block.name:</b> {}   <b>RecordingChannelGroup.name:</b> {}   <b>Trodness:</b>{} ' .format( sps.rcg.block.name, sps.rcg.name,  sps.trodness) )
        self.mainLayout.addWidget( self.label )
        
        g = QGridLayout()
        self.mainLayout.addLayout( g )
        
        #~ self.disp_signals = sps.initial_state =='full_band_signal' or sps.initial_state =='filtered_band_signal'
        self.disp_signals = sps.full_band_sigs is not None 
        if self.disp_signals:
            self.labelSignal = QLabel('AnalogSignal')
            g.addWidget( self.labelSignal, 0,0)
            self.tableSignal = QTableWidget()
            g.addWidget( self.tableSignal , 1,0)

        self.labelSipkeTrain = QLabel('SpikeTrain')
        g.addWidget( self.labelSipkeTrain, 0,1)
        self.tableSpikeTrain = QTableWidget()
        g.addWidget( self.tableSpikeTrain, 1,1 )


    def refresh(self):
        sps = self.spikesorter
        
        if sps.spike_clusters is not None:
            n_neurons = len( sps.cluster_names)
        else:
            n_neurons = 0
        n_segments = len(sps.segs)

        # signal
        if self.disp_signals:
            self.tableSignal.clear()
            self.tableSignal.setRowCount(len(sps.rcs))
            self.tableSignal.setColumnCount(n_segments)
            for i, seg in enumerate(sps.segs):
                item = QTableWidgetItem('Seg {}'.format(i))
                self.tableSignal.setHorizontalHeaderItem( i, item)
            for j,rc  in enumerate(sps.rcs):
                item = QTableWidgetItem('Chanel {}'.format(rc.index) )
                self.tableSignal.setVerticalHeaderItem( j, item)
            for i, seg in enumerate(sps.segs):
                for j,rc  in enumerate(sps.rcs):
                    if sps.filtered_sigs[j,i] is not None:
                        ana = sps.filtered_sigs[j,i]
                    else:
                        ana = sps.full_band_sigs[j,i]
                    item = QTableWidgetItem(QIcon(), 'AnalogSignal\n size:{}\n duration:{}'.format(ana.size, (ana.size/sps.sig_sampling_rate).rescale('s') ))
                    self.tableSignal.setItem(j, i , item )
            self.tableSignal.resizeColumnsToContents()
            self.tableSignal.resizeRowsToContents()


        #table neurons
        self.tableSpikeTrain.clear()
        self.tableSpikeTrain.setRowCount(n_neurons)
        self.tableSpikeTrain.setColumnCount(n_segments)
        for i, seg in enumerate(sps.segs):
            item = QTableWidgetItem('Seg {}'.format(i))
            self.tableSpikeTrain.setHorizontalHeaderItem( i, item)
        for j,c  in enumerate(sps.cluster_names.keys()):
            nb = np.where(sps.spike_clusters==c)[0].size
            item = QTableWidgetItem('Units : {}\n {}\n nb: {}\n'.format(c, sps.cluster_names[c], nb) )
            self.tableSpikeTrain.setVerticalHeaderItem( j, item)        
        
        for i, seg in enumerate(sps.segs):
            for j,c  in enumerate(sps.cluster_names.keys()):
                clusters_in_seg = sps.spike_clusters[sps.seg_spike_slices[i]]
                nb_spikes = np.sum(clusters_in_seg == c)
                pix = QPixmap(10,10 )
                r,g,b = sps.cluster_colors[c]
                pix.fill(QColor( r*255,g*255,b*255  ))
                icon = QIcon(pix)
                item = QTableWidgetItem(icon, 'Nb spikes {}'.format( nb_spikes) )
                self.tableSpikeTrain.setItem(j, i , item )
        self.tableSpikeTrain.resizeColumnsToContents()
        self.tableSpikeTrain.resizeRowsToContents()


class PlotIsi(SpikeSortingWidgetBase):
    name = 'Inter-Spike Interval'
    refresh_on = [  'spike_index_array', 'spike_clusters', ]# TODO
    icon_name = 'plot-isi.png'
    
    plot_dataset = type('Parameters', (DataSet,), {   'bin_width' : FloatItem('bin width (ms)', 2.),
                                                                                                    'limit' : FloatItem('limit (ms)', 50.),
                                                                                                    'plot_type' : ChoiceItem('plot_type', ['bar', 'line']),
                                                                                                })
    
    def __init__(self,**kargs):
        super(PlotIsi, self).__init__(**kargs)
        
        self.combo = QComboBox()
        self.mainLayout.addWidget( self.combo )
        self.combo.currentIndexChanged.connect( self.comboChanged )
        
        self.canvas = SimpleCanvas()
        self.fig = self.canvas.fig
        self.ax = self.fig.add_subplot(1,1,1)
        self.mainLayout.addWidget(self.canvas)
        
    def refresh(self):
        sps = self.spikesorter
        if sps.spike_index_array is None : return
        self.combo.clear()
        self.combo.addItems( ['Neuron {}'.format(c) for c in  sps.cluster_names ])
        

    def comboChanged(self, ind):
        
        sps = self.spikesorter
        if sps.spike_clusters is None: return
        c = sps.spike_clusters[ind]
        self.ax.clear()

        width = self.plot_parameters['bin_width']
        limit = self.plot_parameters['limit']
        
        all_isi = [ ]
        for s, seg in enumerate(sps.segs):
            all_isi.append(np.diff(sps.get_spike_times(s,c, units = 'ms').magnitude))
        isi = np.concatenate(all_isi)
        
        y,x = np.histogram(isi, bins = np.arange(0,limit, width))
        if self.plot_parameters['plot_type'] == 'bar':
            self.ax.bar(x[:-1], y, width =width, color = sps.cluster_colors[c])
        elif self.plot_parameters['plot_type'] == 'line':
            self.ax.plot(x[:-1], y,  color = sps.cluster_colors[c])
        self.ax.set_xlabel('isi (ms)')
        self.ax.set_ylabel('count')
        self.canvas.draw()
        






class PlotCrossCorrelogram(SpikeSortingWidgetBase):
    name = 'Cross-correlogram'
    refresh_on = [  'spike_index_array', 'spike_clusters', ]
    icon_name = 'plot-crosscorrelogram.png'
    
    plot_dataset = type('Parameters', (DataSet,), {   'bin_width' : FloatItem('bin width (ms)', 2.),
                                                                                                    'limit' : FloatItem('limit (ms)', 50.),
                                                                                                    'plot_type' : ChoiceItem('plot_type', ['bar', 'line']),
                                                                                                })
    
    def __init__(self,**kargs):
        super(PlotCrossCorrelogram, self).__init__(**kargs)

        self.canvas = SimpleCanvas()
        self.fig = self.canvas.fig
        self.mainLayout.addWidget(self.canvas)

        self.threadRefresh = None


    def refresh(self):
        if self.threadRefresh is not None:
            self.threadRefresh.wait()
        self.threadRefresh = ThreadRefresh(widgetToRefresh = self)
        self.threadRefresh.start()
        
        
    def refresh_background(self):
        sps = self.spikesorter
        if sps.cluster_names is None : return
        
        bin_width = self.plot_parameters['bin_width']
        limit = self.plot_parameters['limit']
         
        clusters = sps.cluster_names.keys()
        clusters = [ c  for c in clusters if sps.active_cluster[c] ]
        n = len(clusters)
        
        self.canvas.fig.clear()
        self.counts = { }
        for i, c1 in enumerate(clusters):
                for j, c2 in enumerate(clusters):
                    if j<i: continue

                    delta = .05
                    ax = self.canvas.fig.add_axes([delta/4.+i*1./n, delta/4.+j*1./n  ,(1.-delta)/n, (1.-delta)/n])
                    all_count = [ ]
                    for s , seg in enumerate(sps.segs):
                        t1 = sps.get_spike_times(s,c1, units = 'ms').magnitude
                        t2 = sps.get_spike_times(s,c2, units = 'ms').magnitude
                        if t1.size==0 or t2.size==0: continue
                        count, bins = correlogram(t1,t2, bin_width = bin_width, limit = limit , auto = i==j)
                        all_count.append(count[np.newaxis,:])
                    if len(all_count)==0: continue
                    count = np.sum(np.concatenate(all_count, axis= 0 ), axis=0)
                    
                    
                    if i==j:
                        color =  sps.cluster_colors[ c1 ]
                    else:
                        color = 'k'

                    if self.plot_parameters['plot_type'] == 'bar':
                        ax.bar(bins[:-1]+bin_width/2., count , width = bin_width, color = color)
                    elif self.plot_parameters['plot_type'] == 'line':
                        ax.plot(bins[:-1]+bin_width/2., count , color = color)
                    ax.set_xlim(-limit, limit)
                    
                    if i!=j: ax.set_xticks([])
                    if i!=0: ax.set_yticks([])
                
        self.canvas.draw()
    
    def on_spike_selection_changed(self):
        # TODO something less lazy with a cache for counts
        self.refresh()



