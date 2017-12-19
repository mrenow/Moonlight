from PyQt5 import QtGui
import numpy as np

import inspect
import types
# Contains functions that assist finding frequencies from audio snippets.

current_note = ""

'''def minSearch(data,lower,upper):
    mid = (upper + lower)//2
    if(mid == lower):
        if(data[lower]>data[upper]):
            return upper
        else:
            return lower
    if(data[mid]>data[mid+1]):
        return minSearch(data,mid,upper)
    if(data[mid]<data[mid-1]):
        return minSearch(data,lower,mid)
    return mid
'''

def lino():
    """Returns the current line number in our program."""
    print(inspect.currentframe().f_back.f_lineno)

def minSearch(data, lower, upper):
    if (type(data) == np.ndarray):
        data1 = lambda i: data[i]
    else:
        data1 = data
    mid = (upper + lower)//2
    step = (upper - lower)//2
    if(upper == lower):
        if (data1(mid) < data1(mid + 1) and data1(mid) < data1(mid - 1)):
            return upper
        else:
            return -1
    if (data1(mid) > data1(mid + 1)):
        return minSearch(data1, upper - step, upper)
    if (data1(mid) > data1(mid - 1)):
        return minSearch(data1, lower, lower + step)
    return mid


def maxSearch(data, lower, upper):


    if (type(data) == np.ndarray):
        data1 = lambda i: data[i]
        maxindex = len(data)
    else:
        data1 = data
        maxindex = 2**32

    mid = (upper + lower) // 2
    step = (upper - lower) // 2
    if (upper == lower):
        if (data1(mid) > data1(mid + 1) and data1(mid) > data1(mid - 1)):
            return upper
        else:
            return -1

    if (data1(mid) < data1(min(mid + 1,maxindex))):
        return maxSearch(data1, upper - step, upper)
    if (data1(mid) < data1(max(mid - 1,0))):
        return maxSearch(data1, lower, lower + step)
    return mid
#input is a frequency graph
def peakDetect(data):
    data = np.absolute(data)

    threshold = 100
    begin = -1
    minimum1 = 0
    minimum2 = 0
    divisions = 20
    division = len(data)//divisions
    peaks = {}

    for i in range(len(data)):
        divpos = i//division
        if i%division == 0:
            minimum1 = min(data[division*divpos:division*divpos+division])
        if i%division == division//2:
            minimum2 = min(data[division*divpos+division//2:division*divpos+division//2+division])
        minimum = max(minimum1,minimum2)+1000000
        print("minimum",minimum)
        print("max",max(data))
        # get bounds of above threshold
        if begin == -1 and data[i] > threshold * minimum:
            begin = i
            # if end of region reached, binary search for peak
        if begin != -1 and data[i] < threshold * minimum:
            end = i
            # location of trough
            peak = maxSearch(data, begin, end)
            peaks[data[peak]] = peak
            begin = -1
    return peaks


def troughDetect(data, scale=0.1 ** 4):
    threshold = 0.07
    begin = -1
    end = -1
    extreme = -1
    troughs = []
    errors = np.ndarray((len(data) // 2 - 2,))
    getErrors = lambda i: 10000 + sum(((data[:i + 2] - data[i + 2:2 * (i + 2)]) * scale) ** 2) // (i + 2)
    for i in range(len(data) // 2 - 2):
        # Sum shifted and original waveforms
        errors[i] = getErrors(i)
        extreme = max(extreme, errors[i])
        # get bounds of region below threshold
        if (begin == -1 and errors[i] < threshold * extreme):
            begin = i
            # if end of region reached
        if (begin != -1 and errors[i] > threshold * extreme):
            end = i
            #min checking window
            window = end-begin
            # location of trough
            while end<len(data)//2-2:
                if(errors[i] < threshold * extreme):

                    print("session killed")
                    if(len(troughs)>1):
                       return troughs
                    return []



                # location of trough
                trough = minSearch(getErrors, begin, end)
                #no trough detected
                if(trough == -1):
                    print("session killed")
                    if(len(troughs)>1):
                       return troughs
                    return []
                troughs.append(trough + 2)
                interval = troughs[-1] // len(troughs)
                begin = interval + troughs[-1]-window//2-2
                end = interval + troughs[-1]+window//2-2

            break
    return troughs


def autocorrelate(data):  # 1d ndarray
    global current_note
    troughs= troughDetect(data)

    # check that troughs appear at regular intervals
    if troughs==[]:
        return -1
    tolerance = 2
    period = troughs[0]
    for i in range(1, len(troughs)):
        if (abs(troughs[i] - troughs[i - 1] - period) < tolerance):

            # take average of all recently seen intervals
            period = (troughs[i] - troughs[i - 1] + period) / 2

        else:
            period = -1


    if (period > 0):
        frequency = 44100 /period
        new_note = getPitch(frequency)
        if current_note != new_note:
            print(new_note, frequency, period, troughs)
        current_note = new_note
    else:
        frequency = -1
    return frequency


def dominantFreq(data):
    peaks = peakDetect(data)
    if peaks == {}:
        return -1
    return peaks[max(peaks.keys())]


notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def getPitch(freq):
    MIDC = 261.625565
    scale = 0.05776226505  # natural log twelveth root of 2
    factor = int(np.log(freq / MIDC) / scale)
    # print(factor)

    return notes[factor % 12] + str((factor) // 12 + 4)
