# -*- coding: utf-8 -*-


"""
This benchmark BLOB write in a DB vs HDF5 and direct BLOB on a disk





Conclusion for big arrays 1e8 or 1e9 elements:
  * for small array DO NOT CARE
  * compression lead to better result*
  * blosc is the compressor
  * storing in BLOB in MySQL or SQLite is a bad idea in front of directly in file or in PyTables but not SO ridiculous (between 3x or 5X slower)
  * storing in BLOB in MySQL or SQLite is NOT a idea in front ZIP
  * chunk for BLOB in MySQL is a bit better
  * chunk for BLOB MySQLite is a bit worst
  * with SQL solutions W suffer more than read


"""
import sys
import numpy as np
import os
import time

import io
import zlib
import blosc
nthreads = 8
blosc_comp = 9
blosc.set_nthreads(nthreads)
import tables
import sqlalchemy as sa


sig_size = 1e6
loop = 50

arr = np.random.rand(sig_size).astype('f4')
#~ arr = np.zeros(sig_size)
#~ arr = np.empty(sig_size)
buf = np.getbuffer(arr)

print 'Array :',arr.shape, arr.dtype, ' buffer size',len(buf), len(buf)/1024.**3, 'Go'



def assert_arrays_equal(a, b):
    assert isinstance(a, np.ndarray), "a is a %s" % type(a)
    assert isinstance(b, np.ndarray), "b is a %s" % type(b)
    assert a.shape == b.shape, "%s != %s" % (a,b)
    #assert a.dtype == b.dtype, "%s and %s not same dtype %s %s" % (a, b, a.dtype, b.dtype)
    assert (a.flatten()==b.flatten()).all(), "%s != %s" % (a, b)




class StandartFile():
    filename = 'pure binray {}.raw'
    def setUp(self, ):
        self.clean()
    def tearDw(self,):
        self.clean()
    
    def clean(self, ):
        for i in range(100000):
            f =self.filename.format(i)
            if os.path.exists(f):
                os.remove(f)
    
    def write_one(self, arr, n):
        f = io.open(self.filename.format(n), 'wb')
        f.write(np.getbuffer(arr))
        f.flush()
        f.close()
    
    def read_one(self, n):
        f = io.open(self.filename.format(n), 'rb')
        a = np.frombuffer(f.read(), dtype  = arr.dtype)
        return a
        


class MemMapFile(StandartFile):
    filename = 'memmap bin {}.raw'
    def write_one(self, arr, n):
        arr2 = np.memmap(self.filename.format(n), dtype = arr.dtype, mode = 'w+', offset = 0, shape = arr.shape, )
        arr2[:] = arr
    def read_one(self, n):
        a = np.memmap(self.filename.format(n), dtype = arr.dtype, mode = 'r', offset = 0, shape = arr.shape, )
        return a


class CompressedFileZLib(StandartFile):
    filename = 'compressed zlib binray {}.raw'
    def write_one(self, arr, n):
        f = io.open(self.filename.format(n), 'wb')
        buf = zlib.compress(np.getbuffer(arr), 1)
        f.write(buf)
        f.close()
    def read_one(self, n):
        f = io.open(self.filename.format(n), 'rb')
        a = np.frombuffer(zlib.decompress(f.read()), dtype  = arr.dtype)
        return a


class CompressedFileBlosc(StandartFile):
    filename = 'compressed blosc binray {}.raw'
    def write_one(self, arr, n):
        f = io.open(self.filename.format(n), 'wb')
        buf = blosc.compress(arr.tostring(), typesize = arr.dtype.itemsize, clevel= blosc_comp)
        f.write(buf)
        f.close()
    def read_one(self, n):
        f = io.open(self.filename.format(n), 'rb')
        a = np.frombuffer(blosc.decompress(f.read()), dtype  = arr.dtype)
        return a


class NumpySaveZ(StandartFile):
    name = 'numpy save Z file'
    filename = 'npz {}.npz'
    def write_one(self, arr, n):
        np.savez_compressed(self.filename.format(n), arr)
        #~ np.savez(self.filename.format(n), arr)
    def read_one(self, n):
        a = np.load(self.filename.format(n))['arr_0']
        return a


