# -*- coding: utf-8 -*-
"""
This is the mainwindow!!
"""

from .qt import *

import sys, os

from collections import deque


from .guiutil.icons import icons
from .guiutil.picklesettings import PickleSettings

from .opendb import OpenDB, CreateDB
from .explorer import MainExplorer
from .importdata import ImportData


from ..core.sqlmapper import open_db, MAX_BINARY_SIZE
from ..core.base import OEBase


if __name__ == '__main__' :
    app = QApplication([ ])

    
class MainWindow(QMainWindow) :
    def __init__(self, parent = None,
                applicationname = 'OpenElectrophy_0_3',
                ) :
        super(MainWindow, self).__init__(parent)
        
        self.settings = PickleSettings(applicationname=applicationname)
        self.applicationname = applicationname

        self.settings.getValueOrDefault('recently_opened_db', deque())
        self.settings.save()

        
        self.setWindowTitle(self.tr('OpenElectrophy'))
        self.setWindowIcon(QIcon(':/openelectrophy.png'))
        self.setMinimumSize(600,400)
        
        self.tabDatabases = QTabWidget()
        self.setCentralWidget(self.tabDatabases)
        self.tabDatabases.setTabsClosable(True)
        self.tabDatabases.tabCloseRequested.connect(self.closeOneExplorer)
        
        
        self.setDockNestingEnabled(True)

        self.createActions()
        self.createMenus()
        #self.createToolBars()

        self.explorers = [ ]
        
        
    def createActions(self):
        self.actionCreateDb = QAction(u'&Create a new database', self,
                                                                shortcut = "Ctrl+C",
                                                                icon =QIcon(':/create-db.png'))
        self.actionCreateDb.triggered.connect(self.createDatabase)
        
        self.actionOpenDb = QAction(u'&Open a database', self,
                                                                shortcut = "Ctrl+O",
                                                                icon =QIcon(':/open-db.png'))
        self.actionOpenDb.triggered.connect(self.openDatabaseDialog)
        
        self.actionOpenFile = QAction(u'Open read only file with neo (in memory DB)', self,
                                                                icon =QIcon(':/document-open-folder.png'))
        self.actionOpenFile.triggered.connect(self.openNeoFile)

        self.quitAct = QAction(self.tr("&Quit"), self)
        self.quitAct.setShortcut(self.tr("Ctrl+Q"))
        self.quitAct.setStatusTip(self.tr("Quit the application"))
        self.quitAct.setIcon(QIcon(':/window-close.png'))
        self.connect(self.quitAct, SIGNAL("triggered()"), self.close)

        self.aboutAct = QAction(self.tr("&About"), self)
        self.aboutAct.setStatusTip(self.tr("Show the application's About box"))
        self.aboutAct.setIcon(QIcon(':/help-about.png'))
        self.connect(self.aboutAct,SIGNAL("triggered()"), self.about)

        self.helpAct = QAction(self.tr("&Help"), self)
        self.helpAct.setStatusTip(self.tr("Help"))
        self.helpAct.setIcon(QIcon(':/help-contents.png'))
        self.connect(self.helpAct,SIGNAL("triggered()"), self.openHelp)




    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu(self.tr("&Dataset"))
        self.fileMenu.addAction(self.actionCreateDb)
        self.fileMenu.addAction(self.actionOpenDb)
        
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.actionOpenFile)
        self.fileMenu.addSeparator()
        
        
        self.recentlyOpenedMenu = self.fileMenu.addMenu(QIcon(':/view-history.png'), u'Recently opened databases')
        self.refresh_recentlyOpenedMenu()
        
        
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.quitAct)

        self.menuBar().addSeparator()
        
        self.menuBar().addSeparator()
        self.helpMenu = self.menuBar().addMenu(self.tr("&Help"))
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.helpAct)
        
        
    
    def refresh_recentlyOpenedMenu(self):
        self.recentlyOpenedMenu.clear()
        for kargs in self.settings['recently_opened_db']:
            act = self.recentlyOpenedMenu.addAction(QIcon(kargs['icon']), kargs['url'])
            act.kargs = kargs
            act.triggered.connect(self.open_recently)
            

    def createDatabase(self):
        d = CreateDB(parent = self,settings =self.settings)
        if d.exec_():
            d.create_a_new_db()
    
    def open_recently(self):
        self.openDatabase(**self.sender().kargs)
    
    def openDatabaseDialog(self):
        d = OpenDB(parent = self,settings =self.settings)
        if d.exec_():
            kargs =  d.get_opendb_kargs()
            kargs['myglobals'] = None
            kargs['suffix_for_class_name'] = ''
            kargs['use_global_session'] = False
            kargs['relationship_lazy'] =  'select'
            #TODO
            #~ object_number_in_cache = 3000
            #~ compress = 'blosc'
            #~ max_binary_size = MAX_BINARY_SIZE
            
            kargs['icon'] = d.get_dbengine().icon
            self.openDatabase(**kargs)
            
    
    def openDatabase(self, **kargs):
        kargs_open = { }
        kargs_open.update(kargs)
        kargs_open.pop('icon')
        dbinfo = open_db(**kargs_open)
        dbinfo.kargs_reopen = kargs_open # for futur open if schema modified
        #TODO do this better:
        name = dbinfo.url.split('/')[-1]
        explorer = MainExplorer(dbinfo = dbinfo, settings = self.settings, name = name)
        self.explorers.append(explorer )
        
        icon = QIcon(kargs['icon'])
        
        self.tabDatabases.addTab( explorer ,icon,  name)
        self.tabDatabases.setCurrentIndex(self.tabDatabases.count()-1)
        
        d = self.settings['recently_opened_db']
        for recently in d:
            if recently['url'] == kargs['url']:
                d.remove(recently)
                break
        d.append(kargs)
        while len(d) >= 5:
            d.popleft()
        self.settings['recently_opened_db'] = d
        self.refresh_recentlyOpenedMenu()
        
    
    def openNeoFile(self):
        
        
        dbinfo = open_db(url = 'sqlite://', myglobals = None, suffix_for_class_name = '',
                                use_global_session = False, relationship_lazy = False, object_number_in_cache = None,
                                max_binary_size = MAX_BINARY_SIZE, compress = None,)
        
        w = ImportData(dbinfo = dbinfo, use_thread = False)
        if w.exec_():
            name = '{} {}'.format(w.ioclass.name, os.path.basename(w.names[0]) )
            explorer = MainExplorer(dbinfo = dbinfo, name = name)
            self.explorers.append(explorer)
            self.tabDatabases.addTab( explorer , QIcon(':/document-open-folder.png'), name)
            self.tabDatabases.setCurrentIndex(self.tabDatabases.count()-1)
        
    def closeOneExplorer(self):
        num = self.tabDatabases.currentIndex()
        self.tabDatabases.removeTab(num)
        
        
    
    def getCurrentExporer(self):
        num = self.tabDatabases.currentIndex()
        return self.explorers[num]
            
    #~ def openImportData(self):
        #~ if len( self.explorers) == 0: return
        #~ explorer = self.getCurrentExporer()
        #~ w = ImportData(dbinfo = explorer.dbinfo)
        #~ w.setWindowTitle('Import new data in database')
        #~ if w.exec_():
            #~ explorer.refresh()

    #~ def openTableDesign(self):
        #~ d = TableDesign(metadata =self.getCurrentExporer().metadata,
                                    #~ session = self.getCurrentExporer().session,
                                    #~ explorer = self.getCurrentExporer(),
                                    #~ )        
        #~ d.exec_()
    
    
    def about(self):
        QMessageBox.about(self, self.tr("About Dock Widgets"),
                    self.tr("""<b>OpenElectrophy</b> : <BR/>
                    A all-in-one GUI+toolbox+datastorage+framework<BR/>
                    for analysing extra or intra cellular data, dev by<BR/>
                    <b>Samuel GARCIA</b>, <BR/>
                    in Centre de Recheche en Neurosciences de Lyon, CNRS, Lyon, France
                    """
                    ))

    def openHelp(self):
        from PyQt4.QtWebKit import QWebView
        
        if not hasattr(self, 'helpview'):
            self.helpview = QWebView()
            self.helpview.setWindowFlags(Qt.SubWindow)
            self.helpview.load(QUrl('http://packages.python.org/OpenElectrophy/index.html'))
        
        self.helpview.setVisible(True)
        

if __name__ == '__main__' :
	mw =MainWindow()
	mw.show()
	app.exec_()
