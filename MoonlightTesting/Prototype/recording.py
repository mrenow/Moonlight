__author__ = 'My Computer'
import pyaudio
import _thread
import wave
class AudioController:
    CHUNK = 2000
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    lastchunk = []
    recording = False
    INDEX = 2

    p = pyaudio.PyAudio()

    def __init__(s):
        s.registerDevices()

    def registerDevices(s):
        s.input_devices = {}
        s.output_devices = {}
        for i in range(s.p.get_device_count()):
            device = s.p.get_device_info_by_host_api_device_index(0,i)
            if(device["maxOutputChannels"]>0):
                s.output_devices[device["name"]] = device
            if(device["maxInputChannels"]>0):
                s.input_devices[device["name"]] = device
    def setInput(s,name):
        #set input device and reset sound data
        s.sound_input = []
        s.mic = s.input_devices[name]
        s.RATE = s.mic["defaultSampleRate"]
        print(s.mic)
        s.CHANNELS = s.mic["maxInputChannels"]
        s.INDEX = s.mic["index"]
        pass

    #recording will be excecuted in a separate thread
    def startRecord(s):

        s.sound_input = []
        stream = s.p.open(input_device_index = s.INDEX,format = s.FORMAT, channels = s.CHANNELS, rate = int(s.RATE), input = True, frames_per_buffer = s.CHUNK)
        s.recording = True

        #lock to prevent concurrency errors with recording thread
        s.record_lock = True
        _thread.start_new_thread(s.record,(stream,))

    def stopRecord(s):
        s.recording = False
        while(s.record_lock):
           pass
    def getSound(s):
        return s.sound_input

    def saveSound(s,path):
        wf = wave.open(path,'wb')
        wf.setnchannels(s.CHANNELS)
        wf.setsampwidth(s.p.get_sample_size(s.FORMAT))
        wf.setframerate(s.RATE)
        wf.writeframes(b''.join(s.sound_input))
        wf.close()

    def record(s,stream):

        while(s.recording):
            s.lastchunk = stream.read(s.CHUNK)
            s.sound_input.append(s.lastchunk)

        s.record_lock = False




    '''
    pyaudio.Stream(PA_manager=)

    start_stream()
    for i in range(10):

        print(pyaudio.Stream.rea

    pyaudio.Stream.stop_stream()d(10))




    '''