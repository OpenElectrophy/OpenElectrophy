# -*- coding: utf-8 -*-
"""
widget for openning a existing db
"""



from PyQt4.QtCore import *
from PyQt4.QtGui import *


from .guiutil.icons import icons
from .guiutil.myguidata import *

from sqlalchemy import create_engine

import quantities as pq
import numpy as np


class DbConnect(object):
    def __init__(self,settings = None):
        
        self.settings = settings
        
        self.widget = QWidget()
        self.mainLayout = QVBoxLayout()
        self.widget.setLayout(self.mainLayout)
        h = QHBoxLayout()
        self.mainLayout.addLayout(h)
        l = QLabel()
        l.setPixmap( QIcon(self.icon).pixmap(64,64))
        h.addWidget(l)
        h.addWidget(QLabel(self.info))
        self.params = ParamWidget(self.Parameters,  settings = settings, settingskey = 'dbconnections')
        self.mainLayout.addWidget(self.params)
    
    def get_widget(self):
        return self.widget


class DbConnectWithDBList(DbConnect):
    def __init__(self,settings = None):
        super(DbConnectWithDBList, self).__init__( settings = settings)

        h = QHBoxLayout()
        self.mainLayout.addLayout(h)
        self.comboDbList = QComboBox()
        self.comboDbList.setEditable(True)
        h.addWidget(self.comboDbList)
        but = QPushButton(QIcon(':/server-database') , 'Get db list')
        h.addWidget(but)
        but.clicked.connect(self.get_db_list)

    def half_url(self):
        d = self.params.to_dict()
        d['name'] = self.name
        return '{name}://{user}:{password}@{host}:{port}/'.format(**d)

    def get_db_list(self):
        engine = create_engine( self.half_url() )
        try:
            res= engine.execute(self.query_db_list)
            db_list = []
            for l, in  res.fetchall():
                if l not in [ 'information_schema', 'template1', 'template0', 'postgres']:
                    db_list.append(l)
            self.comboDbList.clear()
            self.comboDbList.addItems(db_list)
        except:
            QMessageBox.warning(self.widget,'Fail',"Failed to get list : check host, user and password", 
                QMessageBox.Ok , QMessageBox.NoButton)
    
    def get_kargs(self):
        url = self.half_url()+str(self.comboDbList.currentText())
        return dict(url = url)
        


class TypeMySQL(DbConnectWithDBList):
    name =  'mysql'
    info  ='To use MySQL, you need a configured server (distant or local)'
    Parameters = type('Parameters',(DataSet,), dict(host = StringItem('host', default = 'localhost'),
                                                                                                    port =  IntItem('port', 3306),
                                                                                                    user = StringItem('user', default = ''),
                                                                                                    password =  PasswordItem('password', default = '' ),
                                                                                                    ) )
    icon =  ':/mysql.png'
    query_db_list = 'show databases'
    
class TypePostgresSQL(DbConnectWithDBList):
    name =  'postgresql'
    info  = 'To use PostgreSql, you need a configured server (distant or local)'
    Parameters = type('Parameters',(DataSet,), dict(host = StringItem('host', default = 'localhost'),
                                                                                                    port =  IntItem('port', 5432),
                                                                                                    user = StringItem('user', default = ''),
                                                                                                    password =  PasswordItem('password', default = '' ),
                                                                                                    ) )
    icon =  ':/postgres.png'
    query_db_list = 'select datname from pg_database'


class TypeSQLite(DbConnect):
    name =  'sqlite'
    info  ='SQLite is a lightweight DB system contained in a single (big) file'
    Parameters = type('Parameters',(DataSet,), dict(filename = FileOpenItem('SQLite file') ))
    icon =  ':/sqlite.png'
    
    def get_kargs(self):
        p = self.params.to_dict()
        url = 'sqlite:///'+p['filename']
        return dict(url = url)


class TypeSQLiteHDF5(DbConnect):
    name =  'sqlite+HDF5'
    info  ='Hybrid database SQLite+Hdf5'
    Parameters = type('Parameters',(DataSet,), dict(filename_sqlite = FileOpenItem('SQLite file'),
                                                                                                    hdf5_filename = FileOpenItem('HDF5 file')
                                                                                                    ))
    icon =  ':/sqlite_hdf5.png'

    def get_kargs(self):
        p = self.params.to_dict()
        return dict(url = 'sqlite:///'+p['filename_sqlite'],
                                hdf5_filename = p['hdf5_filename'])



dbtypes = [ TypeMySQL,TypeSQLite, TypePostgresSQL, TypeSQLiteHDF5 ]


class OpenDB(QDialog) :
    def __init__(self  , parent = None , settings = None):
        super(OpenDB, self).__init__( parent = parent)
        
        self.settings = settings
        
        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)
        
        self.mainLayout.addWidget(QLabel('Select the appropriate tab for SQL engine'))
        
        self.tabEngines = QTabWidget()
        self.mainLayout.addWidget(self.tabEngines)
        
        self.opendbguis = [dbtype(settings = self.settings) for dbtype in dbtypes ]
        for opendbgui in self.opendbguis:
            self.tabEngines.addTab(opendbgui.get_widget() , opendbgui.name)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Open| QDialogButtonBox.Cancel)
        self.mainLayout.addWidget(buttonBox)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

    def get_kargs(self):
        num = self.tabEngines.currentIndex()
        return self.opendbguis[num].get_kargs()


