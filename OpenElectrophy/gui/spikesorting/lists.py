# -*- coding: utf-8 -*-
"""
Theses widgets dislpay Qt list of spikes and units.
"""





from .base import *

from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D

from ...spikesorting import color_utils
from ...spikesorting.sorting.tools import apply_descending_sort_with_waveform


class ModelSpikeList(QAbstractItemModel):
    """
    Implementation of a treemodel for a long spike list
    """
    def __init__(self, parent =None ,
                        spikesorter = None,
                        ) :
        QAbstractItemModel.__init__(self,parent)
        self.spikesorter = spikesorter
        self.refresh()
        
    def columnCount(self , parentIndex):
        return 4
        
    def rowCount(self, parentIndex):
        sps =self.spikesorter
        if not parentIndex.isValid():
            return sps.nb_spikes
        else :
            return 0
        
    def index(self, row, column, parentIndex):
        if not parentIndex.isValid():
            if column==0:
                childItem = row
            #~ elif column==1:
                #~ pass
                #~ childItem = self.spikesorter.spikeTimes[row]
                #~ childItem = 'TODO'
            #~ return self.createIndex(row, column, childItem)
            return self.createIndex(row, column, None)
        else:
            return QModelIndex()
    
    def parent(self, index):
        return QModelIndex()
        
    def data(self, index, role):
        sps = self.spikesorter
        if not index.isValid():
            return None
        col = index.column()
        row = index.row()
        # get segment and pos in segment
        s = sps.get_seg_from_num(row)
        if role ==Qt.DisplayRole :
            if col == 0:
                return u'{}'.format(row)
            elif col == 1:
                
                return u'{}'.format(s)
            elif col == 2:
                if sps.sig_sampling_rate is not None:
                    sr = sps.sig_sampling_rate.rescale('Hz').magnitude
                else:
                    sr = sps.wf_sampling_rate.rescale('Hz').magnitude
                t_start = sps.seg_t_start[s].magnitude
                spike_indexes = sps.spike_index_array[s]
                sl = sps.seg_spike_slices[s]
                spike_time = spike_indexes[row-sl.start]/sr+t_start                
                #~ return u'TODO '
                return u'{}'.format(spike_time)

            
            elif col == 3:
                if sps.spike_clusters is None :#or sps.cluster_displayed_subset is None:
                    return u''
                else:
                    c = sps.spike_clusters[row]
                    return'{}'.format(row in sps.cluster_displayed_subset[c])
            else:
                return None
        elif role == Qt.DecorationRole :
            if col == 0 and sps.spike_clusters is not None and sps.spike_clusters[row] in self.icons:
                return self.icons[sps.spike_clusters[row]]
            else:
                return None
        else :
            return None

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable #| Qt.ItemIsDragEnabled

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return  ['num', 'segment', 'time', 'Is sampled'][section]
        return
    
    def refresh(self):
        self.icons = { }
        for c in self.spikesorter.cluster_names:
            pix = QPixmap(10,10 )
            r,g,b = self.spikesorter.cluster_colors[c]
            pix.fill(QColor( r*255,g*255,b*255  ))
            self.icons[c] = QIcon(pix)
        
        self.icons[-1] = QIcon(':/user-trash.png')
        
        self.layoutChanged.emit()


