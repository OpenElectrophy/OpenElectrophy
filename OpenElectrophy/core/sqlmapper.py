#encoding : utf-8
"""

SQL mapper
============

Hi Chris. Thank you to read this. This will the fondation of OE3. It is imprtant to be OK.


Concepts
-------------------

This module is on top of sqlalchemy and offer the user the abbility to play with databases with few knownledges.

The model object is based on neo 0.2 enhanced with some classes (Oscillation, respiratorySignal, imageSerie, ImageMask, LickTrain)

Main possibilities of this mapper are:
  * Create automagically table schema from neo.description (enhenced by OpenElectrophy.description) on MySQL, SQLite or PG (and 
        and normally all sqlalchemy backends)
  * Create for the user new tables and its relationship (Ex Animal on top of Block)
  * when openning a databse explore all tables schema to also map new columns and new tables.
  * map transparently numpy.ndarray and quantities.Quantity in 3 or 4 SQL columns
  * cache loaded object in fixed size queue to avoid reloding when accing several times
  * cache big numpy.arrays on the the local disk with memmap to avoid long network transfert.


Conversion
----------------------------


Rules of conversions:
    * standart python are converted naturally to one column with sqlalchemy types (str>Text, int>Integer, datetime>DateTime,  float > Float)
    * np.array attributes are split in 3 SQL columns (buffer BLOB, shape TEXT, dtype TEXT)
    * Quantity attributes are split in 4 SQL columns (buffer BLOB, shape TEXT, dtype TEXT, units TEXT)
    * Classes that inerit in neo Quantities have 4 columns = like Quantities attrbiutes (AnalogSIgnal.signal, SpikeTrain.times, ...)
    
Notes:
    * all numpy.array and pq.Quantity are deffered loaded. (They are load only when used)
    * np.array can be memmap cached.
    * np.array can be compressed with zlib

Rules of relationship:
    * one_to_many and many_to_one : the child name have a column (Interger) which is also Index construct with: *parentname.lower()*+'_id'
    * many_to_many: a table  with XREF do the job. Ex:   table1XREFtable2



Schema creation and manipualtion
----------------------------------------------------------------


Example1 : Creating a db, the first opening  create the schema::

    url = 'sqlite:///myfirstdb.sqlite'
    open_db(url)



   




Standart save and load
-------------------------------------------

There are ways for playing with object in databases 

  1. the easy one is to open_db with:
      * use_global_session=True
      * myglobals = globals()

    With that you can do for creating::

        url = 'sqlite:///myfirstdb.sqlite'
        open_db(url, use_global_session=True, myglobals = globals())
        bl = Block(name = 'a new block')
        seg = Segment(name = 'a segment', index = 0)
        bl.segments.append(seg)
        bl.save()
        
    And this for loading::
    
        url = 'sqlite:///myfirstdb.sqlite'
        open_db(url, use_global_session=True, myglobals = globals())
        bl = Block.load(id = 50)
        print bl.id
        print bl.name
        # also
        bl = Block(id = 50)
        print bl.id
        print bl.name
        

  2. The sqlalchemy way play with session by our own::

        url = 'sqlite:///myfirstdb.sqlite'
        dbinfo = open_db(url, use_global_session=False, myglobals = globals())
        Session = dbinfo.Session # this is a session generator in sqlalchemy land.
        
        # create a session
        session = Session()
        bl = Block(name = 'a new block')
        seg = Segment(name = 'a segment', index = 0)
        bl.segments.append(seg)
        session.add(bl)
        session.commit()
        id_bl = bl.id
        session.close()
        
        # create another session
        session = Session()
        reload_bl = session.query(Block).get(id_bl)
        
    
    This way is safer with multiprocessing and GUI.


Mapped classes
--------------------------------

Classes in OE are generated on the fly when openning a db.

Each time a new db is opened (with open_db) each time the classes are re created (in a dict)

When scripting, you can injected this mapped_classes dict in your locals() or globals() to use direectly object : Block, Segment, AnalogSignal, ...

Ex::

    open_db(url, myglobals= locals())

is equivalent to::

    dbinfo= open_db(url)
    locals().update(dbinfo.mapped_classes)

You also inject in globals() for standart scripting and interactive environement (ipython)::

    open_db(url, myglobals= globals())



If you want to avoid problems with neo namespace you can add a prefix to lass name (suffix_for_class_name = '_',) ::

    from neo import *
    print Block # this is a neo.Block
    open_db(url, myglobals= locals(), suffix_for_class_name = '_')
    print _Block # this is a OpenElectrophy.core.mapper._Block



Links with neo
---------------------------------

Mapped classes are not directly neo classes because:
  * Some neo classes directly inherits numpy.array that make the mapper tricky!
  * Some neo classes directly inherits numpy.array that force the mapper to load all BLOB columns
  * free attributes are dealt with annotations dict in neo they are standart mapped attributes in OE.

In short neo.Block is not a Block of OpenElectrophy but it behave the same (relationship, attributes).


You can convert objects from neo to OE with OEbase.to_neo method for all object.
And recipro objects OE to neo with OEBase.from_neo (class method).
This is usefull for toolboxes bases on neo objects.


Example: read with neo io and save to database::

    from neo import PlexonIO
    from OpenElectrophy import open_db
    reader = io.PlexonIO(filename='File_plexon_1.plx')
    block_neo = reader.read_block()
    url = 'sqlite:///' # in memory
    open_db(url, myglobals= globals())
    block_OE = Block.from_neo(bl, cascade = True) # this convert block and all hierachy
    block_OE.save() # this save the block and all the hierachy
    
Cache
------------------

To avoid multiple reload when queying several times the same object.
The mapper offer a very basic cache system : with the event load sytem of sqlalchemy.
The object is put is in big list (collections.deque) with a limit size so the object is referenced a least once.
At futur reaload the object is not reloaded.

Example::
    
    import quantities as pq
    url = 'sqlite:///myfirstdb.sqlite'
    open_db(url, myglobals = globals(), object_number_in_cache = 20)
    
    ana = AnalogSignal( signal = np.arange(1000)*pq.mV, t_start= 0.*pq.s, sampling_rate = 200*pq.Hz)
    ana.save()
    id = ana.id
    
    del ana
    for i in range(50):
        # the load is done only once
        ana  = AnalogSignal(id = id)


Memmap cache for numpy.array
-------------------------------------------------------------

numpy.array and quantity attributes can be heavy and you cannot keep them all in memory.
The mapper offer a memmaped cache system for this attributes.
The behavior is simple: when they are loaded the first time the BLOB (raw binary part) is directly copied in a files in 
memmaped_path with its objetc name+id+attributes name.

The following load for this attributes will be take directly in the path avoiding load from the db.

This is the user responsability to clear the path (delete files) to keep and keep synchronize with the db.
Take care of this when you play with a db from several computers and when you modify a numpy.array attributes.
Other computer will not see the change. But in general case, this is usefull enougth because:
  * you rarelly modify numpy.array but often read them.
  * you are alone to analyse your datasets.




Reference
-----------------------


.. autofunction:: open_db

.. autofunction:: execute_sql

.. autoclass:: DataBaseConnectionInfo


"""

