#encoding : utf-8 


"""
This modules provide a widget able to display a treeview of a SQL schema

"""

from .qt import *

import numpy as np
import quantities as pq

from .guiutil.icons import icons

from sqlalchemy.sql import select
import sqlalchemy as sa


#~ from operator import itemgetter, attrgetter

import time


class TreeDescription(object):
    def __init__(self,
                            name = 'New',
                            dbinfo = None,
                            table_children = { },
                            columns_to_show = { },
                            table_on_top = 'Block',
                            table_order = { },
                        ):
        object.__init__(self)
        
        
        self.name = name
        self.table_children = table_children
        self.columns_to_show = columns_to_show
        self.table_on_top = table_on_top
        self.table_order = table_order
        
        self.check_and_complete(dbinfo)
    
    def __getstate__(self):
        # for pickle
        d = { }
        for attr in ['name', 'table_children', 'columns_to_show', 'table_on_top', 'table_order']:
            d[attr] = self.__dict__[attr]
        return d
    
    def check_and_complete(self, dbinfo):
        mapped_classes = dbinfo.mapped_classes
        tablename_to_class = dict( [(c.tablename, c) for c in dbinfo.mapped_classes ] )
        #~ tablename_to_class = { }
        #~ for mapped_class in mapped_classes:
            #~ tablename_to_class[mapped_class.tablename] = mapped_class

        for mapped_class in mapped_classes:
            if mapped_class.tablename not in self.columns_to_show :
                columns = [ ]
                for attrname, attrtype in mapped_class.usable_attributes.items() :
                    if attrtype != np.ndarray and attrtype != pq.Quantity :
                        columns += [attrname]
                self.columns_to_show[mapped_class.tablename] = columns
        
        for tablename in tablename_to_class:
            if tablename not in self.table_children:
                self.table_children[tablename] = [ ]
        
        self.table_parents = { }
        for parentname, childrennames in self.table_children.items():
            for childname in childrennames:
                assert childname not in self.table_parents, 'In treeview a child must have only one parent {} {}'.format(childname, parentname) 
                self.table_parents[childname] = parentname
        self.table_parents[self.table_on_top] = None
        
        self.topClass = tablename_to_class[self.table_on_top]
        self.dbinfo = dbinfo
        self.tablename_to_class = tablename_to_class



class TreeItem(object):
    def __init__(self, tablename, id, parent, row):
        self.tablename = tablename
        self.id = id
        self.parent = parent
        self.row = row

        self.children = None
        self.is_root = self.tablename is None and self.id is None
        self.columns_display = { }
    
    def children_count(self, session, treedescription):
        return len(self.get_children(session, treedescription))
    
    def get_child(self, row, session, treedescription):
        return self.get_children(session, treedescription)[row]
    
    def get_children(self, session, treedescription):
        if self.children is None:
            #~ print 'SQL', self.tablename, self.id
            if self.is_root:
                childnames = [ treedescription.table_on_top ]
            else:
                childnames = treedescription.table_children[self.tablename]
            
            self.children = [ ]
            row = 0
            for childname in childnames:
                if childname in  treedescription.table_order:
                    #~ order_by = childname+'.'+treedescription.table_order[childname]
                    order_by = treedescription.table_order[childname]
                else:
                    order_by = None
                if self.is_root:
                    q = select(columns =  [ sa.text('`'+childname+'`.`id`')],
                                    from_obj = [sa.text(childname)],
                                    order_by = order_by,
                                    )
                elif childname in treedescription.tablename_to_class[self.tablename].many_to_many_relationship:
                    #many to many
                    xref = self.tablename+'XREF'+childname
                    if xref not in treedescription.dbinfo.metadata.tables:
                        xref =childname+'XREF'+self.tablename
                    q = select(columns = [ sa.text('`'+childname+'`.`id`')],
                                    whereclause = '`{}`.`id` = `{}`.`{}_id` AND `{}`.`{}_id` = {}'.format(childname, xref,childname.lower(), xref, self.tablename.lower(), self.id),
                                    from_obj = [sa.text(childname), sa.text(xref)],
                                    order_by = order_by,
                                    )
                else:
                    # one to many
                    q = select(columns = [ sa.text('`'+childname+'`.`id`')],
                                    whereclause = '`{}`.`{}_id` = {}'.format(childname, self.tablename.lower(), self.id),
                                    from_obj = [sa.text(childname)],
                                    order_by = order_by,
                                    )
                
                #~ print q
                #~ for id, in session.execute(q):
                for id, in session.bind.execute(q):
                    self.children.append(TreeItem(childname, id, self, row))
                    row +=1
        
        return self.children
        
        def get_parent(self):
            return self.parentitem
        

