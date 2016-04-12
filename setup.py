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
                'numpy>=1.3.0',
                'quantities>=0.9.0',
                'neo>=0.3',
                'scipy>=0.9.0',
                'matplotlib>=1.1.0',
                'sqlalchemy>=0.7',
                'sqlalchemy-migrate>=0.7',
                'pyqtgraph>=0.9.3',
                'guidata>=1.4.1',
                'joblib>=0.6.4',
                'tables>=2.3.1',
                'pywavelets>=0.2.2',
                'scikit-learn>=0.11',
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