from collections import OrderedDict, deque

import sqlalchemy
import migrate.changeset
from sqlalchemy import orm

from sqlalchemy import create_engine  , MetaData
from sqlalchemy import Table, Column, Integer, String, Float,  Text, UnicodeText, LargeBinary, DateTime, FLOAT
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import event
from sqlalchemy.orm import object_session

import os
import quantities as pq
from datetime import datetime
import numpy as np

import zlib
import blosc

from base import OEBase




MAX_BINARY_SIZE = 2**30


python_to_sa_conversion = { 
                                                        str : Text,
                                                        int : Integer,
                                                        datetime : DateTime,
                                                        float : Float,
                                                        }
#~ sa_to_python_conversion = { }
#~ for k,v in python_to_sa_conversion.items():
    #~ sa_to_python_conversion[v] = k


global globalsesession
globalsesession = None




def create_column_if_not_exists(table, attrname, attrtype):
    """
    Create a clolumn in a table given its python type.
    
    :param table: 
    
    :param attribute:
    
    """
    colnames = [ col.name for col in table.columns ]
    
    
    if attrtype == np.ndarray or attrtype == pq.Quantity :
        if attrname+'_blob' not in colnames:
            col =  Column(attrname+'_shape', String(128))
            col.create( table)
            col =  Column(attrname+'_dtype', String(128))
            col.create( table)
            col =  Column(attrname+'_blob', LargeBinary(MAX_BINARY_SIZE))
            col.create( table)
            if attrtype == pq.Quantity :
                col =  Column(attrname+'_units', String(128))
                col.create( table)
    elif attrtype in python_to_sa_conversion:
        if attrname not in colnames:
            col = Column(attrname, python_to_sa_conversion[attrtype])
            col.create( table )
    else:
        raise NotImplementedError

