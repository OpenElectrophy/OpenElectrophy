#encoding : utf-8 

"""
This modules provide a widget able to design a treeview that can be displayed
in a qtsqltreeview

"""


import copy

from .qt import *

from .guiutil import *

from .qtsqltreeview import TreeDescription, QtSqlTreeView



import quantities as pq
import numpy as np

from sqlalchemy.sql.expression import asc, desc



class MyQListWidget(QListWidget):
    item_dropped = pyqtSignal()
    def	dropEvent(self, event ):
        QListWidget.dropEvent(self, event )
        self.item_dropped.emit()
        
    


class ViewDesigner(QDialog) :
    """
    Dialog to design the treeview
    """
    def __init__(self  , parent = None ,
                            treedescription = None,
                            dbinfo = None,
                            settings = None,
                            ):
        QDialog.__init__(self, parent)
        
        self.treedescription = copy.deepcopy(treedescription)
        #~ self.treedescription = TreeDescription(treedescription.__dict__)
        #~ self.treedescription = treedescription
        
        
        self.dbinfo = dbinfo
        self.settings = settings
        
        self.setWindowTitle(self.tr('Table view designer'))

        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)
        
        g = QGridLayout()
        self.mainLayout.addLayout(g)
        g.addWidget(QLabel('View name'),0,0)
        self.lineName = QLineEdit('')
        g.addWidget(self.lineName,0,1)
        g.addWidget(QLabel('Possible tables'),1,0)
        self.listPossibleTable = QListWidget()
        g.addWidget(self.listPossibleTable,2,0)
        g.addWidget(QLabel('Tables to display'),1,1)
        self.listDisplayedTable = MyQListWidget()
        g.addWidget(self.listDisplayedTable,2,1)
        
        self.listDisplayedTable.item_dropped.connect(self.onDrop)
        
        #~ but = QPushButton(QIcon(':/configure.png') , 'Field to display for selected table'  )
        #~ g.addWidget(but,3,1)
        #~ self.connect( but , SIGNAL('clicked()') , self.editField )
        
        #~ g.addWidget(QLabel('Top Hierarchy table :'),4,0)
        #~ self.comboTop = QComboBox()
        #~ g.addWidget(self.comboTop,4,1)
        #~ allTableNames =  [ name for name in self.metadata.tables ]
        #~ self.comboTop.addItems( allTableNames )
        
        

        #~ #button
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.mainLayout.addWidget(buttonBox)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        
        
        # drap n drop
        self.listPossibleTable.setDragDropMode(QAbstractItemView.DragOnly)
        self.listDisplayedTable.setDragDropMode(QAbstractItemView.DropOnly)
        
        #Context Menu
        self.listDisplayedTable.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listDisplayedTable.customContextMenuRequested.connect(self.callContextMenu)
        #~ self.customContextMenuRequested.connect(self.callContextMenu)
        #~ self.connect( self.listDisplayedTable,SIGNAL('customContextMenuRequested( const QPoint &)'),self.callContextMenu)
        
        #~ # shorcuts
        #~ DeleteShortcut = QShortcut(QKeySequence(Qt.Key_Delete),self.listDisplayedTable)
        #~ self.connect(DeleteShortcut, SIGNAL("activated()"), self.deleteSelection)
        
        #~ if 'showColumns' in kargs:
            #~ self.showColumns = {}
            #~ self.showColumns.update(kargs['showColumns'])
            #~ self.lineName.setText(kargs['name'])
            #~ if kargs['table_on_top'] in allTableNames:
                #~ self.comboTop.setCurrentIndex( allTableNames.index( kargs['table_on_top']  ) )
            #~ tablesToDisplay = [ ]
            #~ for k,v in kargs['table_children'].iteritems():
                #~ tablesToDisplay += [k]
                #~ tablesToDisplay += v
            #~ tablesToDisplay = numpy.unique(tablesToDisplay).tolist()
            #~ for tableName in tablesToDisplay:
                #~ self.listDisplayedTable.addItem( tableName )
            
        #~ else:
            #~ self.showColumns = { }
        
        self.createContextMenu()
        
        self.refresh()

    def createContextMenu(self):
        #~ self.actionOnTop = QAction(self.tr("This table is on top"), self)
        #~ self.actionOnTop.setIcon( QIcon.fromTheme("go-first") )
        #~ self.actionOnTop.setShortcuts([QKeySequence("Ctrl+T"),  ])
        #~ self.actionOnTop.triggered.connect(self.putSelectedTableOnTop)
        
        self.actionRemoveTable = QAction(self.tr("Remove this table from view"), self)
        self.actionRemoveTable.setIcon(QIcon(':/list-remove.png'))
        self.actionRemoveTable.triggered.connect(self.removeSelectedTable)
        
        self.actionColumnsShows = QAction(self.tr("Edit columns to show"), self)
        self.actionColumnsShows.setIcon(QIcon(':/document-properties.png'))
        self.actionColumnsShows.triggered.connect(self.editColumnsShown)
        
        self.actionOrderBy = QAction(self.tr("Order by"), self)
        #~ (':/oder-by.png')
        self.actionOrderBy.setIcon(QIcon.fromTheme('view-sort-ascending'))
        self.actionOrderBy.triggered.connect(self.editOrderBy)

        self.menu = QMenu()
        #~ self.menu.addAction(self.actionOnTop)
        self.menu.addAction(self.actionRemoveTable)
        self.menu.addAction(self.actionColumnsShows)
        self.menu.addAction(self.actionOrderBy)
        
    
    def refresh(self):
        self.listPossibleTable.clear()
        self.listPossibleTable.addItems( [ genclass.tablename  for genclass in self.dbinfo.mapped_classes ] )
        
        self.lineName.setText(self.treedescription.name)

        tablename_to_class = dict( [(c.tablename, c) for c in self.dbinfo.mapped_classes ] )
        
        classnames =[ self.treedescription.table_on_top ]
        
        for tablename, children in self.treedescription.table_children.items():
            classname =  tablename_to_class[tablename].__name__
            for child in children:
                classname =  tablename_to_class[child].__name__
                if classname not in classnames:
                    classnames.append(classname)
        #~ print self.treedescription.table_children
        #~ print classnames
        self.listDisplayedTable.clear()
        self.listDisplayedTable.addItems(classnames)

        for n in range(self.listDisplayedTable.count()):
            self.listDisplayedTable.item(n).setIcon(QIcon(''))
        icon = QIcon.fromTheme("go-first")
        self.listDisplayedTable.item(0).setIcon(icon)

        
        
    
    def onDrop(self):
        self.getTreeDescription()
        self.refresh()
        
    
    def getTreeDescription(self):
        tablenames = [ str(self.listDisplayedTable.item(n).text()) for n in range(self.listDisplayedTable.count()) ]
        tablename_to_class = dict( [(c.tablename, c) for c in self.dbinfo.mapped_classes ] )
        #~ children = construct_children(tablename_to_class , tablenames, self.treedescription.table_on_top)
        #~ print 'tablenames', tablenames
        
        td = self.treedescription
        td.table_children = { }
        td.table_parents = { }
        for tablename in tablename_to_class:
            td.table_children[tablename] = [ ]
        for tablename in tablenames:
            for parentname in tablename_to_class[tablename].many_to_one_relationship:
                if tablename not in td.table_children[parentname] and parentname in tablenames:
                    td.table_children[parentname].append(tablename)
                    td.table_parents[tablename] = parentname
        for tablename in tablenames:
            for parentname in tablename_to_class[tablename].many_to_many_relationship:
                if tablename not in td.table_children[parentname] and parentname in tablenames and\
                    tablename not in td.table_parents:
                    td.table_children[parentname].append(tablename)
                    td.table_parents[tablename] = parentname
            

        
        
        if td.table_on_top not in tablenames and len(tablenames)>0:
            td.table_on_top = tablenames[0]
        #~ print td.table_parents
        ok = True
        while ok:
            ok = False
            if td.table_on_top in td.table_parents and \
                            td.table_parents[td.table_on_top] in tablenames:
                td.table_on_top = td.table_parents[td.table_on_top]
                ok = True
                break
            else:
                ok = False
        td.check_and_complete(self.dbinfo)
        
        self.treedescription.name = str(self.lineName.text())
        return self.treedescription
    
    def callContextMenu(self, point):
        if len(self.listDisplayedTable.selectedIndexes())>0:
            act = self.menu.exec_(self.cursor().pos())
    
    #~ def putSelectedTableOnTop(self):
        #~ row = self.listDisplayedTable.selectedIndexes()[0].row()
        #~ name =  str(self.listDisplayedTable.item(row).text())
        #~ self.treedescription.table_on_top = name.lower()

        #~ tablenames = [ str(self.listDisplayedTable.item(n).text()).lower() for n in range(self.listDisplayedTable.count()) ]
        #~ tablename_to_class = dict( [(c.tablename, c) for c in self.dbinfo.mapped_classes ] )
        
        #~ self.getTreeDescription()
        #~ self.refresh()

        
        #~ for n in range(self.listDisplayedTable.count()):
            #~ self.listDisplayedTable.item(n).setIcon(QIcon(''))
        #~ icon = QIcon.fromTheme("go-first")
        #~ self.listDisplayedTable.selectedItems()[0].setIcon(icon)
    
    def removeSelectedTable(self):
        row = self.listDisplayedTable.selectedIndexes()[0].row()
        self.listDisplayedTable.takeItem(row)

        self.getTreeDescription()
        self.refresh()

        
    def editColumnsShown(self):
        row = self.listDisplayedTable.selectedIndexes()[0].row()
        tablename =  str(self.listDisplayedTable.item(row).text())
        
        #~ tablename = name.lower()
        
        tablename_to_class = dict( [(c.tablename, c) for c in self.dbinfo.mapped_classes ] )
        d = FieldListdesigner(class_ =tablename_to_class[tablename],
                                    columns_to_show = self.treedescription.columns_to_show[tablename])
        if d.exec_():
            self.treedescription.columns_to_show[tablename] = d.getColumnToShow()
    
    def editOrderBy(self):
        name = str(self.listDisplayedTable.currentItem().text())
        possible_columns = [ 'id' , ]
        tablename_to_class = dict( [(c.tablename, c) for c in self.dbinfo.mapped_classes ] )
        for attrname, attrtype in tablename_to_class[name].usable_attributes.items() :
            if attrtype != np.ndarray and attrtype != pq.Quantity :
                possible_columns += [attrname]
        
        directions = ['asc', 'desc' ]
        class Parameters(DataSet):
            order_by = ChoiceItem('order by',possible_columns)
            direction = ChoiceItem('direction', directions )
        p = Parameters()
        if p.edit():
            self.treedescription.table_order[name.lower()] = {'asc' : asc, 'desc' : desc }[directions[p.direction]]( possible_columns[p.order_by])




