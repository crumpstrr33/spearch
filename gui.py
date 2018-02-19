import sys
from PyQt5 import QtWidgets, QtCore, QtGui

def window():
    app = QtWidgets.QApplication(sys.argv)
    widget = QtWidgets.QWidget()
    widget.setWindowTitle('Shit')
    widget.show()

    sys.exit(app.exec_())

window()