def create_one_to_many_relationship_if_not_exists(parenttable, childtable):
    if parenttable.name.lower()+'_id' in childtable.columns: return
    col=  Column(parenttable.name.lower()+'_id', Integer)#, ForeignKey(parenttable.name+'.id'))
    col.create( childtable)
    ind = Index('ix_'+childtable.name.lower()+'_'+parenttable.name.lower()+'_id', col , unique = False)
    ind.create()

def create_many_to_many_relationship_if_not_exists(table1, table2, metadata):
    xref1 = table1.name+'XREF'+table2.name
    xref2 = table2.name+'XREF'+table1.name
    if xref1 in metadata.tables: return
    if xref2 in metadata.tables: return
    c1 = Column(table1.name.lower()+'_id', Integer, ForeignKey(table1.name+'.id'), index = True)
    c2 = Column(table2.name.lower()+'_id', Integer, ForeignKey(table2.name+'.id'), index = True)
    table =  Table(xref1, metadata, c1, c2  )
    table.create()




def create_table_from_class(oeclass, metadata):
    """
    Create one table from a OEclass (see classes module).
    This do not create relationship.
    
    :param tablename: tablename (str)
    
    :param schema_description: see schema_description
    
    :param metadata: sqlalchemy metadata
    
    """
    #~ columns = [ Column('id', Integer, primary_key=True, index = True) ,]
    #~ table =  Table(oeclass.tablename, metadata, *columns  , mysql_charset='utf8', mysql_engine='InnoDB',)
    table =  Table(oeclass.tablename, metadata, Column('id', Integer, primary_key=True, index = True)  , mysql_charset='utf8', mysql_engine='InnoDB',)
    #~ table =  Table(oeclass.tablename, metadata, Column('id', Integer, primary_key=True, index = True)  , mysql_engine='InnoDB',)
    table.create()
    for attrname, attrtype in oeclass.usable_attributes.items():
        create_column_if_not_exists(table,  attrname, attrtype)
    return table


def create_or_update_database_schema(engine, oeclasses, max_binary_size = MAX_BINARY_SIZE,):
    """
    Create a database schema from oeclasses list (see classes module).
    If the schema already exist check if all table and column exist.
    
    
    :params engine: sqlalchemy engine
    
    :params oeclasses: list of oeclass
    
    """
    
    metadata = MetaData(bind = engine)
    metadata.reflect()

    class_by_name = { }
    for oeclass in oeclasses:
        class_by_name[oeclass.__name__] = oeclass
    
    # check all tables
    for oeclass in oeclasses:
        tablename = oeclass.tablename
        
        if tablename not in metadata.tables.keys() :
            # create table that are not present in db from class_names list
            table = create_table_from_class(oeclass, metadata)
        else:
            #check if all attributes are in SQL columns
            table = metadata.tables[tablename]
            for attrname, attrtype in oeclass.usable_attributes.items():
                create_column_if_not_exists(table,  attrname, attrtype)
    
    # check all relationship
    for oeclass in oeclasses:
        # one to many
        for childclassname in oeclass.one_to_many_relationship:
            parenttable = metadata.tables[oeclass.tablename]
            childtable = metadata.tables[class_by_name[childclassname].tablename]
            create_one_to_many_relationship_if_not_exists(parenttable, childtable)
        
        # many to many
        for classname2 in oeclass.many_to_many_relationship:
            table1 = metadata.tables[oeclass.tablename]
            table2 = metadata.tables[class_by_name[classname2].tablename]
            create_many_to_many_relationship_if_not_exists(table1, table2, metadata)
            
    metadata.create_all()


