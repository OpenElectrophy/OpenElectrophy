#encoding : utf-8 

"""
This modules provide dialogs for databse edition:
  * edit fields
  * change parent
  * edit recordingchannelgroup
"""

from .qt import *

import quantities as pq
import numpy as np
#~ import datetime
from datetime import datetime

import re

from .guiutil import *



conversion = {str : StringItem,
                            float : FloatItem,
                            int : IntItem,
                            datetime : DateTimeItem,
                            bool : BoolItem,
                            }

class EditFieldsDialog(QDialog):
    def __init__(self  , parent = None ,
                            session = None,
                            instance = None,
                            ):
        QDialog.__init__(self, parent)
        self.session = session
        self.instance = instance
        
        #~ self.setWindowFlags(Qt.Dialog)
        #~ self.setWindowModality(Qt.NonModal)
        title = 'Edit fields for {} : {}'.format(instance.tablename , instance.id)
        self.setWindowTitle(title)
        
        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)
        
        items = { }
        for attrname, type_ in self.instance.usable_attributes.items():
            if type_ == np.ndarray or  type_ ==  pq.Quantity: continue
            val = getattr(instance, attrname)
            if type_ in conversion:
                edititem = conversion[type_]
            else:
                edititem = StringItem
            if attrname in ['info', 'notes', 'description' ]:
                edititem = TextItem
            items[attrname] = edititem(attrname, default = val)
        
        Parameters = type('Parameters',(DataSet,), items)
        self.params = DataSetEditGroupBox(title,Parameters, show_button = False)
        self.mainLayout.addWidget( self.params )

        self.buttonBox = buttonBox = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.mainLayout.addWidget(buttonBox)
        buttonBox.accepted.connect(self.saveAndClose)
        buttonBox.rejected.connect(self.close)
    
    def saveAndClose(self):
        self.params.set()
        for attrname, type_ in self.instance.usable_attributes.items():
            if type_ == np.ndarray or  type_ ==  pq.Quantity: continue
            setattr(self.instance, attrname, getattr(self.params.dataset, attrname))
        self.session.commit()
        self.close()
        self.accept()



class ChangeParentDialog(QDialog):
    def __init__(self  , parent = None ,
                            session = None,
                            ids =[ ],
                            class_ = None,
                            mapped_classes = None,
                            ):
        QDialog.__init__(self, parent)
        self.session = session
        self.ids = ids
        self.class_ = class_
        
        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)
        
        self.tablename_to_class = dict( [(c.tablename, c) for c in mapped_classes ] )
        self.possible_parents =  [self.tablename_to_class[p].__name__ for p in self.class_.many_to_one_relationship]
        
        if len(self.possible_parents):
            class Parameters(DataSet):
                parentnum = ChoiceItem('Wich parent to change',self.possible_parents)
                id = IntItem('id', )
            self.params = DataSetEditGroupBox('Change parent',Parameters, show_button=False)
            self.mainLayout.addWidget( self.params )
        else:
            self.params = None
        
        buttonBox = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.mainLayout.addWidget(buttonBox)
        buttonBox.accepted.connect(self.applyChange)
        buttonBox.rejected.connect(self.close)
    
    def applyChange(self):
        if self.params:
            # verify that parent exists
            self.params.set()
            parentname =self.possible_parents[self.params.dataset.parentnum]
            id_parent = self.params.dataset.id
            parentclass = self.tablename_to_class[parentname]
            parentinstance = self.session.query(parentclass).get(id_parent)
            if parentinstance:
                relationship = getattr(parentinstance, self.class_.tablename.lower()+'s')
                for id in self.ids:
                    instance = self.session.query(self.class_).get(id)
                    relationship.append(instance)
                    
                self.session.commit()
                self.accept()
            else:
                self.close()
        else:
            self.close()




