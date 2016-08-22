# -*- coding: utf-8 -*-
from setuptools import setup
import os

from setuptools import setup, find_packages

from OpenElectrophy.version import __version__  as version

long_description = open("README.txt").read()


if os.name == 'nt':
    scripts = ['startOpenElectrophy.py',]
    entry_points = {
                                'gui_scripts' : [ 'startOpenElectrophy = startOpenElectrophy'],
                            }
else:
    scripts = ['startOpenElectrophy.py']
    entry_points = None


install_requires=[
                'numpy',
                'quantities',
                'neo>=0.4,<0.5',
                'scipy',
                'matplotlib',
                'sqlalchemy',
                'sqlalchemy-migrate',
                'pyqtgraph',
                'guidata',
                'joblib',
                'tables',
                'pywavelets',
                'scikit-learn',
                'blosc',
                ]

#~ numexpr

# these are optional because hard to instal on win32:
   #~ 'MySQLdb (>=1.2.3)',
   #~ 'psycopg2',
   #~ 'blosc',
   #~ 'snappy',
   #~ 'lz4',


setup(
    name = "OpenElectrophy",
    version = version,
    packages = find_packages(),
    scripts = scripts,
    entry_points = entry_points,
    include_package_data=True,
    install_requires = install_requires,
    requires = [ ],
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