def create_classes_from_schema_sniffing( engine, oeclasses,
                                                                                suffix_for_class_name = '_',):
    """
    This function exxplore a database schema and generate classes ready to be mapped by sa.
    This detect attributes (even numpy or quantities one)
    You can give a list a already existing classes (oeclasses):
      * if the name already exists in this list, the class will iherit this one
      * if not, the class will inherits OEBase
    
    Why this ????
    Because a user can add table or column to any databse for a particular puporse so we can't directly
    map predefined classes from OpenElectrophy.core.classes (Block, Segment, ...). We need to generate new ones.
    
    :params engine: sqlalchemy engine
    
    :params oeclasses: list of oeclass
    
    :params suffix_for_class_name: suffix for theses classes name
    
    
    """
    class_by_name = { }
    for oeclasse in oeclasses:
        class_by_name[oeclasse.__name__] = oeclasse
    
    tablename_to_oeclass = { }
    for oeclass in oeclasses:
        tablename_to_oeclass[oeclass.tablename] = oeclass
    
    
    generated_classes = [ ]
    
    #~ classes_by_tablename = { }
    metadata = MetaData(bind = engine)
    metadata.reflect()
    
    all_many_to_many = { }
    for tablename, table in metadata.tables.items() :
        # detect many_to_many_relationship
        if 'XREF' in tablename:
            table1, table2 = tablename.split('XREF')
            all_many_to_many[table1] = table2
            all_many_to_many[table2] = table1
            continue
        
        # create the generated class
        if tablename in tablename_to_oeclass:
            classname  = suffix_for_class_name+tablename_to_oeclass[tablename].__name__
            neoclass = tablename_to_oeclass[tablename].neoclass
            classbase = tablename_to_oeclass[tablename]
        else:
            classname = suffix_for_class_name+tablename
            neoclass = None
            classbase = OEBase
        genclass = type(classname,(classbase,), { })
        genclass.tablename = tablename
        genclass.neoclass = neoclass
        genclass.usable_attributes = OrderedDict(  )
        genclass.one_to_many_relationship =  [ ]
        genclass.many_to_one_relationship =  [ ]
        genclass.many_to_many_relationship = [ ]
        
        
        
        # auto guess what are attributes
        for col in table.columns:
            if col.name =='id':
                pass
            elif col.name.endswith('_id'):
                pass
            elif col.name.endswith('_blob'):
                arrayname = col.name.replace('_blob' , '')
                if  ( arrayname+'_shape' in table.columns) and \
                    ( arrayname+'_dtype' in table.columns):
                    if ( arrayname+'_units' in table.columns):
                        genclass.usable_attributes[arrayname] = pq.Quantity
                    else:
                        genclass.usable_attributes[arrayname] = np.ndarray
            elif col.name.endswith('_dtype') or \
                    col.name.endswith('_shape') or\
                    col.name.endswith('_units'):
                pass
                #done in_blob
            else:
                # when metadat.reflect() return the highest level type (Ex: sa.DATETIME and not sa.DateTime)
                # so we must go up in class inheritance
                t = None
                for ptype, satype in python_to_sa_conversion.items():
                    if issubclass(type(col.type), satype):
                        t = ptype
                genclass.usable_attributes[col.name] = t
        generated_classes.append(genclass)


    #  auto guess relationship
    tablename_to_generated_class = { }
    for genclass in generated_classes:
        tablename_to_generated_class[genclass.tablename] = genclass
    
    # many to many relationship
    for k,v in all_many_to_many.items():
        if v not in tablename_to_generated_class[k].many_to_many_relationship:
            tablename_to_generated_class[k].many_to_many_relationship.append(v)
            tablename_to_generated_class[v].many_to_many_relationship.append(k)
    
    # one to many relationship
    for g1 in generated_classes:
        table = metadata.tables[g1.tablename]
        for col in table.columns:
            if col.name.endswith('_id'):
                tablelower = col.name[:-3]
                for g2 in generated_classes:
                    if (tablelower==g2.__name__.lower()) and (g1.__name__ not in g2.one_to_many_relationship) and\
                            (g2.__name__ not in g1.many_to_many_relationship)  :
                        g1.many_to_one_relationship.append(g2.__name__)
                        g2.one_to_many_relationship.append(g1.__name__)
    
    return generated_classes




