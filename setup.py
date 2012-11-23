# -*- coding: utf-8 -*-
"""

NON:   http://sourceforge.net/projects/mingw-w64/files/mingw-w64/mingw-w64-release/
OUI:  http://www.microsoft.com/en-us/download/details.aspx?id=18950


distutils.cfg dans C:\WinPython-64bit-2.7.3.1\python-2.7.3.amd64\Lib



Note install on windows:
   1. - winpython http://code.google.com/p/winpython/  and install it in C:\WinPython-64bit-2.7.3.1
   2. - execute C:\python-2.7.3.amd64\WP control PANEL  MENU>Advanced>register distribution
   3.- cd C:\python-2.7.3.amd64\Sripcts
   3. - easy_install pip
   4. - pip install quantities
   5. - pip install neo
   6. - pip install sqlalchemy-migrate
   7. - pip install joblib
   7. - Download pyton blosc (http://pypi.python.org/pypi/blosc/1.0.3) and install it
   8. - Downlod python mysql (http://www.lfd.uci.edu/~gohlke/pythonlibs/)
PB   9. - Download lz4 http://pypi.python.org/pypi/lz4
PB   10. - Download snappy http://pypi.python.org/pypi/python-snappy
   11. - Download pyqtgraph () rename it pyqtgraph-223.0.0.win-amd64-py2.7
   12. - pip install OpenElectrophy

"""


from setuptools import setup, find_packages

from OpenElectrophy.version import version

long_description='''
OpenElectrophy is a framework to facilitate storage, manipulation and analysis 
of electrophysiological data.

The GUI have been design with a particular attention to provide fast and intuitive
acces to data but OpenElectrophy is at the same time a base package to write
new analysis based on scripts.

Analysis tools included in OpenELectrophy are spike sorting and oscillation
detection. Further analysis have to be written but OpenElectrophy provides
a library of class and function which highly facilitates the querying of useful
data in the database and their manipulation.
'''

import os

if __name__=="__main__":
    if os.name == 'nt':
        scripts = ['startOpenElectrophy.pyw',]
        entry_points = {
                                    'gui_scripts' : [ 'startOpenElectrophy = startOpenElectrophy'],
                                }
    else:
        scripts = ['startOpenElectrophy.py']
        entry_points = None
    
    setup(
        name = "OpenElectrophy",
        version = version,
        packages = find_packages(),
        scripts = scripts,
        entry_points = entry_points,
        include_package_data=True,
        
        install_requires=[
                        'neo>=0.2',
                        'numpy>=1.3.0',
                        'scipy>=0.8.0',
                        'matplotlib>=0.99.1',
                        'SQLAlchemy>=0.7',
                        'sqlalchemy-migrate>=0.6',
                        'scikit-learn',
                        ],
                        
        requires = ['PyQt4 (>=4.6.2)',
                       'MySQLdb (>=1.2.3)',
                      ],
        author = "OpenElectrophy authors and contributors",
        author_email = "sam.garcia.die@gmail.com",
        maintainer = "Samuel Garcia",
        maintainer_email = "sam.garcia.die@gmail.com",
        long_description = long_description,
        url = 'http://packages.python.org/OpenElectrophy/',
        license = "BSD",
        description = "OpenElectrophy : an electrophysiological data- and analysis-sharing framework",
        classifiers=['Development Status :: 3 - Alpha',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: BSD License',
            'Natural Language :: English',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 2',
            'Topic :: Scientific/Engineering :: Bio-Informatics'
            ],
    )