class SpikeList(SpikeSortingWidgetBase):
    name = 'Spike list'
    refresh_on = [  'spike_clusters', 'cluster_names']
    icon_name = 'TODO.png'

    def __init__(self,**kargs):
        super(SpikeList, self).__init__(**kargs)
        
        self.mainLayout.addWidget(QLabel('<b>All spikes</b>') )
        self.treeSpike = QTreeView(minimumWidth = 100, 
                                                            uniformRowHeights = True,
                                                            selectionMode= QAbstractItemView.ExtendedSelection,
                                                            selectionBehavior = QTreeView.SelectRows,
                                                            contextMenuPolicy = Qt.CustomContextMenu,
                                                            )
        self.treeSpike.setColumnWidth(0,80)
        self.mainLayout.addWidget(self.treeSpike)
        self.treeSpike.customContextMenuRequested.connect(self.contextMenuSpike)
        
        self.modelSpike = ModelSpikeList( spikesorter = self.spikesorter)
        self.treeSpike.setModel(self.modelSpike)
        self.treeSpike.selectionModel().selectionChanged.connect(self.newSelectionInSpikeTree)

        for i in range(self.modelSpike.columnCount(None)):
            self.treeSpike.resizeColumnToContents(i)


    def refresh(self):
        self.modelSpike.refresh()
    
    def newSelectionInSpikeTree(self):
        sps = self.spikesorter
        sps.selected_spikes[:] =False
        for index in self.treeSpike.selectedIndexes():
            if index.column() == 0: 
                sps.selected_spikes[index.row()] =True
        self.spike_selection_changed.emit()

    def on_spike_selection_changed(self):
        # TO avoid SIGNAL larsen 
        self.treeSpike.selectionModel().selectionChanged.disconnect(self.newSelectionInSpikeTree)
        
        # change selection
        self.treeSpike.selectionModel().clearSelection()
        flags = QItemSelectionModel.Select #| QItemSelectionModel.Rows
        itemsSelection = QItemSelection()
        ind, = np.where(self.spikesorter.selected_spikes)
        #~ if ind.size>1000:
            #~ # only the first one because QT4 is able to handle with big selections
            #~ if ind.size>0:
                #~ for j in range(2):
                    #~ index = self.treeSpike.model().index(ind[0],j,QModelIndex())
                    #~ ir = QItemSelectionRange( index )
                    #~ itemsSelection.append( ir )
        #~ else:
            #~ for i in ind:
                #~ for j in range(2):
                    #~ index = self.treeSpike.model().index(i,j,QModelIndex())
                    #~ ir = QItemSelectionRange( index )
                    #~ itemsSelection.append( ir )
        if ind.size>100:
            ind = ind[:10]
        for i in ind:
            for j in range(2):
                index = self.treeSpike.model().index(i,j,QModelIndex())
                ir = QItemSelectionRange( index )
                itemsSelection.append( ir )
        self.treeSpike.selectionModel().select( itemsSelection , flags)

        # set selection visible
        if len(ind)>=1:
            index = self.treeSpike.model().index(ind[0],0,QModelIndex())
            self.treeSpike.scrollTo(index)

        self.treeSpike.selectionModel().selectionChanged.connect(self.newSelectionInSpikeTree)

    def contextMenuSpike(self, point):
        #~ pass
        menu = QMenu()
        act = menu.addAction(QIcon(':/user-trash.png'), self.tr('Move selection to trash'))
        act.triggered.connect(self.moveSpikeToTrash)
        act = menu.addAction(QIcon(':/merge.png'), self.tr('Group selection in one unit'))
        act.triggered.connect(self.createNewClusterWithSpikes)
        menu.exec_(self.cursor().pos())
    
    def getSelection(self):
        l = [ ]
        for index in self.treeSpike.selectedIndexes():
            if index.column() !=0: continue
            l.append(index.row())
        ind = np.array(l)
        return ind
    
    def moveSpikeToTrash(self):
        ind = self.getSelection()
        self.spikesorter.spike_clusters[ ind ]= -1
        self.spikesorter.check_display_attributes()
        self.refresh()
        self.spike_clusters_changed.emit()

    def createNewClusterWithSpikes(self):
        ind = self.getSelection()
        self.spikesorter.spike_clusters[ ind ]= max(self.spikesorter.cluster_names.keys())+1
        self.spikesorter.check_display_attributes()
        self.refresh()
        self.spike_clusters_changed.emit()




