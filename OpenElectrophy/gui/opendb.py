# -*- coding: utf-8 -*-
"""
widget for openning a existing db
"""


from .qt import *


from .guiutil.icons import icons
from .guiutil.myguidata import *

from sqlalchemy import create_engine
import tables
import quantities as pq
import numpy as np




def create_basic_widget(self, params):
    w = QWidget()
    mainLayout = QVBoxLayout()
    w.setLayout(mainLayout)
    h = QHBoxLayout()
    mainLayout.addLayout(h)
    l = QLabel()
    l.setPixmap( QIcon( self.icon).pixmap(64,64))
    h.addWidget(l)
    h.addWidget(QLabel(self.info))
    mainLayout.addWidget(params)
    return w



class DbConnect(object):
    def __init__(self,settings = None):
        
        self.settings = settings
        self.params_open = ParamWidget(self.ParametersOpen,  settings = settings, settingskey = 'opendb'+self.name)
        self.widget_opendb =  create_basic_widget(self, self.params_open)
        
        self.params_create = ParamWidget(self.ParametersCreate)
        self.widget_createdb =  create_basic_widget(self, self.params_create)
        
    def get_widget_opendb(self):
        return self.widget_opendb
    
    def get_widget_createdb(self):
        return self.widget_createdb


class DbConnectWithDBList(DbConnect):
    def __init__(self,settings = None):
        super(DbConnectWithDBList, self).__init__( settings = settings)
        
        mainlayout = self.widget_opendb.layout()
        h = QHBoxLayout()
        mainlayout.addLayout(h)
        self.comboDbList = QComboBox()
        self.comboDbList.setEditable(True)
        h.addWidget(self.comboDbList,3)
        but = QPushButton(QIcon(':/server-database') , 'Get db list')
        h.addWidget(but)
        but.clicked.connect(self.get_db_list)

    def half_url(self):
        d = self.params_open.to_dict()
        return '{name}://{user}:{password}@{host}:{port}/'.format(name =  self.name, **d)

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
            QMessageBox.warning(self.widget_opendb,'Fail',"Failed to get list : check host, user and password", 
                QMessageBox.Ok , QMessageBox.NoButton)
    
    def get_opendb_kargs(self):
        url = self.half_url()+str(self.comboDbList.currentText())
        return dict(url = url, numpy_storage_engine = 'sqltable')



class TypeMySQL(DbConnectWithDBList):
    name =  'mysql'
    info  ='To use MySQL, you need a configured server (distant or local)'
    ParametersOpen = type('ParametersOpen',(DataSet,), dict(host = StringItem('host', default = 'localhost'),
                                                                                                    port =  IntItem('port', 3306),
                                                                                                    user = StringItem('user', default = ''),
                                                                                                    password =  PasswordItem('password', default = '' ),
                                                                                                    ) )
    ParametersCreate = type('ParametersCreate',(DataSet,), dict(host = StringItem('host', default = 'localhost'),
                                                                                                    port =  IntItem('port', 3306),
                                                                                                    adminName = StringItem('adminName', default = ''),
                                                                                                    adminPassword =  PasswordItem('adminPassword', default = '' ),
                                                                                                    user = StringItem('user', default = ''),
                                                                                                    dbName = StringItem('dbName', default = ''),
                                                                                                    ) )
    icon =  ':/mysql.png'
    query_db_list = 'show databases'
    
    def create_a_new_db(self):
        d = self.params_create.to_dict()
        url = '{name}://{adminName}:{adminPassword}@{host}:{port}/'.format(name = self.name, **d)
        engine = create_engine( url )
        try:
            res= engine.execute("CREATE DATABASE `{dbName}`".format(**d) )
            res= engine.execute("GRANT ALL on `{dbName}`.* TO `{user}` ".format( **d) )
        except:
            QMessageBox.warning(self.widget_createdb,u'Fail','Failed to create a database : check host, user and password', 
                QMessageBox.Ok , QMessageBox.NoButton)

        
    
