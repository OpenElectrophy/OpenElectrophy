 
import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import icons

print dir(icons)
if __name__ == '__main__' :
	app = QApplication(sys.argv)
	
	w = QWidget()
	w.show()
	w.setWindowIcon(QIcon(':/param.png'))
	
	sys.exit(app.exec_())
	
	