class MyView(QTreeView):    
    def __init__(self, parent =None) :
        QTreeView.__init__(self,parent)
        self.setIconSize(QSize(22,22))
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)        


class MyModel(QAbstractItemModel):
    """
    Implementation of a treemodel base on OpenElectrophy mapper layer on top of  sqlalchemy
    and mapper.
    """
    def __init__(self, parent =None ,
                        session = None,
                        treedescription = None,):

        QAbstractItemModel.__init__(self,parent)
        self.session= session
        self.td = treedescription
        
        self.rootItem = TreeItem(None, None, None, None)
        
        # nb of columns
        self.maxColumn = 0
        for fieldnames in self.td.columns_to_show.values() :
            if len(fieldnames)>self.maxColumn:
                self.maxColumn = len(fieldnames)+1
        
        
        #~ self.total_time = {'rowCount':0.,'index':0., 'parent' : 0., 'data':0. , 'getinst' : 0., '??' : 0.}
        
        #~ print 'self.maxColumn', self.maxColumn
    
    def columnCount(self , parentIndex):
        #~ print '##columnCount', parentIndex, parentIndex.isValid()
        return self.maxColumn

    def rowCount(self, parentIndex):
        #~ t1 = time.time()
        if not parentIndex.isValid():
            n= self.rootItem.children_count(self.session, self.td)
        else:
            item = parentIndex.internalPointer()
            n= item.children_count(self.session, self.td)
        #~ t2 = time.time()
        #~ self.total_time['rowCount'] +=t2-t1
        #~ print self.total_time
        return n

 #~ def reset(self):
        #~ self.rootNodes = self._getRootNodes()
        #~ QAbstractItemModel.reset(self)
        
        
    def index(self, row, column, parentIndex):
        #~ t1 = time.time()
        if not parentIndex.isValid():
            ind = self.createIndex(row, column, self.rootItem.get_children(self.session, self.td)[row])
        else:
            parentItem = parentIndex.internalPointer()
            ind = self.createIndex(row, column, parentItem.children[row])
        #~ t2 = time.time()
        #~ self.total_time['index'] +=t2-t1
        #~ print self.total_time
        return ind
        
    def parent(self, index):
        #~ t1 = time.time()
        if not index.isValid():
            ind = QModelIndex()
        else:
            item = index.internalPointer()
            if item.parent is None or item.parent.tablename is None:
                ind = QModelIndex()
            else:
                ind = self.createIndex(item.parent.row, 0, item.parent)
        #~ t2 = time.time()
        #~ self.total_time['parent'] +=t2-t1
        #~ print self.total_time
        return ind


    def data(self, index, role):
        if not index.isValid():
            return None
            
        #~ t1 = time.time()
        
        
        item = index.internalPointer()
        class_ = self.td.tablename_to_class[item.tablename]

        
        col = index.column()
        
        #~ t5 = time.time()
        if role ==Qt.DisplayRole :
            fieldnames = self.td.columns_to_show[item.tablename]
            if col > len(fieldnames):
                ret = None
            else:
                if col not in item.columns_display:
                    if  col ==0:
                        #~ return QVariant( '{} : {}'.format( item.tablename, item.id) )
                        item.columns_display[col] =  u'{} : {}'.format( item.tablename, item.id) 
                    else :

                        #~ t3 = time.time()
                        inst = self.session.query(self.td.tablename_to_class[item.tablename]).get(item.id) ##### TROP LENT
                        #~ t4 = time.time()

                        #~ self.total_time['getinst'] +=t4-t3

                        
                        
                        
                            #~ ret = None
                        
                        #~ else:
                            
                        fieldname= fieldnames[col-1]
                        if hasattr(inst, fieldname):
                            value = getattr(inst, fieldname)
                            item.columns_display[col] =  u'{} : {}'.format( fieldname, value)
                        else:
                            item.columns_display[col] =  u''
                    
                ret = item.columns_display[col]
                
                        
                        
                    #~ else:
                        #~ ret= None
                    

        
        #~ elif role == Qt.DecorationRole :
            #~ if col == 0:
                #~ ret =  QIcon(':/'+ item.tablename+'.png')
            #~ else:
                #~ ret = None
        elif role == 'table_and_id':
            ret = item.tablename, item.id
            
        #~ elif role == 'object':
            #~ ret =  inst
            
        #~ elif role == 'table_index' :
            #~ #for drag and drop
            #~ return table+':'+str(id_principal)
        else :
            ret = None

        #~ t6 = time.time()
        #~ self.total_time['??'] +=t6-t5


        #~ t2 = time.time()
        #~ self.total_time['data'] +=t2-t1
        #~ print self.total_time
        return ret



    #~ def hasChildren ( self, parentIndex) :
        #~ if not parentIndex.isValid():
            #~ return True
        #~ return True

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable #| Qt.ItemIsDragEnabled