class NumpyArrayPropertyLoader():
    """ 
    Class to manage property of numpy.ndarray attribute in mapped classes.
    
    :params arraytype: np.ndarray or pq.Quantity
    """
    def __init__(self, name, arraytype = np.ndarray, 
                                    memmap_path = None, min_size_memmap = 2,
                                    compress = False,):
        assert arraytype == np.ndarray or arraytype == pq.Quantity
        self.name = name
        self.arraytype = arraytype
        self.memmap_path = memmap_path
        self.min_size_memmap = min_size_memmap
        self.compress = compress
    
    def fget(self , inst):
        #~ print object_session(inst)
        
        if hasattr(inst, self.name+'_array') :
            return getattr(inst, self.name+'_array')

        if getattr(inst, self.name+'_shape') is None or \
            getattr(inst, self.name+'_dtype') is None:# or \
            #~ getattr(inst, self.name+'_blob') is None:
            return None
        
        if getattr(inst, self.name+'_shape') =='':
            shape = ()
        else:
            shape = tuple([ int(v) for v in getattr(inst, self.name+'_shape').split(',') ])
        
        dt = str(getattr(inst, self.name+'_dtype'))
        compressed = dt.startswith('Z')
        if compressed: dt = dt[1:]
        dt = np.dtype(dt)
        
        do_create_memmap = False
        arr = None
        if self.memmap_path:
            f = self.get_memmap_filename(inst)
            if os.path.exists(f):
                # do not load take from file
                #~ print 'la'
                arr = np.memmap(f, dtype = dt, mode = 'r+', offset = 0,
                                        shape = shape, )
            else:
                # create if array is big
                do_create_memmap = np.prod(shape)>=self.min_size_memmap
                
        if arr is None:
            
            blob = getattr(inst, self.name+'_blob')
            if compressed:
                #~ print 'uncomop'
                #~ blob = zlib.decompress(blob)
                blob = blosc.decompress(blob)
                
            if np.prod(shape)==0:
                if len(blob) != 0:
                    arr = np.frombuffer( blob , dtype = dt)
                else:
                    arr= np.empty( shape, dtype = dt )
            else:
                arr = np.frombuffer( blob , dtype = dt)
                arr.flags.writeable = True
                arr = arr.reshape(shape)
            
            if do_create_memmap:
                arr2 = np.memmap(f, dtype = dt, mode = 'w+', offset = 0,
                                        shape = shape, )
                arr2[:] = arr[:]
                arr = arr2

        if self.arraytype == pq.Quantity:
            arr = pq.Quantity(arr, units = getattr(inst, self.name+'_units'), copy =False)
        
        # next access will be direct
        setattr(inst, self.name+'_array', arr)
        return arr


    def fset(self, inst, value):
        if value is None:
            setattr(inst, self.name+'_shape',    None)
            setattr(inst, self.name+'_dtype',    None)
            setattr(inst, self.name+'_blob',    None)
            if self.arraytype == pq.Quantity:
                setattr(inst, self.name+'_units',    None)
            if hasattr(inst, self.name+'_array') :
                delattr(inst, self.name+'_array')
            return 
        
        if self.arraytype == np.ndarray:
            assert (type(value) == np.ndarray) or (type(value) == np.memmap) , 'Value is not np.array or np.memmap but {}'.format(type(value))
        if self.arraytype == pq.Quantity:
            assert type(value) == pq.Quantity , 'value is not pq.Quantity'
        
        shape = str(value.shape).replace('(','').replace(')','').replace(' ','')
        if shape.endswith(',') : shape = shape[:-1]
        setattr(inst, self.name+'_shape',    shape)
        
        if self.compress:
            setattr(inst, self.name+'_dtype', 'Z'+value.dtype.str)
        else:
            setattr(inst, self.name+'_dtype', value.dtype.str)
        
        
        blob = np.getbuffer(value)
        #~ if self.compress:
            #~ blob = zlib.compress(blob)
        if self.compress:
            blob = blosc.compress(value.tostring(), typesize = value.dtype.itemsize, clevel= 9)


        
        setattr(inst, self.name+'_blob', blob)
        
        if self.arraytype == pq.Quantity:
            setattr(inst, self.name+'_units',    value.dimensionality.string)
        
        setattr(inst, self.name+'_array', value)
    
    def get_memmap_filename(self, inst):
        fname = '{} {} {}'.format(inst.tablename, inst.id, self.name)
        return os.path.join(self.memmap_path, fname)

    
    def fdel(self, inst):
        if hasattr(inst, self.name+'_array') :
            delattr(inst, self.name+'_array') 
        setattr(inst, self.name+'_dtype', None)
        setattr(inst, self.name+'_shape', None)
        setattr(inst, self.name+'_blob', None)