class ManyToManyModel(QAbstractItemModel):
    """
    Implementation of a treemodel base on OpenElectrophy mapper layer on top of  sqlalchemy
    and mapper.
    """
    def __init__(self, parent =None ,
                        class1 = None,
                        class2 = None,
                        list1 = [],
                        list2 = [],
                        columns1 = [],
                        columns2 = [],
                        multicolumn = False,
                        ):
        QAbstractItemModel.__init__(self,parent)
        self.class1 = class1
        self.class2 = class2
        self.list1 = list1
        self.list2 = list2
        self.columns = {class1 : columns1, class2 : columns2 }
        self.multicolumn = multicolumn
        self.dict_index_to_parent_index = { }

    def columnCount(self , parentIndex):
        if self.multicolumn:
            return max([ len(col) for col in self.columns.values() ])+1
        else:
            return 1
    
    def rowCount(self, parentIndex):
        if not parentIndex.isValid():
            return len(self.list1)
        else :
            parentItem = parentIndex.internalPointer()
            if type(parentItem) == self.class1:
                children = getattr(parentItem, self.class2.__name__.lower()+'s')
                return len(children)
            else:
                return 0
        
    def index(self, row, column, parentIndex):
        if not parentIndex.isValid():
            children = self.list1
        else:
            parentItem = parentIndex.internalPointer()
            children = getattr(parentItem, self.class2.__name__.lower()+'s')
        if row >= len(children):
            return QModelIndex()
        childItem = children[row]
        
        index = self.createIndex(row, column, childItem)
        if index not  in self.dict_index_to_parent_index:
            if parentIndex.isValid():
                self.dict_index_to_parent_index[index] = parentIndex
            else:
                self.dict_index_to_parent_index[index] = None
                
        return index

    def parent(self, index):
        if index in self.dict_index_to_parent_index:
            if self.dict_index_to_parent_index[index]:
                return self.dict_index_to_parent_index[index]
            else:
                return QModelIndex()
        else:
            return QModelIndex()
    
    def data(self, index, role):
        if not index.isValid():
            return None
        item = index.internalPointer()
        columns = self.columns[type(item)]
        if self.multicolumn:
            col = index.column()
            if role ==Qt.DisplayRole :
                if  col <len(columns)+1:
                    if col == 0:
                        value = type(item).__name__
                        return QVariant( type(item).__name__ )
                    else:
                        colname= columns[col-1]
                        value = getattr(item, colname)
                        return QVariant( '{} : {}'.format( colname, str(value)) )
            elif role == Qt.DecorationRole :
                if col == 0:
                    return QIcon(':/'+ item.tablename+'.png')
                else:
                    return QVariant()
            else :
                return QVariant()
        else:
            if role ==Qt.DisplayRole :
                t = type(item).__name__+' '
                for colname in columns:
                    value = getattr(item, colname)
                    t += str(value)+' '
                    
                return QVariant( t)
            elif role == Qt.DecorationRole :
                return QIcon(':/'+ item.tablename+'.png')
            

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        if self.parent(index).isValid():
            return Qt.ItemIsEnabled
        else:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled
        
    def supportedDropActions(self):
        return Qt.LinkAction
        
    def dropMimeData(self, data, action, row, column, parentIndex):
        if action!= Qt.LinkAction: return False
        
        if str(data.data('text/plain')).startswith(self.class1.__name__+'.rows'):
            return False
        
        target = parentIndex.internalPointer()
        target_children  = getattr(target, self.class2.__name__.lower()+'s')
        #print 'target', target
        
        r = re.findall('(\d+),',str(data.data('text/plain')))
        idx = [ int(i) for i in r]
        for i in idx:
            source = self.list2[i]
            source_children  = getattr(source, self.class1.__name__.lower()+'s')
            #print 'source', source
            if source not in target_children:
                target_children.append(source)
            if target not in source_children:
                source_children.append(target)
            
        #self.layoutChanged.emit()
        self.refresh()
        

        return True
    
    def mimeData(self, indexes):
        mimedata = QMimeData()
        idx = ''
        for index in indexes:
            if index.column()==0:
                idx +=  str(index.row())+','
        mimedata.setData('text/plain', '{}.rows={}'.format(self.class1.__name__, idx))
        return mimedata
    
    def mimeTypes(self):
        return ['text/plain']

    def refresh(self):
        self.layoutChanged.emit()



class MyQTreeView(QTreeView):
##     item_dropped = pyqtSignal()
    def __init__(self, parent = None):
        QTreeView.__init__(self, parent)
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.DragDrop)
        
##     def	dropEvent(self, event ):
##         QTreeView.dropEvent(self, event )
##         self.item_dropped.emit()