class TypePostgresSQL(DbConnectWithDBList):
    name =  'postgresql'
    info  = 'To use PostgreSql, you need a configured server (distant or local)'
    ParametersOpen = type('ParametersOpen',(DataSet,), dict(host = StringItem('host', default = 'localhost'),
                                                                                                    port =  IntItem('port', 5432),
                                                                                                    user = StringItem('user', default = ''),
                                                                                                    password =  PasswordItem('password', default = '' ),
                                                                                                    ) )
    ParametersCreate = type('ParametersCreate',(DataSet,), dict(host = StringItem('host', default = 'localhost'),
                                                                                                    port =  IntItem('port', 5432),
                                                                                                    adminName = StringItem('adminName', default = ''),
                                                                                                    adminPassword =  PasswordItem('adminPassword', default = '' ),
                                                                                                    user = StringItem('user', default = ''),
                                                                                                    dbName = StringItem('dbName', default = ''),
                                                                                                    ) )
    icon =  ':/postgres.png'
    query_db_list = 'select datname from pg_database'

    def create_a_new_db(self):
        import psycopg2
        d = self.params_create.to_dict()
        url = '{name}://{adminName}:{adminPassword}@{host}:{port}/'.format(name = self.name, **d)
        engine = create_engine( url )
        try:

                conn = psycopg2.connect("dbname=template1 user={adminName} password={adminPassword}".format(**d))
                conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
                cur = conn.cursor()
                cur.execute('CREATE DATABASE {dbName} OWNER {user}'.format(**d) )
        except:
            QMessageBox.warning(self.widget_createdb,u'Fail','Failed to create a database : check host, user and password', 
                QMessageBox.Ok , QMessageBox.NoButton)


class TypeSQLite(DbConnect):
    name =  'sqlite'
    info  ='SQLite is a lightweight DB system contained in a single (big) file'
    ParametersOpen = type('ParametersOpen',(DataSet,), dict(sqlite_filename = FileOpenItem('SQLite file') ))
    ParametersCreate = type('ParametersCreate',(DataSet,), dict(sqlite_filename = FileSaveItem('SQLite file') ))
    icon =  ':/sqlite.png'
    
    def get_opendb_kargs(self):
        p = self.params_open.to_dict()
        url = 'sqlite:///'+p['sqlite_filename']
        return dict(url = url, numpy_storage_engine = 'sqltable')
    
    def create_a_new_db(self):
        p = self.params_create.to_dict()
        url = 'sqlite:///'+p['sqlite_filename']
        engine = create_engine( url )
        engine.connect()

class TypeSQLiteHDF5(DbConnect):
    name =  'sqlite+HDF5'
    info  ='Hybrid database SQLite+Hdf5'
    ParametersOpen = type('ParametersOpen',(DataSet,), dict(sqlite_filename = FileOpenItem('SQLite file'),
                                                                                                    hdf5_filename = FileOpenItem('HDF5 file')
                                                                                                    ))
    ParametersCreate = type('ParametersCreate',(DataSet,), dict(sqlite_filename = FileSaveItem('SQLite file'),
                                                                                                    hdf5_filename = FileSaveItem('HDF5 file'),
                                                                                                    complib = ChoiceItem('complib', ['blosc', 'zlib', 'None'])
                                                                                                    ))
    
    
    icon =  ':/sqlite_hdf5.png'
    

    def get_opendb_kargs(self):
        p = self.params_open.to_dict()
        return dict(url = 'sqlite:///'+p['sqlite_filename'],
                                hdf5_filename = p['hdf5_filename'],
                                numpy_storage_engine = 'hdf5',
                                )
        
    def create_a_new_db(self):
        p = self.params_create.to_dict()
        url = 'sqlite:///'+p['sqlite_filename']
        engine = create_engine( url )
        engine.connect()
        hfile = tables.openFile(p['hdf5_filename'], mode = "a", filters = tables.Filters(complevel=9, complib=p['complib'],))
        



dbtypes = [ TypeMySQL,TypeSQLite, TypePostgresSQL, TypeSQLiteHDF5 ]


class OpenOrCreateDB(QDialog) :
    def __init__(self  , parent = None , settings = None):
        super(OpenOrCreateDB, self).__init__( parent = parent)
        
        self.settings = settings
        
        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)
        
        self.mainLayout.addWidget(QLabel('Select the appropriate tab for SQL engine'))
        
        self.tabEngines = QTabWidget()
        self.mainLayout.addWidget(self.tabEngines)
        
        self.opendbguis = [dbtype(settings = self.settings) for dbtype in dbtypes ]
        for opendbgui in self.opendbguis:
            if self.mode =='opendb':
                self.tabEngines.addTab(opendbgui.get_widget_opendb() , opendbgui.name)
            elif self.mode =='createdb':
                self.tabEngines.addTab(opendbgui.get_widget_createdb() , opendbgui.name)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Open| QDialogButtonBox.Cancel)
        self.mainLayout.addWidget(buttonBox)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
    
    def get_dbengine(self):
        num = self.tabEngines.currentIndex()
        return self.opendbguis[num]
    
    def get_opendb_kargs(self):
        return self.get_dbengine().get_opendb_kargs()

    def create_a_new_db(self):
        num = self.tabEngines.currentIndex()
        self.opendbguis[num].create_a_new_db()

class OpenDB(OpenOrCreateDB):
    mode = 'opendb'

class CreateDB(OpenOrCreateDB):
    mode = 'createdb'




