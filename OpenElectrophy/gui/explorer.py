# -*- coding: utf-8 -*-


"""
This modules provide a explorer for managing treeviews
"""

from .qt import *

from .qtsqltreeview import TreeDescription, QtSqlTreeView
from .contextmenu import context_menu
from guiutil.icons import icons


from .viewdesigner import ViewDesigner
from .schemadesign import SchemaDesign
from .importdata import ImportData



def get_standart_treeview(dbinfo):
    td1 = TreeDescription(
                                        name = 'BySegment',
                                        dbinfo = dbinfo,
                                        table_children = { 'Block' : ['Segment' ],
                                                                    'Segment' : [ 'AnalogSignal', 'EventArray' , 'EpochArray', 'SpikeTrain'],
                                                                    },
                                        table_on_top = 'Block',
                                        )
    

    td2 = TreeDescription(
                                        name = 'ByRecordingChannelGroup',
                                        dbinfo = dbinfo,
                                        table_children = { 'Block' : ['RecordingChannelGroup' ],
                                                                    'RecordingChannelGroup' : [ 'RecordingChannel', 'Unit'],
                                                                    'RecordingChannel' : [ 'AnalogSignal', ],
                                                                    'Unit' : ['SpikeTrain'],
                                                                    },
                                        table_on_top = 'Block',
                                        )

    td3 = TreeDescription(
                                        name = 'ByUnits',
                                        dbinfo = dbinfo,
                                        table_children = { 'Block' : ['RecordingChannelGroup' ],
                                                                    'RecordingChannelGroup' : ['Unit' ],
                                                                    'Unit' : [ 'SpikeTrain', ],
                                                                    },
                                        table_on_top = 'Block',
                                        )
    
    
    
    l = [td1, td2, td3]
    for td in l:
        td.columns_to_show = {  'Block' : ['index', 'name', 'file_origin',],
                                'Segment' : ['index', 'name',],
                                'Unit' : ['name', ],
                                'RecordingChannelGroup' : [ 'name',],
                                'RecordingChannel' : ['index', 'name',],
                                'AnalogSignal' : [ 'name',],
                                'SpikeTrain' : [ 'name',],
                            }
        td.check_and_complete(dbinfo)
                            
    
    return l

    
    
    