class FieldListdesigner(QDialog) :
    """
    Dialog for choosing the field list to dislplay
    """
    def __init__(self  , parent = None ,class_ =None,
                                    columns_to_show = None,
                                    
                                    ):
        QDialog.__init__(self, parent)
        
        self.tablename = class_.tablename
        self.class_ = class_
        self.columns_to_show = list(columns_to_show)

        self.possible_columns = [ ]
        for attrname, attrtype in class_.usable_attributes.items() :
            if attrtype != np.ndarray and attrtype != pq.Quantity :
                self.possible_columns += [attrname]

        
        self.setWindowTitle(self.tr('Choose fields to be dislpayed in the tree'))
        
        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)
        
        g = QGridLayout()
        self.mainLayout.addLayout(g)
        self.listField = QListWidget()
        g.addWidget(self.listField , 1,0)
        
        
        for columns in self.possible_columns :
            it = QListWidgetItem(columns)
            it.setCheckState(columns in self.columns_to_show)
            self.listField.addItem(it)
       
        #button
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.mainLayout.addWidget(buttonBox)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        
        
    def getColumnToShow(self):
        columns_to_show = [ ]
        for i in range( self.listField.count()):
            f = self.listField.item(i)
            if f.checkState() :
                columns_to_show += [str(f.text())]
        return columns_to_show


