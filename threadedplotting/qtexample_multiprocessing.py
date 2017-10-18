"""
Created on Thu Dec 12 08:38:21 2013

@author: Sukhbinder Singh

Simple QTpy and MatplotLib example with Zoom/Pan

Built on the example provided at
How to embed matplotib in pyqt - for Dummies
http://stackoverflow.com/questions/12459811/how-to-embed-matplotib-in-pyqt-for-dummies

https://sukhbinder.wordpress.com/2013/12/16/simple-pyqt-and-matplotlib-example-with-zoompan/

"""
import sys
from PyQt5 import QtWidgets as QtGui

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

import random


import multiprocessing
import sys

def plotting():
    p = multiprocessing.current_process()
    print('Starting plotting daemon')
    sys.stdout.flush()
    main()
    
def run():
    d = multiprocessing.Process(name='daemon',  target=plotting)
    d.daemon = True



class Window(QtGui.QDialog):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)

        
        self.toolbar = NavigationToolbar(self.canvas, self)
        #self.toolbar.hide()

        # Just some button 
        self.button = QtGui.QPushButton('Plot')
        self.button.clicked.connect(self.plot)

        #self.button1 = QtGui.QPushButton('Zoom')
        #self.button1.clicked.connect(self.zoom)
        
        #self.button2 = QtGui.QPushButton('Pan')
        #self.button2.clicked.connect(self.pan)
        
        #self.button3 = QtGui.QPushButton('Home')
        #self.button3.clicked.connect(self.home)


        # set the layout
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        layout.addWidget(self.button)
        #layout.addWidget(self.button1)
        #layout.addWidget(self.button2)
        #layout.addWidget(self.button3)
        self.setLayout(layout)

#    def home(self):
#        self.toolbar.home()
#    def zoom(self):
#        self.toolbar.zoom()
#    def pan(self):
#        self.toolbar.pan()
        
    def plot(self):
        ''' plot some random stuff '''
        data = [random.random() for i in range(25)]
        ax = self.figure.add_subplot(111)
        ax.hold(False)
        ax.plot(data, '*-')
        self.canvas.draw()

def main():
    app = QtGui.QApplication(sys.argv)

    main = Window()
    main.setWindowTitle('Simple QTpy and MatplotLib example with Zoom/Pan')
    main.show()

    #sys.exit(app.exec_())
    app.exec_()
