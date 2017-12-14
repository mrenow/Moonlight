from PyQt5 import QtGui


#Contains functions that assist finding frequencies from audio snippets.
class DetectPitch:
    sample_size = 1024
    def autocorrelate(self,data): #list
        #plot average innacuracy

        for i in range(1,len(data)):
            #Sum shifted and original waveforms
            error = 0
            for j in range(len(data)-i):
                error += (data[j]-data[j+i])**2
            averror = error/(len(data)-i)