class QtSqlTreeView(QWidget) :
    def __init__(self  , parent = None ,
                            session = None,
                            treedescription = None,
                            explorer = None,
                            settings = None,
                            context_menu = None,
                            ):
        QWidget.__init__(self, parent)
        
        self.session = session
        self.treedescription = treedescription
        self.explorer = explorer
        
        self.settings = settings
        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)
        
        self.treeview = MyView()
        self.mainLayout.addWidget(self.treeview)
        
        #~ self.model = MyModel( session = self.session,treedescription = self.treedescription,)
        #~ self.treeview.setModel(self.model)
        self.refresh()
        
        self.context_menu = context_menu
        if self.context_menu is not None:
            self.setContextMenuPolicy(Qt.CustomContextMenu)
            self.customContextMenuRequested.connect(self.callContextMenu)
        
    
        
    def refresh(self):
        #~ self.layoutAboutToBeChanged.emit()
        self.model = MyModel( session = self.session,treedescription = self.treedescription,)
        self.treeview.setModel(self.model)
        self.resizeColumWidth()
        
    def resizeColumWidth(self):
        # FIXME: this is a  draft
        # resize column
        for c in range( self.model.columnCount(QModelIndex()) ):
            if c == 0: N=200
            else: N = 150
            if self.treeview.columnWidth(c) <N:
                self.treeview.setColumnWidth(c, N)
    
    
    
    def callContextMenu(self):
        # is selection uniform
        tablenames= [ ]
        ids = [ ]
        for index in self.treeview.selectedIndexes():
            if index.column()==0:
                tablename, id = self.model.data(index , 'table_and_id')
                tablenames.append(tablename)
                ids.append( id )
        homogeneous = np.unique(tablenames).size == 1
        
        
        # create menu
        menu = QMenu()
        actions = { }
        for m in self.context_menu:
            if  m.table is None and \
                  ( (m.mode == 'unique' and len(ids)==1) or\
                    (m.mode == 'homogeneous' and homogeneous) or\
                    (m.mode =='all' ) or \
                    (m.mode =='empty' and len(ids)==0) ):
                act = menu.addAction(QIcon(m.icon), m.name)
                actions[act] = m
            if  m.table is not None and \
                ( (m.mode =='unique' and len(ids)==1) or \
                    (m.mode =='homogeneous' and homogeneous) ) and \
                m.table == tablenames[0] :
                act = menu.addAction(QIcon(m.icon), m.name)
                actions[act] = m
        
        # execute action
        act = menu.exec_(self.cursor().pos())
        if act is None : return
        m = actions[act]()
        kargs = dict( treeview = self,
                      settings = self.settings,
                      treedescription = self.treedescription,
                      session = self.session,
                      explorer = self.explorer,
                      )
        if m.mode == 'unique':
            kargs['id'] = ids[0]
            kargs['tablename'] = tablenames[0]
        elif m.mode == 'homogeneous':
            kargs['ids'] = ids
            kargs['tablename'] = tablenames[0]
        elif m.mode == 'all' :
            kargs['ids'] = ids
            kargs['tablenames'] = tablenames
        #~ print kargs.keys()
        m.execute( **kargs)

    
    #~ def getSelectedObject(self):
        #~ objects = [ ]
        #~ for index in self.treeview.selectedIndexes():
            #~ if index.column()==0:
                #~ objects.append(self.model.data(index , 'object'))
        #~ return objects
    
    #~ def getSelectedTableAndIDs(self):
        #~ tablenames= [ ]
        #~ ids = [ ]
        #~ for index in self.treeview.selectedIndexes():
            #~ if index.column()==0:
                #~ tablename, id = self.model.data(index , 'table_and_id')
                #~ tablenames.append(tablename)
                #~ ids.append( id )
        #~ return tablenames, ids