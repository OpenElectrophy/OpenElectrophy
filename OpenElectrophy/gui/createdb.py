# -*- coding: utf-8 -*-
"""
widget for creating a db
"""

from .qt import *

from .guiutil.icons import icons
from .guiutil.myguidata import *


from sqlalchemy import create_engine

import quantities as pq
import numpy as np




from .opendb import dbtypes


class CreateDB(QDialog) :
    def __init__(self  , parent = None , settings = None):
        super(CreateDB, self).__init__( parent = parent)
        
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
