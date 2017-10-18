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

import pyqtgraph as pg

import multiprocessing
import sys
import random
import time

class Window(QtGui.QDialog):
    def __init__(self, pipe, parent=None):
        super(Window, self).__init__(parent)

        self.plotw = pg.PlotWidget()

        self.pipe = pipe
        self._continuousplot = True

        
        #self.toolbar = NavigationToolbar(self.canvas, self)
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

        # set the layout
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.plotw)
        #layout.addWidget(self.toolbar)
        #layout.addWidget(self.canvas)
        layout.addWidget(self.button)
        layout.addWidget(self.checkbox)
        layout.addWidget(self.stopbutton)
        self.setLayout(layout)

        # Set blank data so I can add to it with the plotter
        self.data = []


        self.plotter_pipe, self.gui_pipe = multiprocessing.Pipe()
        self.d = multiprocessing.Process(name='liveishplotting', target=self.contplot,
                                         kwargs = {'pipe'   : self.plotter_pipe,
                                                   'plotter': self.plot})
        self.d.daemon = True
        self.d.start()
    
    def toggle_continuousplot(self):
        # TODO: use pool or pipes for this
        if self._continuousplot == True:
            self.gui_pipe.send('stop')
            self._continuousplot = False
        else:
            self.gui_pipe.send('start')
            self._continuousplot = True

    def contplot(self, pipe, plotter):
        stopped = False
        while True:
            if pipe.poll():
                msg = pipe.recv()
                if msg == 'stop':
                    stopped = True
                if msg == 'start':
                    stopped = False

            if not stopped:
                self.plot()
            time.sleep(1)
        
    def plot(self):
        ''' plot some random stuff '''

        print(self.pipe.poll())
        sys.stdout.flush()

        if self.pipe.poll():
            mesg = self.pipe.recv()
            if mesg == 'Data':
                data = self.pipe.recv()
                self.data = self.data + data
                self.curve = self.plotw.getPlotItem().plot()
                self.curve.setData(self.data)
                

    def stopmeasurement(self):
        self.pipe.send('ExitNow')

    def closeEvent(self, event):
        self.gui_pipe.send('stop')



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
