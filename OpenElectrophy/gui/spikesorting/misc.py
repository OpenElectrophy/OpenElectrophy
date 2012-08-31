# -*- coding: utf-8 -*-
"""
"""





from .base import *

from mpl_toolkits.mplot3d import Axes3D
from matplotlib.gridspec import GridSpec

from .ndviewer import NDViewer


class Summary(SpikeSortingWidgetBase):
    name = 'Summary'
    refresh_on = [  'waveform_features', 'feature_names', ]# TODO
    icon_name = 'TODO.png'
    
    def __init__(self,**kargs):
        super(Summary, self).__init__(**kargs)
        
        sps = self.spikesorter
        
        self.label = QLabel('<b>Block.name:</b> {}   <b>RecordingChannelGroup.name:</b> {}   <b>Trodness:</b>{}   <b>Initial state:</b> {}' .format( sps.rcg.block.name, sps.rcg.name,  sps.trodness, sps.initial_state) )
        self.mainLayout.addWidget( self.label )
        
        g = QGridLayout()
        self.mainLayout.addLayout( g )
        
        self.disp_signals = sps.initial_state =='full_band_signal' or sps.initial_state =='filtered_band_signal'
        if self.disp_signals:
            self.labelSignal = QLabel('AnalogSignal')
            g.addWidget( self.labelSignal, 0,0)
            self.tableSignal = QTableWidget()
            g.addWidget( self.tableSignal , 1,0)

        self.labelSipkeTrain = QLabel('SpikeTrain')
        g.addWidget( self.labelSipkeTrain, 0,1)
        self.tableSpikeTrain = QTableWidget()
        g.addWidget( self.tableSpikeTrain, 1,1 )


    def refresh(self, step = None):
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
                item = QTableWidgetItem('Seg {} {}'.format(i, seg.name))
                self.tableSignal.setHorizontalHeaderItem( i, item)
            for j,rc  in enumerate(sps.rcs):
                item = QTableWidgetItem('Chanel {}'.format(rc.index) )
                self.tableSignal.setVerticalHeaderItem( j, item)
            for i, seg in enumerate(sps.segs):
                for j,rc  in enumerate(sps.rcs):
                    if self.spikesorter.initial_state == 'full_band_signal':
                        ana = sps.full_band_sigs[j,i]
                    elif self.spikesorter.initial_state == 'filtered_signal':
                        ana = sps.filtered_sigs[j,i]
                        print (ana.size/sps.sig_sampling_rate).rescale('s')
                    item = QTableWidgetItem(QIcon(), 'AnalogSignal\n size:{}\n duration:{}'.format(ana.size, (ana.size/sps.sig_sampling_rate).rescale('s') ))
                    self.tableSignal.setItem(j, i , item )
        self.tableSignal.resizeColumnsToContents()
        self.tableSignal.resizeRowsToContents()


        #table neurons
        self.tableSpikeTrain.clear()
        self.tableSpikeTrain.setRowCount(n_neurons)
        self.tableSpikeTrain.setColumnCount(n_segments)
        for i, seg in enumerate(sps.segs):
            item = QTableWidgetItem('Seg {} {}'.format(i, seg.name))
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
