from PyQt5 import QtGui
import numpy as np
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
    else:
        data1 = data

    mid = (upper + lower) // 2
    step = (upper - lower-1) // 2
    if (upper == lower):
        if (data1(mid) > data1(mid + 1) and data1(mid) > data1(mid - 1)):
            return upper
        else:
            return -1
    if (data1(mid) < data1(mid + 1)):
        return maxSearch(data1, upper - step, upper)
    if (data1(mid) < data1(mid - 1)):
        return maxSearch(data1, lower, lower + step)
    return mid
def peakDetect(data, scale=0.1 ** 4):
    threshold = 10
    begin = -1
    minimum = 2 ** 32
    peaks = []
    errors = np.ndarray((len(data) // 2 - 2,))

    for i in range(len(data) // 2 - 3):
        # Sum shifted and original waveforms
        error = sum((((data[i + 2:2 * (i + 2)] - data[:i + 2]) * scale) ** 2))

        averror = 100 + error // (i + 2)
        errors[i] = averror
        minimum = min(minimum, averror)

        # get bounds of above threshold
        if (begin == -1 and errors[i] > threshold * minimum):
            begin = i
            # if end of region reached, binary search for peak
        if (begin != -1 and errors[i] < threshold * minimum):
            end = i
            # location of trough
            peak = maxSearch(errors, begin, end)
            peaks.append(peak + 2)
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
                # location of trough
                trough = minSearch(getErrors, begin, end)
                #no trough detected
                if(trough == -1):
                    print("session killed")
                    return []
                troughs.append(trough + 2)
                interval = troughs[-1] // len(troughs)
                begin = interval + troughs[-1]-window//2
                end = interval + troughs[-1]+window//2

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
    frequency = len(troughs)*44100 / troughs[-1]

    if (period > 0):
        new_note = getPitch(frequency)
        if current_note != new_note:
            print(new_note, frequency, period, troughs)
        current_note = new_note
    return frequency


def dominantFreq(data):
    peaks = peakDetect(data)
    tolerance = 2
    interval = peaks[0]

    for i in range(1, len(peaks)):
        if (abs(peaks[i] - peaks[i - 1] - interval) < tolerance):

            # take average of all recently seen intervals
            interval = (peaks[i] - peaks[i - 1] + interval) / 2
        else:
            return [-1]
    return peaks


notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def getPitch(freq):
    MIDC = 261.625565
    scale = 0.05776226505  # natural log twelveth root of 2
    factor = int(np.log(freq / MIDC) / scale)
    # print(factor)

    return notes[factor % 12] + str((factor) // 12 + 4)
