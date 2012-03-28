# -*- coding: utf-8 -*-
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
                        'sklearn',
                        ],
                        
        requires = ['PyQt4 (>=4.6.2)',
                       'MySQLdb (>=1.2.3)',
                      ],
        author = "Neo authors and contributors",
        author_email = "sam.garcia.die@gmail.com",
        maintainer = "Samuel Garcia",
        maintainer_email = "sam.garcia.die@gmail.com",
        long_description = long_description,
        url = 'http://packages.python.org/OpenElectrophy/'
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



