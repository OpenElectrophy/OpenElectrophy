#encoding : utf-8 

"""
This is an alternative to QSettings.
"""



import sys , os
import shutil
import pickle
import user


def get_working_dir(applicationname) :
    if sys.platform.startswith('win'):
        working_dir = os.path.join(os.environ['APPDATA'], applicationname)
    if sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
        working_dir = os.path.join(os.environ['HOME'],'.'+ applicationname+'/')
    if not(os.path.isdir(working_dir)) :
        os.mkdir(working_dir)
    return working_dir


def get_desktop_dir() :
    if sys.platform =='win32' :
        desktop_dir = os.path.join(user.home , 'Desktop')
    if sys.platform[:5] =='linux' :
        desktop_dir = os.path.join(os.environ['HOME'] , 'Desktop')
    if sys.platform== 'darwin' :
        desktop_dir = os.path.join(os.environ['HOME'] , 'Desktop')
    if not(os.path.isdir(desktop_dir)) :
        os.mkdir(desktop_dir)
    return desktop_dir


class PickleSettings:
    """
    Same goal as QSettings but use pickle.
    """
    def __init__(self,applicationname = None,
                    filename = None):
        self.applicationname = applicationname
        if filename is None:
            working_dir = get_working_dir(applicationname)
            filename = os.path.join(working_dir,'pickled_global_application_settings')
        self.filename = filename
        
        if os.path.exists(self.filename) :
            self.load()
        else :
            self.gdict = { }
            self.save()
    
    def getValueOrDefault(self, key, default):
        if key not in self.gdict:
            self.gdict[key]=default
        return self.gdict[key]
    
    def __setitem__(self,key,value):
        self.gdict[key] = value
        self.save()
    
    def __getitem__(self,key):
        if key in self.gdict:
            return self.gdict[key]
        else :
            return None

    def update(self, d):
        self.gdict.update(d)
        self.save()

    def pop(self,key):
        if key in self.gdict:
            v= self.gdict.pop(key)
            self.save()
            return v
        else :
            return None
        
    def load(self) :
        try :
            fid = open(self.filename,'rb')
            self.gdict = pickle.load(fid)
            fid.close()
        except :
            self.gdict = { }
    
    
    def save(self) :
        fid = open(self.filename,'wb')
        pickle.dump(self.gdict,fid)
        fid.close()
