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
from PyQt5 import QtCore

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

#import pyqtgraph as pg
import matplotlib.pyplot as plt

import multiprocessing
import sys
import random
import time

class Window(QtGui.QDialog):
    def __init__(self, pipe, parent=None):
        super(Window, self).__init__(parent)

        #self.plotw = pg.PlotWidget()
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        ax = self.figure.add_subplot(111)
        ax.plot([0,0],[0,0])
        self.canvas.draw()

        self.measurement_pipe = pipe
        self._continuousplot = True
        self._turnedonplotting = False

        
        self.toolbar = NavigationToolbar(self.canvas, self)
        #self.toolbar = NavigationToolbar()
        #self.toolbar.hide()

        # plot button 
        self.button = QtGui.QPushButton('Plot')
        self.button.clicked.connect(self.plot)

        # continuous plot check box
        self.checkbox = QtGui.QCheckBox('Continuous Plot')
        self.checkbox.setChecked(True)
        self.checkbox.toggled.connect(self.toggle_continuousplot)

        # stop measurement button
        self.stopbutton = QtGui.QPushButton('Stop Measurement')
        self.stopbutton.clicked.connect(self.stopmeasurement)

        # turn on plotting button
        #self.button2 = QtGui.QPushButton('push me now to turn on live plotting')
        #self.button2.clicked.connect(self.turnonplotting)

        # set the layout
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        #layout.addWidget(self.plotw)
        #layout.addWidget(self.toolbar)
        #layout.addWidget(self.canvas)
        layout.addWidget(self.button)
        layout.addWidget(self.checkbox)
        layout.addWidget(self.stopbutton)
        #layout.addWidget(self.button2)
        self.setLayout(layout)

        # Set blank data so I can add to it with the plotter
        self.data = []

        self.plotter_pipe, self.gui_pipe = multiprocessing.Pipe()

        # Setup the worker object and the worker_thread
        self.worker = WorkerObject(self.contplot)
        self.worker_thread = QtCore.QThread()
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.startWork)
        self.worker_thread.start()

        


    def turnonplotting(self):
        if self._turnedonplotting:
            return
        else:
            self._turnedonplotting = True
            self.worker.startWork()

    
    def toggle_continuousplot(self):
        # TODO: use pool or pipes for this
        if self._continuousplot == True:
            self.gui_pipe.send('stop')
            self._continuousplot = False
        else:
            self.gui_pipe.send('start')
            self._continuousplot = True

    def contplot(self):
        stopped = False
        while True:
            if self.plotter_pipe.poll():
                msg = self.plotter_pipe.recv()
                if msg == 'stop':
                    stopped = True
                if msg == 'start':
                    stopped = False

            if not stopped:
                self.plot()
            time.sleep(1)
        
    def plot(self):
        ''' plot some random stuff '''

        print(self.measurement_pipe.poll())
        sys.stdout.flush()

        if self.measurement_pipe.poll():
            mesg = self.measurement_pipe.recv()
            if mesg == 'Data':
                data = self.measurement_pipe.recv()
                self.data = self.data + data
                ax = self.figure.add_subplot(111)
                ax.hold(False)
                ax.plot(self.data, '*-')
                self.canvas.draw()

    def stopmeasurement(self):
        self.measurement_pipe.send('ExitNow')

    def closeEvent(self, event):
        self.stopmeasurement()
        self.gui_pipe.send('stop')

class WorkerObject(QtCore.QObject):

    def __init__(self, func, parent=None):
        super(self.__class__, self).__init__(parent)
        self.func = func

    @QtCore.pyqtSlot()
    def startWork(self):
        self.func()



def procedure(pipe, instr):
    print('startprocedure!')
    sys.stdout.flush()
    p = Procedure(instr, pipe, timeout=1)
    print('running!')
    sys.stdout.flush()
    p.run()


def main():
    # Make or get instruments
    instr = Instr()

    # Make pipe 
    pipe_forprocedure, pipe_forgui = multiprocessing.Pipe()

    # Make measurement process
    p = multiprocessing.Process(name='measurement', 
                                        target=procedure, 
                                        kwargs={'pipe':pipe_forprocedure,
                                                'instr':instr})
    p.daemon=False
    p.start()

    # Create the GUI
    app = QtGui.QApplication(sys.argv)
    main = Window(pipe_forgui)
    main.setWindowTitle('Simple QTpy and MatplotLib example with Zoom/Pan')
    main.show()

    #sys.exit(app.exec_())
    app.exec_()



class Instr():

    def __init__(self):
        self._gain = 1
        pass

    def __repr__(self):
        return 'Instr()'

    def __str__(self):
        return 'Template Instrument'

    @property
    def voltage(self):
        return random.random() * self.gain

    @voltage.setter
    def voltage(self, val):
        pass

    @property
    def gain(self):
        return self._gain

    @gain.setter
    def gain(self, val):
        self._gain = val

class Procedure():

    def __init__(self, instr, guipipe, timeout = 1):
        self.instr = instr
        self.guipipe = guipipe
        self.timeout = timeout

        self.gains = [0,1,2,3,4,5,6,7,8,9]
        self.Vs = []


    def run(self):
        running = True
        print('Starting to run')
        sys.stdout.flush()
        print('gains: ', self.gains)
        sys.stdout.flush()

        for g in self.gains:
            self.instr.gain = g
            V = []
            for v in range(10):
                print(v)
                sys.stdout.flush()
                V.append(self.instr.voltage)
                time.sleep(1)

            self.senddatainpipe(V)
            self.Vs.append(V)

            [mesg,running] = self.mesgfrompipe()

            if mesg == 'ChangeGain!':
                [mesg,_] = self.mesgfrompipe()
                self.gains = mesg

            if not running:
                break

    def senddatainpipe(self, data):
        self.guipipe.send('Data')
        self.guipipe.send(data)
            
    def mesgfrompipe(self):
        running = True
        if self.guipipe.poll(self.timeout):
            mesg = self.guipipe.recv()
            if mesg == 'ExitNow': 
                print('Stopping Measurement due to user input from pipe')
                running=False

            return [mesg, running]
        return [None, running]