class EditManyToManyWidget(QWidget):
    def __init__(self  , parent = None ,
                        class1 = None, class2 = None,
                        list1 = [], list2 = [],
                        columns1 = [], columns2 = []):
        QWidget.__init__(self, parent)
        self.class1 = class1
        self.class2 = class2
        self.list1 = list1
        self.list2 = list2
        
        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)
        
        g = QGridLayout()
        self.mainLayout.addLayout(g)

        self.model1 = ManyToManyModel(class1 = class1,
                                        class2 = class2,
                                        list1 = list1,
                                        list2 = list2,
                                        columns1 = columns1,
                                        columns2 = columns2,
                                        )
        self.tree1 = MyQTreeView()
        g.addWidget(QLabel(class1.__name__), 0,0)
        g.addWidget(self.tree1, 1,0,)
        self.tree1.setModel(self.model1)

        self.model2 = ManyToManyModel(class1 = class2,
                                        class2 = class1,
                                        list1 = list2,
                                        list2 = list1,
                                        columns1 = columns2,
                                        columns2 = columns1,
                                        )
        self.tree2 = MyQTreeView()
        g.addWidget(QLabel(class2.__name__), 0,1)
        g.addWidget(self.tree2, 1,1,)
        self.tree2.setModel(self.model2)

        #FIXME recursive
        self.model1.layoutChanged.connect(self.refresh)
        self.model2.layoutChanged.connect(self.refresh)
        
        self.createActionAndMenu()
        
        bar = QToolBar()
        g.addWidget(bar, 2,0)
        bar.addAction(self.actionAdd1)
        bar.addAction(self.actionRemove1)

    def refresh(self):
        self.model1.layoutChanged.disconnect(self.refresh)
        self.model1.layoutChanged.emit()
        self.model1.layoutChanged.connect(self.refresh)
        
        self.model2.layoutChanged.disconnect(self.refresh)
        self.model2.layoutChanged.emit()
        self.model2.layoutChanged.connect(self.refresh)

    def createActionAndMenu(self):
        self.actionAdd1 = QAction("Add {}".format(self.class1.__name__), self)
        self.actionAdd1.setIcon(QIcon(':/list-add.png'))
        self.actionAdd1.triggered.connect(self.add1)

        self.actionRemove1 = QAction("Add {}".format(self.class1.__name__), self)
        self.actionRemove1.setIcon(QIcon(':/list-remove.png'))
        self.actionRemove1.triggered.connect(self.remove1)

    def add1(self):
        self.list1.append(self.class1())
        self.refresh()

    def remove1(self):
        if len(self.tree1.selectedIndexes()) == 0: return
        if len(self.list1) == 1:
            msg = 'You need at least one RecordinChannelGroup'
            mb = QMessageBox.warning(self,u'delete',msg, 
                    QMessageBox.Ok ,QMessageBox.NoButton  | QMessageBox.Default  | QMessageBox.Escape,
                    QMessageBox.NoButton)
            return
        index = self.tree1.selectedIndexes()[0]
        item = index.internalPointer()
        self.list1.remove(item)
        self.refresh()


class EditRecordingChannelGroupsDialog(QDialog):
    def __init__(self  , parent = None ,
                            Session = None,
                            block = None,
                            mapped_classes = None,
                            ):
        QDialog.__init__(self, parent)
        self.session = Session()
        self.block = block
        self.mapped_classes = mapped_classes
        
        
        self.tablename_to_class = dict( [(c.tablename, c) for c in mapped_classes ] )

        self.rcgs = []
        self.rcs = []
        for i, rcg in enumerate(self.block.recordingchannelgroups):
            self.rcgs.append(rcg)
            for j,rc in enumerate(rcg.recordingchannels):
                if rc not in self.rcs:
                    self.rcs.append(rc)
        RecordingChannelGroup = self.tablename_to_class['RecordingChannelGroup']
        RecordingChannel = self.tablename_to_class['RecordingChannel']


        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)
        
        self.mainLayout.addWidget(QLabel(u'Drag and drop RCG to RC to create link (or reverse)'))
        
        self.editMany = EditManyToManyWidget(class1 = RecordingChannelGroup,
                                        class2 = RecordingChannel,
                                        list1 = self.rcgs,
                                        list2 = self.rcs,
                                        columns1 = ['name'],
                                        columns2 = ['index', 'name', ],
                                        )
        self.mainLayout.addWidget(self.editMany)
        

        
        
        buttonBox = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.mainLayout.addWidget(buttonBox)
        buttonBox.accepted.connect(self.applyChange)
        buttonBox.rejected.connect(self.noChange)
        

     #~ def createActionAndMenu(self):
        #~ self.actionAddRCG = QAction(self.tr("Add RecordingChannelGroup"), self)
        #~ self.actionAddRCG.setIcon(QIcon(':/list-add.png'))
        #~ self.actionAddRCG.triggered.connect(self.addRCG)

        #~ self.actionRemoveRCG = QAction(self.tr("Remove this RecordingChannelGroup"), self)
        #~ self.actionRemoveRCG.setIcon(QIcon(':/list-remove.png'))
        #~ self.actionRemoveRCG.triggered.connect(self.removeRCG)

    def applyChange(self):
        for rcg in self.rcgs:
            if rcg.id is None:
                self.block.recordingchannelgroups.append(rcg)
        self.session.commit()
        self.accept()

    def noChange(self):
        print 'noChange'
        self.session.rollback()
        self.reject()