def map_generated_classes(engine, generated_classes, relationship_lazy = 'select', 
                                                memmap_path = None,  compress = False):
    """
    This function map all classes to the db connected with engine.
    
    :param engine: a sqlalchemy Engine.
    
    :param generated_classes: is a list (return by create_classes_from_schema_sniffing) of classes.
        Each class hold some attributes for helping the mapper:
            * genclass.tablename
            * genclass.neoclass
            * genclass.usable_attributes
            * genclass.one_to_many_relationship
            * genclass.many_to_one_relationship
            * genclass.many_to_many_relationship
    
    :param relationship_lazy: sqlalchemy option for relationship (default 'select') 
                            Can be 'select', 'immediate', dynamic'
                            See http://docs.sqlalchemy.org/en/latest/orm/relationships.html?highlight=lazy
    
    :param memmap_path: a path where numpy.array can be memmaped and cached to avoid long reload.
    
    """
    metadata = MetaData(bind = engine)
    metadata.reflect()
    
    # class by tablename
    tablename_to_class = { }
    for genclass in generated_classes:
        tablename_to_class[genclass.tablename] = genclass

    #~ for tablename, genclass in tablename_to_class.items():
    for genclass in generated_classes:
        table = metadata.tables[genclass.tablename]
        for parentname in genclass.many_to_one_relationship :
            table.c[parentname.lower()+'_id'].append_foreign_key( ForeignKey(parentname+'.id') ) 


    for genclass in generated_classes:
    #~ for classname, class_ in generated_classes.items():
        table = metadata.tables[genclass.tablename]
        
        properties = { }
        # deferred loading for numpy or Quantities fields
        for attrname, attrtype in genclass.usable_attributes.items():
            if attrtype == np.ndarray or attrtype == pq.Quantity:
                # FIXME: think about this : _shape defered or not
                #~ properties[attrname+'_shape'] = orm.deferred( table.columns[attrname+'_shape'] , group = attrname)
                #~ properties[attrname+'_dtype'] = orm.deferred( table.columns[attrname+'_dtype'] , group = attrname)
                #properties[attrname+'_blob'] = orm.deferred( table.columns[attrname+'_blob'] , group = attrname)
                properties[attrname+'_blob'] = orm.deferred( table.columns[attrname+'_blob'] , )
                #~ if  attrtype == pq.Quantity:
                    #~ properties[attrname+'_units'] = orm.deferred( table.columns[attrname+'_units'] , group = attrname)
        
        # one to many relationship
        for childname in genclass.one_to_many_relationship:
            properties[childname.lower()+'s'] = orm.relationship(tablename_to_class[childname],
                                                                primaryjoin = table.c.id==metadata.tables[childname].c[table.name.lower()+'_id'],
                                                                #~ order_by = metadata.tables[childname].c['id'],
                                                                #~ order_by = 'name',
                                                                backref=orm.backref(table.name.lower()),
                                                                #FIXME:
                                                                cascade="all, delete",
                                                                #FIXME:
                                                                lazy = relationship_lazy,
                                                                )
        
        for tablename2 in genclass.many_to_many_relationship:
            xref = table.name+'XREF'+tablename2
            if xref not in metadata.tables:
                xref = tablename2+'XREF'+table.name
            xreftable =metadata.tables[xref]
            properties[tablename2.lower()+'s'] = orm.relationship(tablename_to_class[tablename2],
                                                                                        primaryjoin = table.c.id==xreftable.c[table.name.lower()+'_id'],
                                                                                        secondary = xreftable,
                                                                                        secondaryjoin = metadata.tables[tablename2].c.id==xreftable.c[tablename2.lower()+'_id'],
                                                                                        lazy = ((relationship_lazy != "immediate") and relationship_lazy) or 'select',
                                                                                        foreign_keys = [xreftable.c[table.name.lower()+'_id'],  xreftable.c[tablename2.lower()+'_id']],
                                                                                        )
            
        orm.mapper(genclass , table , properties = properties , )
    
        # magic reconstruction for  np.ndarray pq.Quantity (pq.Quantity scalar)
        for attrname, attrtype in genclass.usable_attributes.items():
            if attrtype == np.ndarray or attrtype == pq.Quantity:
                np_dyn_load = NumpyArrayPropertyLoader(attrname, arraytype =attrtype, memmap_path = memmap_path, compress = compress)
                setattr(genclass, attrname, property( fget = np_dyn_load.fget,  fset = np_dyn_load.fset, fdel = np_dyn_load.fdel))
        
    return metadata