class UnitList(SpikeSortingWidgetBase):
    name = 'Unit list'
    refresh_on = [  'spike_clusters', 'cluster_names']
    icon_name = 'TODO.png'

    def __init__(self,**kargs):
        super(UnitList, self).__init__(**kargs)


        self.tableNeuron = QTableWidget()
        self.mainLayout.addWidget(self.tableNeuron)
        self.tableNeuron.itemChanged.connect(self.item_changed)

    def refresh(self):
        self.tableNeuron.itemChanged.disconnect(self.item_changed)
        sps = self.spikesorter
        self.tableNeuron.clear()
        self.tableNeuron.setColumnCount(5)
        self.tableNeuron.setHorizontalHeaderLabels(['Num', 'Nb sikes','Show/Hide', 'Name', 'Sorting score' ])
        self.tableNeuron.setMinimumWidth(100)
        self.tableNeuron.setColumnWidth(0,60)
        self.tableNeuron.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableNeuron.customContextMenuRequested.connect(self.contextMenuNeuron)
        self.tableNeuron.setSelectionMode( QAbstractItemView.ExtendedSelection)
        self.tableNeuron.setSelectionBehavior( QAbstractItemView.SelectRows)
        
        self.tableNeuron.setRowCount(len(sps.cluster_names))
        
        self.cluster_list = [ ]
        for i, c in enumerate(sps.cluster_names):
            ind, = np.where(c==sps.spike_clusters)
            if c==-1:
                icon = QIcon(':/user-trash.png')
            else:
                pix = QPixmap(10,10 )
                r,g,b = sps.cluster_colors[c]
                pix.fill(QColor( r*255,g*255,b*255  ))
                icon = QIcon(pix)
            if c in sps.cluster_names: name = sps.cluster_names[c]
            else: name = u''


            item = QTableWidgetItem(str(c))
            #~ item.setFlags(Qt.ItemIsUserCheckable|Qt.ItemIsEnabled|Qt.ItemIsSelectable)
            item.setFlags(Qt.ItemIsEnabled|Qt.ItemIsSelectable)
            #~ item.setCheckState({ False: Qt.Unchecked, True : Qt.Checked}[sel])
            #~ item.setBackground(colors[sel])
            self.tableNeuron.setItem(i,0, item)
            item.setIcon(icon)

            item = QTableWidgetItem( str(ind.size))
            item.setFlags(Qt.ItemIsEnabled|Qt.ItemIsSelectable)
            self.tableNeuron.setItem(i,1, item)


            item = QTableWidgetItem( str(sps.active_cluster[c]))
            item.setFlags(Qt.ItemIsEnabled|Qt.ItemIsSelectable|Qt.ItemIsUserCheckable)
            item.setCheckState({ False: Qt.Unchecked, True : Qt.Checked}[sps.active_cluster[c]])
            self.tableNeuron.setItem(i,2, item)

            item = QTableWidgetItem( name)
            item.setFlags(Qt.ItemIsEnabled|Qt.ItemIsSelectable)
            self.tableNeuron.setItem(i,3, item)
            
            
            
            
            
            #~ if c in sps.sortingScores: sortingScore = sps.sortingScores[c]
            #~ else: sortingScore = ''
            
            #~ item = QTreeWidgetItem([str(c) ,  str(ind.size), str(sps.active_cluster[c]), name, ''  ] )
            #~ item.setFlags(Qt.ItemIsSelectable |
                                        #~ Qt.ItemIsEnabled)            
            #~ item.setIcon(0,icon)
            #~ self.tableNeuron.addTopLevelItem(item)
            
            
            self.cluster_list.append(c)
        self.tableNeuron.itemChanged.connect(self.item_changed)

    def item_changed(self, item):
        if item.column() != 2: return
        sel = {Qt.Unchecked : False, Qt.Checked : True}[item.checkState()]
        c = self.cluster_list[item.row()]
        sps = self.spikesorter
        sps.active_cluster[c] = sel
        self.clusters_activation_changed.emit()

    def contextMenuNeuron(self, point):
        n = len(self.tableNeuron.selectedIndexes())/self.tableNeuron.columnCount ()
        self.menu = menu = QMenu()
        #~ print 'n', n
        if n>=0: 
            act = menu.addAction(QIcon(':/applications-graphics.png'), u'Recolorize all cluster')
            act.triggered.connect(self.recolorizeCluster)
            act = menu.addAction(QIcon(':/view-filter.png'), u'Sort by ascending waveform power')
            act.triggered.connect(self.sortCluster)
            act = menu.addAction(QIcon(':/TODO.png'), u'Show all')
            act.triggered.connect(self.showAll)
            act = menu.addAction(QIcon(':/TODO.png'), u'Hide all')
            act.triggered.connect(self.hideAll)
            
        if n>=1:
            act = menu.addAction(QIcon(':/window-close.png'),u'Delete selection forever')
            act.triggered.connect(self.deleteSelection)
            act = menu.addAction(QIcon(':/user-trash.png'), u'Move selection to trash')
            act.triggered.connect(self.moveToTrash)
            act = menu.addAction(QIcon(':/merge.png'), u'Group selection in one unit')
            act.triggered.connect(self.groupSelection)
            act = menu.addAction(QIcon(':/color-picker.png'), u'Select these spikes')
            act.triggered.connect(self.selectSpikeFromCluster)
            act = menu.addAction(QIcon(':/go-jump.png'), u'Regroup small units')
            act.triggered.connect(self.regroupSmallUnits)
        
        #~ act = menu.addAction(QIcon(':/TODO.png'), u'Hide/Show on ndviewer and waveform')
        #~ act.triggered.connect(self.hideOrShowClusters)
        
        if n==1:
            # one selected row only
            #~ act = menu.addAction(QIcon(':/Clustering.png'), u'Explode cluster (sub clustering)')
            #~ act.triggered.connect(self.subComputeCluster)
            act = menu.addAction(QIcon(':/TODO.png'), u'Set name/color/score of this unit')
            act.triggered.connect(self.setUnitNameColorScore)
        
        #~ if menu.exec_(self.cursor().pos()):
        menu.popup(self.cursor().pos())
            #~ pass
            #~ print 'yep'
        
    
    def deleteSelection(self):
        for index in self.tableNeuron.selectedIndexes():
            if index.column() !=0: continue
            r = index.row()
            self.spikesorter.delete_one_cluster(self.cluster_list[r])
        
        self.spikesorter.check_display_attributes()
        self.refresh()
        self.spike_clusters_changed.emit()
        
    
    def moveToTrash(self):
        sps = self.spikesorter
        for index in self.tableNeuron.selectedIndexes():
            if index.column() !=0: continue
            c = self.cluster_list[index.row()]
            sps.spike_clusters[sps.spike_clusters == c] = -1
            sps.cluster_names.pop(c)
        self.spikesorter.check_display_attributes()
        self.refresh()
        self.spike_clusters_changed.emit()
        
    def groupSelection(self):
        sps = self.spikesorter
        n = max(sps.cluster_names) +1
        for index in self.tableNeuron.selectedIndexes():
            if index.column() !=0: continue
            c = self.cluster_list[index.row()]
            sps.spike_clusters[ sps.spike_clusters == c ]= n
            sps.cluster_names.pop(c)
        self.spikesorter.check_display_attributes()
        self.refresh()
        self.spike_clusters_changed.emit()
    
    def selectSpikeFromCluster(self):
        sps =  self.spikesorter
        sps.selected_spikes[:] = False
        for index in self.tableNeuron.selectedIndexes():
            if index.column() !=0: continue
            #~ print sps.selected_spikes.shape
            #~ print sps.spike_clusters.shape
            sps.selected_spikes[sps.spike_clusters == self.cluster_list[index.row()]] = True
        self.spike_selection_changed.emit()
        #~ print 'yep'

    #TODO
    #~ def subComputeCluster(self):
        #~ dia = QDialog(self)
        #~ v = QVBoxLayout()
        #~ dia.setLayout(v)
        
        #~ from ..computing.spikesorting.clustering import list_method
        
        #~ wMeth = WidgetMultiMethodsParam(  list_method = list_method,
                                                            #~ method_name = '<b>Choose method for clustering</b>:',
                                                            #~ globalApplicationDict = self.globalApplicationDict,
                                                            #~ keyformemory = 'spikesorting',
                                                            #~ )
        #~ v.addWidget(wMeth)
        #~ buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        #~ v.addWidget(buttonBox)
        #~ self.connect( buttonBox , SIGNAL('accepted()') , dia, SLOT('accept()') )
        #~ self.connect( buttonBox , SIGNAL('rejected()') , dia, SLOT('close()') )
        #~ if not dia.exec_(): return
        
        #~ sps = self.spikesorter
        #~ for index in self.tableNeuron.selectedIndexes():
            #~ if index.column() != 0: continue
            #~ r = index.row()
            #~ sps.subComputeCluster( self.cluster_list[r], wMeth.get_method(), **wMeth.get_dict())
        
        #~ sps.check_display_attributes()
        #~ self.refresh()
        #~ self.spike_clusters_changed.emit()
    
    def regroupSmallUnits(self):
        class Parameters(DataSet):
            size = IntItem('Regroup unit when size less than', default = 10)
        
        params = [  [ 'size' , { 'value' : 10 , 'label' : 'Regroup unit when size less than' }  ] , ]
        d =  ParamDialog(Parameters, title = 'Regroup small units')
        if d.exec_():
            self.spikesorter.regroup_small_cluster( **d.to_dict() )
        
        self.spikesorter.check_display_attributes()
        self.refresh()
        self.spike_clusters_changed.emit()
    
    #~ def hideOrShowClusters(self):
        #~ sps = self.spikesorter
        #~ for index in self.tableNeuron.selectedIndexes():
            #~ if index.column() !=0: continue
            #~ r = index.row()
            #~ c = self.cluster_list[r]
            #~ if c in sps.cluster_displayed_subset and sps.cluster_displayed_subset[c].size == 0:
                #~ sps.random_display_subset(c)
            #~ else:
                #~ sps.cluster_displayed_subset[c]  = np.array([ ], 'i')
        #~ self.spike_subset_changed.emit()
    
    def setUnitNameColorScore(self):
        sps = self.spikesorter
        for index in self.tableNeuron.selectedIndexes():
            if index.column() !=0: continue
            r = index.row()
            c = self.cluster_list[r]
        
        if c in sps.cluster_names: name = sps.cluster_names[c]
        else: name = u''
        #~ if c in sps.sortingScores: sortingScore = sps.sortingScores[c]
        #~ else: sortingScore = ''
        
        class Parameters(DataSet):
            name = StringItem('Name of unit {}'.format(c), default ='')
            #~ sorting_score = FloatItem('Score of unit {}'.format(c), default =sorting_score)
            color = ColorItem('Color of unit {}'.format(c), default= color_utils.mpl_to_html( sps.cluster_colors[c] ))
        d =  ParamDialog(Parameters, title = 'Name')
        d.update(dict(name = name))
        if d.exec_():
            sps.cluster_names[c] = d.to_dict()['name']
            #~ sps.sortingScores[c] = d.get_dict()['sortingScore']
            color = d.to_dict()['color']
            sps.cluster_colors[c] = color_utils.html_to_mplRGB(color)
            self.refresh()
            self.clusters_color_changed.emit()
            
    
    def recolorizeCluster(self):
        self.spikesorter.refresh_colors(reset = True)
        self.refresh()
        self.clusters_color_changed.emit()
    
    def sortCluster(self):
        apply_descending_sort_with_waveform(self.spikesorter)
        self.spikesorter.refresh_colors(reset = True)
        self.refresh()
        self.spike_clusters_changed.emit()
    
    def showHideAll(self, state):
        sps = self.spikesorter
        for c in sps.cluster_names:
            sps.active_cluster[c] = state
        self.refresh()
        self.clusters_activation_changed.emit()
        
    
    def showAll(self):
        self.showHideAll(True)
    
    def hideAll(self):
        self.showHideAll(False)


