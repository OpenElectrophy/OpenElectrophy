# -*- coding: utf-8 -*-
"""
Dialog to design or modify a schema:
    * add table
    * add relationship
    * add columns
"""


from .qt import *

import numpy as np
import quantities as pq
import datetime

from collections import OrderedDict

from ..core.sqlmapper import (create_column_if_not_exists,
                                        create_one_to_many_relationship_if_not_exists,
                                        create_many_to_many_relationship_if_not_exists,
                                        create_table_from_class)
from ..core.base import OEBase
from ..core.sqlmapper import open_db



from guiutil.myguidata import *

from sqlalchemy import Table, Column, Integer, String, Float, ForeignKey, Binary, Text, LargeBinary, DateTime
import sqlalchemy

#~ import migrate.changeset
#~ from sqlalchemy.orm import sessionmaker , create_session


translate1 = {
                    str : 'Text',
                    float : 'Float',
                    int : 'Integer',
                    np.ndarray : 'numpy.ndarray',
                    datetime.datetime : 'DateTime',
                    pq.Quantity : 'quantities.Quantity'
                    }

translate2 = { }
for k,v in translate1.iteritems():
    translate2[v] = k



class SchemaDesign(QDialog) :
    schema_changed = pyqtSignal()
    
    def __init__(self  , parent = None , dbinfo = None):
        QDialog.__init__(self, parent)
        
        self.dbinfo = dbinfo
        
        self.setWindowTitle(u'schema designer')
        
        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)
        
        h  = QHBoxLayout()
        self.mainLayout.addLayout(h)
        self.comboTable = QComboBox()
        self.comboTable.currentIndexChanged.connect(self.comboTableChanged)
        h.addWidget( self.comboTable , 3)
        but = QPushButton(QIcon(':/list-add.png'), 'Create a new table')
        but.clicked.connect(self.createTable)
        h.addWidget(but)
        self.mainLayout.addSpacing(10)
        
        
        h  = QHBoxLayout()
        self.mainLayout.addLayout(h)
        h.addWidget( QLabel('Fields list') )
        h.addStretch(1)
        but = QPushButton(QIcon(':/list-add.png'), '')
        but.clicked.connect(self.addColumn)
        h.addWidget(but)
        but = QPushButton(QIcon(':/list-remove.png'), '')
        but.clicked.connect(self.removeColumn)
        h.addWidget(but)
        
        self.listFields = QTableWidget(selectionBehavior = QAbstractItemView.SelectRows,
                                                                selectionMode = QAbstractItemView.SingleSelection,
                                                                )
        self.mainLayout.addWidget( self.listFields )
        self.mainLayout.addSpacing(10)
        
        h1 = QHBoxLayout()
        self.mainLayout.addLayout(h1)
        
        self.relationships = OrderedDict()
        self.relationships['many_to_one'] = {'label' : 'Parents (many to one)' }
        self.relationships['one_to_many'] = {'label' : 'Children (one to many)' }
        self.relationships['many_to_many'] = {'label' : 'many to many' }
        
        for name, d in self.relationships.items():
            v = QVBoxLayout()
            h1.addLayout(v)
            h  = QHBoxLayout()
            v.addLayout(h)
            h.addWidget( QLabel(d['label']) )
            h.addStretch(1)
            if name != 'many_to_many':
                but = QPushButton(QIcon(':/list-add.png'), '')
                but.clicked.connect(self.addRelationship)
                h.addWidget(but)
                but.relationship = name
            d['list'] = QListWidget()
            v.addWidget(d['list'] )

        #button
        buttonBox = QDialogButtonBox(QDialogButtonBox.Apply | QDialogButtonBox.Cancel)
        self.mainLayout.addWidget(buttonBox)
        #~ buttonBox.accepted.connect(self.apply_changes)
        buttonBox.buttons()[1].clicked.connect(self.apply_changes)
        buttonBox.rejected.connect(self.reject)
    
        self.deepRefresh(dbinfo = dbinfo)
    
    def deepRefresh(self, dbinfo = None):
        self.dbinfo = dbinfo
        self.init_changes()
        self.allTableNames =  [ cl.tablename for cl in self.dbinfo.mapped_classes ]
        self.comboTable.clear()
        self.comboTable.addItems( self.allTableNames )
        self.comboTable.setCurrentIndex(0)
        
    def init_changes(self):
        self.new_relationship = {'many_to_one' : [ ], 'one_to_many' : [ ], 'many_to_many' : [ ]}
        self.new_fields =OrderedDict()
        self.removed_fields = [ ]

    
    def has_changed(self):
        for rel in self.new_relationship.values():
            if len(rel): return True
        if len(self.new_fields):return True
        if len(self.removed_fields):return True
        return False
    
    def comboTableChanged(self, num):
        if num == -1: return
        if self.has_changed():
            warn = 'some changes occures : do you want to apply them ?'
            mb = QMessageBox.warning(self,u'Apply changes',warn,
                    QMessageBox.Apply ,QMessageBox.Cancel  | QMessageBox.Default  | QMessageBox.Escape,
                    QMessageBox.NoButton)
            if mb == QMessageBox.Apply :
                self.apply_changes()
        self.init_changes()
        self.refresh()
    
    
    
    def refresh(self):
        if self.comboTable.currentIndex() == -1: return
        self.tablename = str(self.comboTable.currentText())
        tablename_to_class = dict( [(c.tablename, c) for c in self.dbinfo.mapped_classes ] )
        self.genclass = tablename_to_class[self.tablename]
        
        cl = self.genclass
        self.listFields.clear()
        self.listFields.setColumnCount(2)
        self.listFields.setHorizontalHeaderLabels(['fieldname', 'fieldtype'])
        self.listFields.setRowCount(len(cl.usable_attributes)+len(self.new_fields))
        r=0
        for fields in [ cl.usable_attributes, self.new_fields ]:
            for fieldname, fieldtype in fields.items():
                item = QTableWidgetItem(fieldname)
                self.listFields.setItem(r, 0 , item)
                if  fieldname in self.removed_fields:
                    item.setIcon(QIcon(':/list-remove.png'))
                if  fieldname in self.new_fields:
                    item.setIcon(QIcon(':/list-add.png'))
                
                if fieldtype in translate1:
                    t = translate1[fieldtype]
                else:
                    t = 'unknown'
                item = QTableWidgetItem(t)
                self.listFields.setItem(r, 1 , item)
                #~ item.setBackground(QBrush(QColor('red')))
                r+=1
        
        for name, d in self.relationships.items():
            d['list'].clear()
            d['list'].addItems(getattr(cl, name+'_relationship'))
            for rel in self.new_relationship[name]:
                item = QListWidgetItem(QIcon(':/list-add.png'), rel)
                d['list'].addItem(item)

    
        
    def addColumn(self):
        class Parameters(DataSet):
            colname = StringItem('name', default = '')
            coltype = ChoiceItem('type', translate2.keys())
        dia = ParamDialog(Parameters)
        if dia.exec_():
            d = dia.to_dict()
            self.new_fields[d['colname']] = translate2[d['coltype']]
            self.refresh()
        
    
    def removeColumn(self):
        if len(self.listFields.selectedItems())==0: return
        item = self.listFields.selectedItems()[0]
        if item.column() != 0: return
        r = item.row()
        attrs = self.genclass.usable_attributes
        if r < len( attrs ):
            self.removed_fields.append( attrs.keys()[r] )
        else:
            self.new_fields.pop( self.new_fields.keys()[len( attrs ) - r] )
        self.refresh( )
    
    
    def addRelationship(self):
        cl = self.genclass
        alltables = [c.tablename for c in self.dbinfo.mapped_classes ]
        if self.tablename is not None:
            alltables.remove( self.tablename )
        menu =  QMenu()
        for table in alltables:
            menu.addAction(table)
        act = menu. exec_(QCursor.pos())
        if act is None: return
        name = str( act.text() )
        
        for rel in self.new_relationship.values():
            if name in rel: return
        if name in cl.one_to_many_relationship: return
        if name in cl.many_to_one_relationship: return
        if name in cl.many_to_many_relationship: return
        self.new_relationship[self.sender().relationship].append(name)
        self.refresh()



    def createTable(self):
        class Parameters(DataSet):
            tablename = StringItem('tablename', default = '')
        dia = ParamDialog(Parameters , title = 'table name')
        if dia.exec_():
            tablename = str(dia.to_dict()['tablename'])
            if tablename in self.dbinfo.metadata.tables:
                return
            #create table
            columns = [ Column('id', Integer, primary_key=True, index = True) ,]
            table =  Table(tablename, self.dbinfo.metadata, *columns  )
            table.create()
            
            self.reopen_database()
    
    def apply_changes(self):
        
        #~ session = self.dbinfo.Session()
        #~ session.begin()
        
        cl = self.genclass
        tablename_to_class = dict( [(c.tablename, c) for c in self.dbinfo.mapped_classes ] )
        tables = self.dbinfo.metadata.tables
        for name, relations in self.new_relationship.items():
            for relation in relations:
                if name =='many_to_one':
                        create_one_to_many_relationship_if_not_exists(parenttable=tables[relation], childtable=tables[cl.tablename])
                        #~ cl.many_to_one_relationship.append(relation)
                        #~ tablename_to_class[relation].one_to_many_relationship.append(cl.tablename)
                elif name =='one_to_many':
                        create_one_to_many_relationship_if_not_exists(parenttable=tables[cl.tablename], childtable=tables[relation])
                        #~ cl.one_to_many_relationship.append(relation)
                        #~ tablename_to_class[relation].many_to_one_relationship.append(cl.tablename)
                elif name =='many_to_many':
                    raise NotImplementedError()
                    # create_many_to_many_relationship_if_not_exists
        
        
        for attrname, attrtype in self.new_fields.items():
            create_column_if_not_exists(tables[self.tablename], attrname,attrtype)
        
        #TODO drop columns
        #~ for attrname in self.removed_fields:
            #~ print attrname, tables[self.tablename], tables[self.tablename].c[attrname]
        
        
        #commit
        #~ sqlalchemy.inspect(pub_obj).session.commit()
        
        #~ session.commit()
        
        self.reopen_database()

    
    def reopen_database(self):
        new_dbinfo = open_db(**self.dbinfo.kargs_reopen)
        new_dbinfo.kargs_reopen = self.dbinfo.kargs_reopen
        self.deepRefresh(dbinfo = new_dbinfo)
        self.schema_changed.emit()