class  MyBasicCache():
    """Basic cache based of deque"""
    def __init__(self, maxsize = 200):
        self.d = deque()
        self.maxsize = maxsize
        
    def add(self, ob):
        # startegy is basic : each object if presente is remove and then pop on right
        if ob in self.d:
            self.d.remove(ob)
        self.d.append(ob)
        self.clean()
        
    def clean(self):
        #~ print 'cache size', len(self.d)
        while len(self.d) >= self.maxsize:
            self.d.popleft()
        


class EventLoadListennerForCache:
    """
    This is an event listenner for very basic cache system.
    All loaded object are put in a deque to keep a ref on the object to avoid another load.
    """
    def __init__(self, cache = None):
        if cache is None:
            self.cache = MyBasicCache()
        else:
            self.cache = cache
    
    def __call__(self, target, context):
        #~ print 'event_load_for_cache', target.tablename, target.id
        self.cache.add(target)



class DataBaseConnectionInfo(object):
    """
    This is a simple class used when open_db and that have theses attributes :
        * url
        * mapped_classes
        * Session
        * metadata
        * cache
        * memmap_path
    
    """
    def __init__(self, **kargs):
        self.__dict__.update(kargs)


def open_db(url, myglobals = None, suffix_for_class_name = '', use_global_session = True, 
                        object_number_in_cache = None, memmap_path = None, min_size_memmap = 2, compress = True,
                        relationship_lazy = 'select', predefined_classes = None, max_binary_size = MAX_BINARY_SIZE,):
    """
    Hight level function from playing with a database: this function create sqlalchemy engine, inspect database, create classes, map then and create caches.
    
    :param url: url in sqlalchemy style
    :param myglobals: your locals() or globals() dict if you want to put mapped classes directly in your namespace
    :param suffix_for_class_name: you can add a suffix to class name to avoid conflct with neo for instance (AnalogSignal or _AnalogSignal)
    :param use_global_session: True by default. True is convinient for easy script mode there is a global session for all object. Do not do this for multiprocessing or GUI.
    :param object_number_in_cache: default=None. use a basic memory cache with a fixed object length to avoid to reload objects from db each time you need them.
                                                            If None do not cache anything.
    :param memmap_path: default=None. all attributes are np.array like (Quantities, ...) can be cached on the disk in a directory with numpy.memmap system.
                                            If None do not cache memmap array.
                                            If 'auto' the path is in HOME user dir.
    :param min_size_memmap: when use memmap define the minimum size of an array to be cached
    :param compress: do compress with zlib all BLOB for np.array (save disk space and band width)
    :param relationship_lazy: sqlalchemy option for relationship (default 'select') 
                            Can be 'select', 'immediate', dynamic'
                            See http://docs.sqlalchemy.org/en/latest/orm/relationships.html?highlight=lazy
    :param predefined_classes: if None it take the OpenElectrophy.core.oeclasses for creating the schema. You can also provide something else.
    :param max_binary_size: max size for BLOB column depend of engine (SQLite limited to 2Go, MySQL need some configs, ...)
    
    
    :rtype: :py:class:`DataBaseConnectionInfo` object with url, mapped classes, metadata. See 
    
    Usage in script mode:
        >>> url = 'sqlite://mydatabase.sqlite'
        >>> open_db(url, myglobals = globals() )
        >>> 
    
    Advanced usage for GUI or multiprocessing:
        >>> url = 'sqlite://mydatabase.sqlite'
        >>> dbinfo = open_db(url, myglobals =None,  use_global_session = False  )
        >>> session = dbinfo.Session()
        >>> print dbinfo.mapped_classes
    
    
    
    """
    engine = create_engine(url, echo=False, convert_unicode = True)
    
    if predefined_classes is None:
        from OpenElectrophy.core import oeclasses
        predefined_classes = oeclasses
    
    create_or_update_database_schema( engine, predefined_classes, max_binary_size = max_binary_size)
    generated_classes = create_classes_from_schema_sniffing( engine, predefined_classes, 
                                                suffix_for_class_name = suffix_for_class_name,
                                                )
    
    if memmap_path == 'auto':
        memmap_path = './'#TODO

    metadata = map_generated_classes(engine, generated_classes, relationship_lazy = relationship_lazy,
                                    memmap_path = memmap_path, compress = compress )

    if object_number_in_cache:
        cache = MyBasicCache(maxsize = object_number_in_cache)
        l = EventLoadListennerForCache(cache = cache)
        for genclass in generated_classes:
            event.listen(genclass, 'load', l)
    else:
        cache = None
    
    
    if myglobals is not None:
        d = { }
        for genclass in generated_classes:
            d[genclass.__name__] = genclass
        myglobals.update(d)
    
    Session = orm.sessionmaker(bind=metadata.bind , autocommit=False, autoflush=True)
    if use_global_session:
        global globalsesession
        globalsesession = Session()
    
    dbinfo = DataBaseConnectionInfo( url =url,mapped_classes = generated_classes,Session = Session,
                                                metadata = metadata, cache = cache,memmap_path = memmap_path,)
    
    return dbinfo
    