class MainExplorer(QWidget) :
    """
    Widget to design the treeview.
    """
    def __init__(self  , parent = None ,
                            dbinfo = None,
                            settings = None,
                            name = None,
                            context_menu = context_menu,
                            ):
        QWidget.__init__(self, parent)
        
        self.dbinfo = dbinfo
        self.name = name
        self.context_menu = context_menu
        
        
        self.setWindowTitle(self.tr('Database explorer'))
        
        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)
        
        self.listTreeDescription = get_standart_treeview(dbinfo)

        self.settings = settings
        if self.settings is not None and self.name is not None:
            self.listTreeDescription = self.settings.getValueOrDefault('/listTreeDescription'+self.name, self.listTreeDescription)
            for td in self.listTreeDescription:
                td.check_and_complete(self.dbinfo)
        
        self.tabViews = QTabWidget()
        self.buttonMenu = QPushButton(QIcon(':/configure.png'), '')
        self.buttonMenu.clicked.connect( self.showConfigureMenu )
        
        self.tabViews.setCornerWidget(self.buttonMenu)
        self.mainLayout.addWidget(self.tabViews)
        
        
        self.tabViews.setTabsClosable(True)
        self.tabViews.tabCloseRequested.connect(self.closeOneTab)
        
        
        
        self.createAction()
        self.createConfigureMenu()
        
        self.deepRefresh()

    def createAction(self):
        self.actionImport = QAction(u'&Import data in this db', self,
                                                                icon =QIcon(':/svn-update.png'))
        self.actionImport.triggered.connect(self.openImportData)
        self.addAction(self.actionImport)
        
        self.actionRefresh = QAction(self.tr("&Refresh view"), self,
                                                                icon = QIcon(':/view-refresh.png'),
                                                                shortcut = QKeySequence("F5"),
                                                                )
        self.actionRefresh.triggered.connect(self.refresh)
        self.addAction(self.actionRefresh)
        
        self.actionAddTab = QAction(self.tr("&Add a new view"), self,
                                                            icon = QIcon(':/list-add.png'),
                                                            shortcut = QKeySequence("Ctrl+T"))
        self.actionAddTab.triggered.connect(self.addOneTab)
        self.addAction(self.actionAddTab)
        
        self.actionDelTab = QAction(self.tr("&Remove this view"), self,
                                                            icon = QIcon(':/list-remove.png'),
                                                            shortcut = QKeySequence("Ctrl+W"))
        self.actionDelTab.triggered.connect(self.closeCurrentTab)
        self.addAction(self.actionDelTab)
        
        self.actionEditTab = QAction(self.tr("&Edit this view"), self,
                                                            icon = QIcon(':/document-properties.png'))
        self.actionEditTab.triggered.connect(self.editCurrentTab)
        self.addAction(self.actionEditTab)
        
        
        if hasattr(self.dbinfo, 'kargs_reopen'):
            self.actionSchemaDesign = QAction(self.tr("Modify schema (add columns and tables)"), self,
                                                                icon = QIcon(':/vcs_diff.png'))
            self.actionSchemaDesign.triggered.connect(self.openSchemaDesign)
            self.addAction(self.actionSchemaDesign)
        
        
        
    def createConfigureMenu(self):
        self.menuConfigure = QMenu()
        self.menuConfigure.addAction(self.actionRefresh)
        self.menuConfigure.addSeparator()
        self.menuConfigure.addAction(self.actionImport)
        self.menuConfigure.addSeparator()
        self.menuConfigure.addAction(self.actionAddTab)
        self.menuConfigure.addAction(self.actionDelTab)
        self.menuConfigure.addAction(self.actionEditTab)
        self.menuConfigure.addSeparator()
        if hasattr(self.dbinfo, 'kargs_reopen'):
            self.menuConfigure.addAction(self.actionSchemaDesign)
        
        
    
    def deepRefresh(self, dbinfo = None):
        """
        To be call in case on modification on schema.
        """
        if dbinfo is not None: 
            self.dbinfo = dbinfo
        for i in range(len(self.tabViews)):
            self.tabViews.removeTab(0)
        self.session = self.dbinfo.Session()
        for td in self.listTreeDescription:
            sqltreeview = QtSqlTreeView(session = self.session, treedescription = td, 
                            settings = self.settings, context_menu = self.context_menu,
                            explorer = self)
            self.tabViews.addTab(sqltreeview , td.name)
        
    def refresh(self):
        self.dbinfo.Session.expire_all()
        if self.dbinfo.cache is not None:
            self.dbinfo.cache.clear()
        #~ self.session = self.dbinfo.Session()
        for i in range(len(self.listTreeDescription)):
            sqltreeview = self.tabViews.widget(i)
            #~ sqltreeview.session = self.session
            sqltreeview.refresh()

    def closeCurrentTab(self):
        self.closeOneTab(self.tabViews.currentIndex())
    
    def closeOneTab(self, num):
        if len(self.listTreeDescription) ==1:
            return
        self.tabViews.removeTab(num)
        self.listTreeDescription.pop(num)
        self.writeSettings()
        
    def addOneTab(self):
        self.editCurrentTab(new = True)
        
    def editCurrentTab(self, new = False):
        if new:
            td = TreeDescription(dbinfo = self.dbinfo)
        else:
            num = self.tabViews.currentIndex()
            td = self.listTreeDescription[num]
        w = ViewDesigner(dbinfo = self.dbinfo, treedescription = td, settings = self.settings)
        if w.exec_() : 
            td = w.getTreeDescription()
            if new:
                sqltreeview = QtSqlTreeView(session = self.session, treedescription = td, 
                                settings = self.settings, context_menu = self.context_menu,
                                explorer = self)
                self.tabViews.addTab(sqltreeview , td.name)
                self.listTreeDescription.append(td)
            else:
                self.listTreeDescription[num] = td
                sqltreeview = self.tabViews.currentWidget()
                sqltreeview.treedescription = td
                sqltreeview.refresh()
        self.writeSettings()

    def writeSettings(self):
        if self.settings is not None :
            self.settings[ '/listTreeDescription'+self.name] = self.listTreeDescription
    
    def showConfigureMenu(self):
        self.menuConfigure. exec_(QCursor.pos())
        
    def getCurrentSqlTreeView(self):
        return  self.tabViews.currentWidget()
    
    def openSchemaDesign(self):
        d = SchemaDesign(dbinfo = self.dbinfo)
        d.schema_changed.connect(self.schemaDesignRefresh)
        d.exec_()
    
    def schemaDesignRefresh(self):
        # open the data again to remap everything
        dia = self.sender()
        self.deepRefresh(dbinfo = dia.dbinfo)

    def openImportData(self):
        w = ImportData(dbinfo = self.dbinfo)
        w.setWindowTitle('Import new data in database')
        if w.exec_():
            self.refresh()

