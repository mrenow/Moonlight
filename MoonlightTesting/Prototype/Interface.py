__author__ = 'My Computer'
from PyQt4 import QtCore
from PyQt4 import QtGui
import sys
import random
import os
import numpy as np

from MoonlightTesting.Prototype.recording import AudioController






class Window(QtGui.QMainWindow):

    #Assembles two buttons and a dropdown selector for input device selection.
    def __init__(s):
        super(Window,s).__init__()

        s.setGeometry(200,200,600,400)
        s.setWindowTitle("TEST")
        s.audio = AudioController()

        #buttons
        s.btn_record = QtGui.QPushButton("Record",s)
        s.btn_record.setGeometry(10,370,75,22)

        s.btn_stop = QtGui.QPushButton("stop",s)
        s.btn_stop.setGeometry(90,370,75,22)
        s.btn_stop.setEnabled(False)

        #dropdown selector
        s.drop_indevice = QtGui.QComboBox(s)
        s.drop_indevice.setGeometry(520,10,69,22)

        #adding all input devices to the dropdown selector
        for device in s.audio.input_devices.values():
            s.drop_indevice.addItem(device["name"])

        #adding event handlers to events
        s.btn_record.clicked.connect(s.btn_record_action)
        s.btn_stop.clicked.connect(s.btn_stop_action)
        s.drop_indevice.activated[str].connect(s.drop_indevice_action)
        s.drop_indevice_action()

        s.canvas = Monitor(s)
        s.canvas.setGeometry(0,0,400,350)

        s.eventloop = QtCore.QTimer(s)
        s.eventloop.timeout.connect(s.eventloop_action)
        s.eventloop.start(200)
        #showing the window


        s.show()



    #Event handlers
    def drop_indevice_action(s):
        s.audio.setInput(s.drop_indevice.currentText())
    def btn_record_action(s):
        s.audio.startRecord()
        s.btn_stop.setEnabled(True)
        s.btn_record.setEnabled(False)
        s.drop_indevice.setEnabled(False)
    def btn_stop_action(s):
        s.audio.stopRecord()
        s.btn_stop.setEnabled(False)
        s.btn_record.setEnabled(True)
        s.drop_indevice.setEnabled(True)
        i = 0
        #if file exists, incremement i
        print(os.listdir())
        while( ("test"+str(i)+".wav") in os.listdir()):
            i+=1
        s.audio.saveSound("test" + str(i)+".wav")
    def eventloop_action(s):
        randomizedarray = [[random.randint(0,255) for _ in range(200)] for _ in range(200)]
        s.canvas.scalez = 1
        s.canvas.setData(randomizedarray)







#Graphical element which takes in a 2D array of values and outputs a colour map.
class Monitor(QtGui.QWidget):
    data = [[]]
    data_height = 0
    data_width = 0
    scalez = 100


    def __init__(s,parent = None):
        super(Monitor,s).__init__(parent)
        s.resetData()
        s.setGeometry(0,0,100,100)

    def setGeometry(s, *__args):
        super(Monitor,s).setGeometry(*__args)
        s.resetData()
    def resetData(s):
        s.data = [[0 for _ in range(s.width())] for _ in range(s.height())]
        s.update()

    def setData(s,newdata):
        if(type(newdata) == np.ndarray):

            s.data_height = len(newdata)
            s.data_width = len(newdata[0])

            np.reshape(newdata,s.data_height*s.data_width)
            np.require(newdata,np.uint8,'C')
            s.data = newdata




        elif(type(newdata) == list):
            #check if data is rectangular. return if otherwise.
            for row in newdata:
                if len(row) != newdata[0]:
                    print("data update failed")
                    return


            #QImage takes a one dimensional list, so the data will need to be formatted as such.
            s.data = []
            for row in newdata:
                s.data += row
        s.update()


    def paintEvent(s,e):
        p = QtGui.QPainter()
        p.begin(s)
        s.drawData(p)
        p.end()
    def drawData(s,p):

        #theres gotta be a faster way to do this

        #img = QtGui.QImage(s.data,s.data_width,s.data_height)



        ylen = len(s.data)
        xlen = len(s.data[0])


        for y in range(s.height()):
            for x in range(s.width()):
                p.setPen(QtGui.QColor(0,0,s.scalez*s.data[int(y*ylen/s.height())][int(x*xlen/s.width())]))
                p.drawPoint(x,y)







app = QtGui.QApplication([])
gui = Window()

sys.exit(app.exec_())