def execute_sql(query ,session = None, column_split = True, 
                                            column_as_numpy = True, **kargs):
    """
    This function is a hight level execute litteral SQL in a session.
    
    :param session: the sqlaclhemy session. If None try globalsession
    
    :param column_split: default True. For traditional SQL execution, the result is given by raw.
                                    In case of True the result is given by column in a tutle.
                                    a, b, c = execute_sql('SELECT table.a, table.b, table.c FROM table')
    
    :param column_as_numpy: defalt True, in case column_split=True the result can be numpy.array
    
    Usage:
        >>> a, b, c = execute_sql('SELECT table.a, table.b, table.c FROM table')
    
    """
    if session is None:
        session = globalsesession
    assert session is not None, 'You must give a session for loading {}'.format(cls.__classname__)
    
    pres = session.execute(query, kargs)
    res = pres.fetchall()
    
    if len(res) == 0:
        if column_split :
            if column_as_numpy:
                res = [ np.array([ ]) for i in pres.keys() ]
            else:
                res = [ [ ] for i in pres.keys() ]
        else:
            res = [ ]
    else:
        if column_split :
            res2 = np.array( res, dtype = object)
            res = [ ]
            for i in range(res2.shape[1]):
                if column_as_numpy:
                    res += [ res2[:,i] ]
                else :
                    res += [ res2[:,i].tolist() ]
    return res

# alias
sql  = execute_sql
