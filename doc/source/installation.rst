.. _installation_page:

****************
Installation
****************


Requirements
------------

    * Python  2.7
    * numpy >= 1.3.0
    * quantities >= 0.9.0
    * neo >= 0.2.1
    * sqlalchemy >= 0.7.8
    * sqlalchemy-migrate >=0.7.2
    * scipy >=0.10
    * matplotlib>=1.1.0
    * pyqtgraph
    * guidata >=1.4.1
    * PyQT4 >= 4.9
    * joblib >=0.6.4
    * tables >=2.3.1
    * pywavelets (pywt)
    * python-sklearn >=0.11
    * pandas
    * cython

Optional but important:
    * psycopg2 (for postgreesql)
    * mysqldb (for mysql)
    * blosc (for fast compression)
    * python-snappy (for really fast compression)
    * lz4 (for really really fast compression)

You can also instal:
   * a mysql server
   * a postrgesql server
but OpenElectrophy also work in file mode or with SQLite db.


Linux
=====================
    
    For debian/ubuntu users, open a terminal:
    
    **Step 1, dependencies**::
    
            sudo apt-get install python python-scipy python-numpy python-matplotlib python-qt4 python-mysqldb python-pip python-psycopg2 python-dev gfortran python-pywt python-sqlalchemy python-migrate python-tables python-joblib  python-guidata python-sklearn python-pandas python-xlwt python-joblib cython
            sudo pip install quantities neo pyqtgraph


    **Step 2, OpenElectrophy**:
        You have two choices:
            1. From pypi (this is the latest stable release)::
                
                sudo pip install OpenElectrophy
         
            2. From source (this includes up-to-date features and bugfixes as they are added)::
                
                sudo apt-get install git
                git clone git@github.com:OpenElectrophy/OpenElectrophy.git
                cd OpenElectrophy
                sudo python setup.py install

Client under Windows with winpython
======================


Steps:
    1. Download winpython http://code.google.com/p/winpython/
    2. Choose win3é or amd64 if you have win64
    3. Choose for the path. Example: C:\\winpython-2.7.3.amd64
    4. in this path lanch control panel. This tool help you to install package. (See http://code.google.com/p/winpython/wiki/WPPM)
    5. Download manually all that depencies and install them withh winpython wontrol panel (choose the good platform win32 or amd64):
        * quantities (http://pypi.python.org/pypi/quantities)
        * neo (http://pypi.python.org/pypi/neo)
        * sqlalchemy-migrate (http://pypi.python.org/pypi/sqlalchemy-migrate)
        * joblib (http://pypi.python.org/pypi/joblib)
        *  blosc (http://pypi.python.org/pypi/blosc/1.0.3)
        * MySQL-python (http://www.lfd.uci.edu/~gohlke/pythonlibs/)
        * pywavelet (http://pypi.python.org/pypi/PyWavelets/)
        * pyqtgraph (http://pypi.python.org/pypi/pyqtgraph/0.9.3)
        
    6. Dowload OPenElectrophy (http://pypi.python.org/pypi/OpenElectrophy) and install it.
    7. In the controal panel> Advanced>register your python

.. warning::
    python-snappy and lz4 are hard to install under windows because they need a compiler at installation times.
    So database access can be slower.


Client under OSX
=========================


I have few experience with apple devices but I succed installing OpenElectrophy once.

For that I used homebrew : http://brew.sh/
It is a ruby script that help you to install many things (include python)

Open a terminal and run theses command:
    * ruby -e "$(curl -fsSL https://raw.github.com/Homebrew/homebrew/go/install)"
    * export PATH=/usr/local/bin:$PATH
    * brew install python
    * brew install pyqt
    * brew install hdf5
    * brew install gfortran
    * brew install pip
    * pip install numpy
    * pip install scipy
    * pip install matplotlib
    * pip install pyqtgraph
    * pip install quantities
    * pip install neo
    * pip install joblib
    * pip install cython
    * pip install sqlalchemy
    * pip install sqlalchemy-migrate
    * pip install numexpr
    * pip install tables
    * pip install scikit-learn
    * pip install pywavelets
    * pip install guidata
    * pip install docutils
    * pip inistall scikits-image
    * pip install blosc
    * pip install pandas
    * pip install xlwt
    * Dowload OPenElectrophy (http://pypi.python.org/pypi/OpenElectrophy) and install it.

Notes some points need compilation and lot of times (pyqt, scipy, ...).


.. warning::
    Many new python users on OSX suffer of the double (tripple) python installation. The method above use homebrew.
    Read this https://github.com/mxcl/homebrew/wiki/Homebrew-and-Python
    Be sure that when you do "which python" in a terminal it give you the good path.
    
    



Test your installation
===============================


If you want to test the UI of OpenElectrophy :

 * Linux : open a console (terminal) type::
     
     startOpenElectrophy.py
     
 * Windows : click (or make a shortcut on your desktop) on::
     
    C:\\WinPython-64bit-2.7.3.1\\python-2.7.3.amd64\\Scripts\\startOpenElectrophy
    


If you want to test if  OpenElectrophy module is installed, open an ipython interactive console ::
    
    import OpenElectrophy


MySQL server under linux
=============================

Just type this ::

    sudo apt-get install mysql-server

During the installation process, choose a password for root (admin).


MySQL server under Windows
=============================


Here you can download binaries for mysql server: http://dev.mysql.com/downloads/


Basic server administration
==================================

The basic MySQL administration is quite simple: you only need to create users, one database, and to grant each user access to the database.

You just have to type in a mysql console.

User creation ::

	CREATE USER user IDENTIFIED BY PASSWORD 'password'

Database creation ::

	CREATE DATABASE  db_name

Privileges for the user on this database ::

	GRANT ALL ON db_name.* TO user






Troubleshooting
==================================

 * **Problems for importing big file (>1Go) in MySQL**
 
    If you experience problems for importing heavy file in mysql you should change this parameters in mysql.cnf on server side ::
        
        max_allowed_packet=32G

    Some users hd reported that this parameters also cause problem in client side.