class AllInOneHDF5:
    filename = 'all in one.h5'
    def setUp(self, ):
        self.clean()
        
    def tearDw(self,):
        self.clean()
    def clean(self, ):
        f =self.filename
        if os.path.exists(f):
            os.remove(f)
    
    def write_one(self, arr, n):
        self.hdf = tables.openFile(self.filename, mode = "a")
        #~ self.hdf.createArray('/', 'array_{}'.format(n), arr)
        
        # CArray
        atom = tables.Atom.from_dtype(arr.dtype)
        a = self.hdf.createCArray('/', 'array_{}'.format(n), atom, arr.shape)
        a[:] = arr[:]
        
        # EArray
        #~ atom = tables.Atom.from_dtype(arr.dtype)
        #~ a = self.hdf.createEArray('/', 'array_{}'.format(n), atom, arr.shape)
        #~ a[:] = arr[:]
        
        #~ self.hdf.createEArray('/', 'array_{}'.format(n), arr)
        
        
        self.hdf.close()
        
    def read_one(self, n):
        self.hdf = tables.openFile(self.filename, mode = "r")
        a = self.hdf.getNode('/', 'array_{}'.format(n)).read()
        self.hdf.close()
        return a


class SqlalchemyBlob:
    compress = False
    def setUp(self, ):
        self.clean()
        self.engine = sa.create_engine(self.url, echo=False)
        metadata = sa.MetaData(bind = self.engine)
        columns = [ sa.Column('id', sa.Integer, primary_key=True, index = True)  ,
                                sa.Column('num', sa.Integer,  index = True)  ,
                                sa.Column('arraybuffer', sa.LargeBinary(length=2**31),)  ,
                            ]
        self.table = sa.Table('onetable', metadata, *columns)
        self.table.create()
        
    def tearDw(self,):
        self.clean()
    
    def clean(self):
        engine = sa.create_engine(self.url, echo=False)
        metadata = sa.MetaData(bind = engine)
        metadata.reflect()
        metadata.drop_all()
    
    def write_one(self, arr, n):
        conn = self.engine.connect()
        if self.compress:
            #~ buf = zlib.compress(np.getbuffer(arr), 1)
            buf = blosc.compress(arr.tostring(), typesize = arr.dtype.itemsize, clevel= blosc_comp)
            #~ print arr.size*arr.dtype.itemsize, len(buf)
        else:
            buf = np.getbuffer(arr)
        ins = self.table.insert().values(arraybuffer = buf, num = n)
        result = conn.execute(ins)
        #~ print result
        #~ print result.inserted_primary_key
        
        #~ print 'yep', n
        
    def read_one(self, n):
        conn = self.engine.connect()
        q = sa.select(columns = [ 'arraybuffer' ], whereclause = 'num = {}'.format(n), from_obj = [self.table ])
        row = conn.execute(q).first()
        arraybuffer = row['arraybuffer']
        if self.compress:
            arraybuffer = blosc.decompress(str(arraybuffer))
        a = np.frombuffer(arraybuffer, dtype  = arr.dtype)
        
        return a
    
    
class SqlalchemyBlobSqlite(SqlalchemyBlob):
    url = 'sqlite:///test_db_1.sqlite'
    def clean(self):
        f = self.url.replace('sqlite:///', '')
        if os.path.exists(f):
            os.remove(f)
        

class SqlalchemyBlobMySQL(SqlalchemyBlob):
    #~ url = 'mysql://test_dev:test_dev@localhost/test_dev_1'
    url = 'mysql://test_dev:test_dev@neuro001.univ-lyon1.fr/test_dev_1'

class SqlalchemyBlobSqliteBlosc(SqlalchemyBlobSqlite):
    url = 'sqlite:///test_db_1.sqlite'
    compress = True

class SqlalchemyBlobMySQLBlosc(SqlalchemyBlobMySQL):
    #~ url = 'mysql://test_dev:test_dev@localhost/test_dev_1'
    url = 'mysql://test_dev:test_dev@neuro001.univ-lyon1.fr/test_dev_1'
    compress = True




