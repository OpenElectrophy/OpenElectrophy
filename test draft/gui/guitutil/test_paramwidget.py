import sys
sys.path.append('../../..')

#TODO


import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *

if __name__ == '__main__' :
    app = QApplication(sys.argv)
    
from numpy import *
    
from OpenElectrophy.gui.guituil.paramwidget import *
#~ from globalapplicationdict import GlobalApplicationDict

import datetime


def test1():
    
    params = [
            ('name' , { 'value' :  'Samuel' , 'type' : unicode  }   ),
            ('age' , { 'value' : 31.5 , 'label' : 'A-G-E' }   ),
            ('age2' , { 'value' : inf , 'label' : 'A-G-E' }   ),
            ('pi' , { 'value' : pi , 'label' : 'A-G-E' }   ),
            ('nbCars' , { 'value' : 2   , 'password' : True}   ),
            ('favorite' , { 'value' :  'one' , 'possible' :[  'one', 'two' , 'tree' ]  }     ),
            ('child' , { 'value' :  1 , 'possible' :[  1,2,3 ]  }     ),
            ('trop fort' , { 'value' :  True }     ),
            
            ('yep' , { 'value' :  None }     ),
            
            ('Rep' , { 'value' :  '~' ,  'widgettype' : ChooseDirWidget }     ),
            ('OneFile' , { 'value' :  '~' ,  'widgettype' : ChooseFileWidget }     ),
            ('ManyFiles' , { 'value' :  '~' ,  'widgettype' : ChooseFilesWidget }     ),
            
            ('Ylim' , { 'value' : [-5,5.] ,  'widgettype' : LimitWidget }     ),
            
            ('double' , { 'value' : 2. , 'widgettype' : QDoubleSpinBox }   ), 
            ('double2' , { 'value' : 2. , 'widgettype' : QDoubleSpinBox  , 'decimals' : 4 , 'singleStep' : .1}   ), 
            
            ('couleur1' , { 'value' : QColor('red'), 'widgettype' : ChooseColorWidget }   ), 
            ('couleur2' , { 'value' : QColor('green') , 'widgettype' : ChooseColorWidget }   ), 
            
            ('multiline' , { 'value' : 'lkjlkj' , 'widgettype' : QTextEdit  , 'type' : unicode}   ), 
            
            #('gains' , { 'value' : [1., 2, 3. ] , 'widgettype' : MultiSpinBox  }   ), 
            
            #~ ('gains2' , { 'value' : range(16) , 'widgettype' : MultiSpinBox  }   ), 
            
            #('range' , { 'value' : [ [-1,1] ]*4 , 'widgettype' : MultiComboBox , 'possible' :  [ [-1,1]  , [-2,2], [-3,3]] }   ), 
            
            ]
    
    #~ pw =ParamWidget(params)
    #~ pw.show()
    
    applicationdict = GlobalApplicationDict('test')
    
    dia = ParamDialog(params , 
                keyformemory = 'nimporte quoi' ,
                applicationdict = applicationdict,
                title = 'Title',
                )
    dia.param_widget.update({'name' : 'SAMUEL'})
    
    dia.param_widget.update({'favorite' : 'two'})
    
    dia.param_widget.update({'Ylim' : [-10,10]})
    
    dia.param_widget.update( {'trop fort' : False})
    
    ok = dia.exec_()
    
    if  ok ==  QDialog.Accepted:
        pw = dia.param_widget
        print 'pi', pi
        for param in params :
            name = param[0]
            
            print name,pw[name] , type(pw[name])
        
        
        
    
    
    sys.exit(app.exec_())
    
def test2():
    
    lw = LimitWidget()
    lw.show()
    sys.exit(app.exec_())
    

def test3():
    
    cw = ChooseColorWidget()
    cw.show()
    sys.exit(app.exec_())
    
    
def test4():
    #~ list_value = [4.456 , 2.5 , 5.6, 2.6 , 5,7.]
    #~ labels = ['lkj' , 'mlk' , 'lkj', 'lkjhlkj', 'lkjklkj' , 'kjhkjh']
    #~ m = MultiSpinBox(list_value= list_value , labels = labels)
    list_value = range(32)
    m = MultiSpinBox(list_value= list_value )
    m.show()
    sys.exit(app.exec_())


def test5():
    #~ list_value = range(30)
    #~ possible = range(30)
    list_value = [ [-1,1] ]*4
    possible = [ [-1,1]  , [-2,2]]
    
    m = MultiComboBox(list_value= list_value , possible = possible)
    m.show()
    sys.exit(app.exec_())


if __name__ == '__main__' :
    test1()
    #~ test2()
    #~ test3()
    #~ test4()
    #~ test5()


