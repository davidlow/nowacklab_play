from PyQt5 import QtCore
from PyQt5 import QtWidgets as QtGui
import pyqtgraph as pg
import random
import sys

class MainWindow(QtGui.QWidget):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        layout = QtGui.QHBoxLayout()
        self.button = QtGui.QPushButton('Start Plotting Left')
        layout.addWidget(self.button)
        self.button.clicked.connect(self.plotter)
        self.button2 = QtGui.QPushButton('Start Plotting Right')
        layout.addWidget(self.button2)
        self.button2.clicked.connect(self.plotter2)
        self.plot = pg.PlotWidget()
        layout.addWidget(self.plot)
        self.plot2 = pg.PlotWidget()
        layout.addWidget(self.plot2)
        self.setLayout(layout)


    def plotter(self):
        self.data =[0]
        self.curve = self.plot.getPlotItem().plot()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updater)
        self.timer.start(0)

    def updater(self):
        self.data.append(self.data[-1]+0.2*(0.5-random.random()) )
        self.curve.setData(self.data)#Downsampling does not help

    def plotter2(self):
        self.data2 =[0]
        self.curve2 = self.plot2.getPlotItem().plot()

        self.timer2 = QtCore.QTimer()
        self.timer2.timeout.connect(self.updater2)
        self.timer2.start(0)

    def updater2(self):
        self.data2.append(self.data2[-1]+0.2*(0.5-random.random()) )
        self.curve2.setData(self.data2) #Downsampling does not help



if __name__ == '__main__':
    app = QtGui.QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