class SqlalchemyBlobChunked:
    chunksize = 2**24
    def setUp(self, ):
        self.clean()
        self.engine = sa.create_engine(self.url, echo=False)
        metadata = sa.MetaData(bind = self.engine)
        columns = [ sa.Column('id', sa.Integer, primary_key=True, index = True)  ,
                                sa.Column('num', sa.Integer,  index = True)  ,
                                sa.Column('arrsize', sa.Integer)  ,
                                
                            ]
        self.table = sa.Table('table1', metadata, *columns)
        self.table.create()
        
        columns = [ sa.Column('id', sa.Integer, primary_key=True, index = True)  ,
                                sa.Column('table1_id', sa.Integer,  sa.ForeignKey('table1.id'), index = True,)  ,
                                sa.Column('buffernum', sa.Integer,  index = True)  ,
                                sa.Column('smallbuffer', sa.LargeBinary(length=2**31),)  ,
                            ]
        self.table2 = sa.Table('table2', metadata, *columns)
        self.table2.create()
        
        
    def tearDw(self,):
        self.clean()
    
    def clean(self):
        engine = sa.create_engine(self.url, echo=False)
        metadata = sa.MetaData(bind = engine)
        metadata.reflect()
        metadata.drop_all()
    
    def write_one(self, arr, n):
        conn = self.engine.connect()
        ins = self.table.insert().values(num = n, arrsize = arr.size)
        result = conn.execute(ins)
        table1_id = result.inserted_primary_key[0]
        
        pos = 0
        for buffernum in range(arr.size/self.chunksize+1):
            arr_chunk = arr[pos:pos+self.chunksize]
            smallbuffer = blosc.compress(arr_chunk.tostring(), typesize = arr.dtype.itemsize, clevel= blosc_comp)
            ins = self.table2.insert().values(table1_id = table1_id, buffernum = buffernum, smallbuffer = smallbuffer)
            result = conn.execute(ins)
            pos += self.chunksize
    
    def read_one(self, n):
        conn = self.engine.connect()
        q = sa.select(columns = [ 'id', 'arrsize' ], whereclause = 'table1.num = {}'.format(n), from_obj = [self.table ])
        row = conn.execute(q).first()
        table1_id = row['id']
        
        q = sa.select(columns = [ 'smallbuffer' ], whereclause = 'table2.table1_id = {}'.format(table1_id),
                                        from_obj = [self.table2 ], order_by = ['table2.buffernum'] )
        
        a = np.empty((row['arrsize'],), dtype = arr.dtype)
        pos = 0
        for smallbuffer, in conn.execute(q):
            arr_chunk= np.frombuffer(blosc.decompress(str(smallbuffer)), dtype  = arr.dtype)
            a[pos:pos+arr_chunk.size] = arr_chunk
            pos += arr_chunk.size
        
        return a



class SqlalchemyBlobChunkedSQlite(SqlalchemyBlobChunked):
    url = 'sqlite:///test_db_1.sqlite'

class SqlalchemyBlobChunkedMySQL(SqlalchemyBlobChunked):
    #~ url = 'mysql://test_dev:test_dev@localhost/test_dev_1'
    url = 'mysql://test_dev:test_dev@neuro001.univ-lyon1.fr/test_dev_1'





benchlist = [
                        StandartFile,
                        #~ MemMapFile, 
                        #~ CompressedFileZLib,
                        CompressedFileBlosc ,
                        #~ NumpySaveZ,
                        AllInOneHDF5, 
                        #~ SqlalchemyBlobSqlite,
                        #~ SqlalchemyBlobMySQL, 
                        SqlalchemyBlobSqliteBlosc,
                        SqlalchemyBlobMySQLBlosc,
                        SqlalchemyBlobChunkedSQlite,
                        SqlalchemyBlobChunkedMySQL,
                        
                        ]


for bench in benchlist:
    b = bench()
    print  b.__class__.__name__
    print '----------------------'
    b.setUp()
    t1 = time.time()
    for i in range(loop):
        b.write_one(arr,i)
    t2 = time.time()
    #~ b.tearDw()
    delta = (t2-t1)/loop
    print b.__class__.__name__, 'time for WRITE =',delta, 'rate =',  len(buf)/1024.**2/delta, 'Mo/s'
    
    #test
    arr2 = b.read_one(0)
    try:
        assert_arrays_equal(arr2, arr)
    except:
        print b.__class__.__name__, '######### fail to W/r correctly'
        print
        continue
    
    t1 = time.time()
    for i in range(loop):
        arr2 = b.read_one(0)
    t2 = time.time()
    #~ b.tearDw()
    delta = (t2-t1)/loop
    print b.__class__.__name__, 'time for READ =',delta, 'rate =',  len(buf)/1024.**2/delta, 'Mo/s'
    print
    
    
    
    
    
    
    
