# -*- coding: utf-8 -*-
"""
Theses widgets dislpay Qt list of spikes and units.
"""





from .base import *

from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D



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
        return 3
        
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
            elif column==1:
                #~ childItem = self.spikesorter.spikeTimes[row]
                childItem = 'TODO'
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
        if role ==Qt.DisplayRole :
            if col == 0:
                return u'{}'.format(row)
            elif col == 1:
                return u'TODO '
            elif col == 2:
                if sps.spike_clusters is None :#or sps.cluster_displayed_subset is None:
                    return u''
                else:
                    c = sps.spike_clusters[row]
                    return'{}'.format(row in sps.cluster_displayed_subset[c])
            else:
                return None
        elif role == Qt.DecorationRole :
            if col == 0:
                return self.icons[sps.spike_clusters[row]]
            else:
                return None
        else :
            return None

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable #| Qt.ItemIsDragEnabled

    
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
        if ind.size>10000:
            # only the first one because QT4 is able to handle with big selections
            if ind.size>0:
                for j in range(2):
                    index = self.treeSpike.model().index(ind[0],j,QModelIndex())
                    ir = QItemSelectionRange( index )
                    itemsSelection.append( ir )
        else:
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


        self.treeNeuron = QTreeWidget()
        self.treeNeuron.setColumnCount(4)
        self.treeNeuron.setHeaderLabels(['Num', 'Nb sikes', 'Name', 'Sorting score' ])
        self.treeNeuron.setMinimumWidth(100)
        self.treeNeuron.setColumnWidth(0,60)
        self.mainLayout.addWidget(self.treeNeuron)
        self.treeNeuron.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeNeuron.customContextMenuRequested.connect(self.contextMenuNeuron)
        self.treeNeuron.setSelectionMode( QAbstractItemView.ExtendedSelection)


    def refresh(self):
        sps = self.spikesorter
        self.treeNeuron.clear()
        self.cluster_list = [ ]
        for c in sps.cluster_names:
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
            
            #~ if c in sps.sortingScores: sortingScore = sps.sortingScores[c]
            #~ else: sortingScore = ''
            
            item = QTreeWidgetItem([str(c) , str(ind.size), name, ''  ] )
            item.setIcon(0,icon)
            self.treeNeuron.addTopLevelItem(item)
            self.cluster_list.append(c)


    def contextMenuNeuron(self, point):
        menu = QMenu()
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
        act = menu.addAction(QIcon(':/TODO.png'), u'Hide/Show on ndviewer and waveform')
        act.triggered.connect(self.hideOrShowClusters)
        
        if len(self.treeNeuron.selectedIndexes()) ==  self.treeNeuron.columnCount():
            # one selected row only
            #~ act = menu.addAction(QIcon(':/Clustering.png'), u'Explode cluster (sub clustering)')
            #~ act.triggered.connect(self.subComputeCluster)
            act = menu.addAction(QIcon(':/TODO.png'), u'Set name of this unit')
            act.triggered.connect(self.setUnitNameAndScore)
        
        menu.exec_(self.cursor().pos())
    
    def deleteSelection(self):
        for index in self.treeNeuron.selectedIndexes():
            if index.column() !=0: continue
            r = index.row()
            self.spikesorter.delete_one_cluster(self.cluster_list[r])
        
        self.spikesorter.check_display_attributes()
        self.refresh()
        self.spike_clusters_changed.emit()
        
    
    def moveToTrash(self):
        sps = self.spikesorter
        for index in self.treeNeuron.selectedIndexes():
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
        for index in self.treeNeuron.selectedIndexes():
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
        for index in self.treeNeuron.selectedIndexes():
            if index.column() !=0: continue
            sps.selected_spikes[sps.spike_clusters == self.cluster_list[index.row()]] = True
        self.spike_selection_changed.emit()

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
        #~ for index in self.treeNeuron.selectedIndexes():
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
    
    def hideOrShowClusters(self):
        sps = self.spikesorter
        for index in self.treeNeuron.selectedIndexes():
            if index.column() !=0: continue
            r = index.row()
            c = self.cluster_list[r]
            if c in sps.cluster_displayed_subset and sps.cluster_displayed_subset[c].size == 0:
                sps.random_display_subset(c)
            else:
                sps.cluster_displayed_subset[c]  = np.array([ ], 'i')
        self.spike_subset_changed.emit()
    
    def setUnitNameAndScore(self):
        sps = self.spikesorter
        for index in self.treeNeuron.selectedIndexes():
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
        d =  ParamDialog(Parameters, title = 'Name')
        d.update(dict(name = name))
        if d.exec_():
            sps.cluster_names[c] = d.to_dict()['name']
            #~ sps.sortingScores[c] = d.get_dict()['sortingScore']
        self.refresh()

