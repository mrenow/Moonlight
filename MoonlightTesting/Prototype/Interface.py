__author__ = 'My Computer'
import sys
import random
import os


from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets

import struct
import math
import inspect
import numpy as np

from MoonlightTesting.Prototype.recording import AudioController





def lino():
    """Returns the current line number in our program."""
    return inspect.currentframe().f_back.f_lineno

class Window(QtWidgets.QMainWindow):
    #Assembles two buttons and a dropdown selector for input device selection.
    def __init__(s):
        super(Window,s).__init__(None)

        s.setGeometry(0,50,1500,800)
        s.setWindowTitle("TEST")
        s.audio = AudioController()
        print("25")

        #tab1
        s.tabs = QtWidgets.QTabWidget(s)
        s.tabs.setGeometry(0,0,1500,800)
        s.main = QtWidgets.QWidget()
        #buttons
        s.btn_record = QtWidgets.QPushButton("Record",s.main)
        s.btn_record.setGeometry(10,700,75,22)
        print("29")
        s.btn_stop = QtWidgets.QPushButton("stop",s.main)
        s.btn_stop.setGeometry(90,700,75,22)
        s.btn_stop.setEnabled(False)
        print("33")
        #dropdown selector
        s.drop_indevice = QtWidgets.QComboBox(s.main)
        s.drop_indevice.setGeometry(1300,700,69,22)
        print("37")
        #adding all input devices to the dropdown selector
        for device in s.audio.input_devices.values():
            s.drop_indevice.addItem(device["name"])

        #adding event handlers to events
        s.btn_record.clicked.connect(s.btn_record_action)
        s.btn_stop.clicked.connect(s.btn_stop_action)
        s.drop_indevice.activated[str].connect(s.drop_indevice_action)
        s.drop_indevice_action()

        s.canvas_time = Monitor(mode = 1)
        s.canvas_time.setGeometry(0,0,1500,600)

        s.canvas_freq = Monitor(mode = 0)
        s.canvas_freq.setGeometry(0,0,1500,600)

        s.tabs.addTab(s.main,"main")
        s.tabs.addTab(s.canvas_time,"time signal")
        s.tabs.addTab(s.canvas_freq,"frequency signal")

        s.eventloop = QtCore.QTimer(s)
        s.eventloop.timeout.connect(s.eventloop_action)
        s.eventloop.start(2)
        #showing the window

        s.show()




    #Event handlers
    def drop_indevice_action(s):
        s.audio.setInput(s.drop_indevice.currentText())
    # update approproate buttons, start recording.
    def btn_record_action(s):
        s.audio.startRecord()
        s.btn_stop.setEnabled(True)
        s.btn_record.setEnabled(False)
        s.drop_indevice.setEnabled(False)
    # update appropriate buttons, make file and save audio to wav
    def btn_stop_action(s):
        s.audio.stopRecord()
        s.btn_stop.setEnabled(False)
        s.btn_record.setEnabled(True)
        s.drop_indevice.setEnabled(True)

        i = 0
        #if file exists, incremement i
        while( ("test"+str(i)+".wav") in os.listdir()):
            i+=1
        s.audio.saveSound("test" + str(i)+".wav")
    #if recording get data from audio stream and draw to monitor
    def eventloop_action(s):
        if(s.audio.recording):
            s.audio.getSound()
            s.canvas_freq.scalez = 3*0.1**10
            s.canvas_time.scalez = 0.1**7
            if(s.audio.lastchunk!=[]):
                data = list(np.fromstring(s.audio.lastchunk,'Int32'))

                s.canvas_freq.setData(list(np.fft.rfft(data)))
                s.canvas_time.setData(data)





#Graphical element which takes in a 2D array of values and outputs a colour map.
class Monitor(QtWidgets.QWidget):
    data = [1,3,4,5]
    data_height = 0
    data_width = 0
    scalez = 1
    mode = 1

    MODES = {"frequency":0,"time":1}
    def __init__(s,parent = None,mode= 0):
        super(Monitor,s).__init__(parent)
        s.resetData()
        s.setGeometry(0,0,100,100)
        s.mode = mode
    def setGeometry(s, *__args):
        super(Monitor,s).setGeometry(*__args)
        s.resetData()
    def resetData(s):
       # s.data = [[0 for _ in range(s.width())] for _ in range(s.height())]
        s.data = [0 for _ in range(s.width())]
        s.update()

    def setData(s,newdata):
        if(type(newdata) == np.ndarray):

            s.data_height = len(newdata)
            s.data_width = len(newdata[0])

            np.reshape(newdata,s.data_height*s.data_width)
            np.require(newdata,np.uint8,'C')
            s.data = newdata



        # for teo dimensional data
        elif(type(newdata) == list or type(newdata) == tuple):
            if(type(newdata[0]) == list or type(newdata[0]) == tuple):
                #check if data is rectangular. return if otherwise.
                for row in newdata:
                    if len(row) != len(newdata[0]):
                        print("Monitor data update failed")
                        return
                #QImage takes a one dimensional list, so the data will need to be formatted as such.
                s.data = []
                for row in newdata:
                    s.data += row
            else:
                #1d list
                s.data = newdata


        s.update()


    def paintEvent(s,e):
        p = QtGui.QPainter()
        p.begin(s)
        s.drawData(p)
        p.end()
    def drawData(s,p):

        #theres gotta be a faster way to do this

        #img = QtGui.QImage(s.data,s.data_width,s.data_height)

        #Plotting 2d array
        if(type(s.data) == list):
            if(type(s.data[0]) == list):
                ylen = len(s.data)
                xlen = len(s.data[0])
                #draws all points on the entire canvas. VERY FREAKING SLOW
                for y in range(s.height()):
                    for x in range(s.width()):
                        p.setPen(QtGui.QColor(0,0,s.scalez*s.data[int(y*ylen/s.height())][int(x*xlen/s.width())]))
                        p.drawPoint(x,y)


            #plotting 1d array
            else:

                xlen = len(s.data)
                #scale data in x direction to fit screen
                div = s.width()/xlen
                p.setPen(QtCore.Qt.blue)
                print(s.mode)
                #draws lines between all data points

                if(s.mode == s.MODES["frequency"]):
                    old = (np.absolute(s.data[0])*s.scalez)**2

                    for i in range(0,xlen-1):
                        new = (np.absolute(s.data[i]) *s.scalez)**2
                        p.drawLine(QtCore.QPoint(int(i*div),s.height()-old),QtCore.QPoint(int((i+1)*div),s.height()-new))
                        old = new
                elif(s.mode == s.MODES["time"]):
                    print("a")
                    old = (s.data[0]*s.scalez)
                    print(s.data[0])
                    for i in range(0,xlen-1):
                        new = (s.data[i]*s.scalez)
                        p.drawLine(QtCore.QPoint(int(i*div),old+s.height()/2),QtCore.QPoint(int((i+1)*div),new+s.height()/2))
                        old = new


if( __name__ == "__main__"):
    app = QtWidgets.QApplication([])
    gui = Window()
    sys.exit(app.exec_())


