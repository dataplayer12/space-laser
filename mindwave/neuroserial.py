import serial
from time import sleep
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque
import numpy as np
import queue
import time
import struct
import pdb
import os

class MindWave(object):

    def __init__(self, port=None, baudrate=57600, log=None, file=None):
        self.port = port
        self.baudrate = baudrate
        self.synced = False
        self.bytecount = 0
        self.lastsync = 0
        self.datalist = []
        self.maxplot=100
        self.x_list=np.linspace(self.maxplot,0,num=self.maxplot)
        #self.attentionqueue=queue.Queue(maxsize=self.maxplot)

        if file:
            self.file = open(file, 'r')
            self.data = self.file.read().split('\n')
            print(len(self.data))
        else:
            self.file = None
            self.srl = serial.Serial(self.port, self.baudrate)

        self.attention = None
        self.rawvalue = None
        self.signal = None
        self.bytesreceived = 0

    def readbyte(self):
        #if self.file:
        #    x = self.data[self.bytesreceived]
            # print(x)
        #else:
        x = self.srl.read(1).encode("hex") #.decode("hex")
        if self.file:
            self.file.write(str(x)+'\n')
            #print(x==0xaa, x)
        self.bytesreceived += 1
        return x

    def initgraph(self):
        

        self.plotline.set_data([],[])
        self.fill_lines=self.plotax.fill_between(self.plotline.get_xdata(),50,0)

        return [self.plotline] + [self.fill_lines]

    def updategraph(self):
        if len(self.attentionlist)>self.maxplot:
            #self.attentionlist=self.attentionlist[-self.maxplot:]
            self.attentionlist.pop(0)

        #self.plotline.set_data(self.x_list,self.attentionlist)
        self.plotax.clear()
        self.plotax.plot(self.x_list,self.attentionlist,'r')
        self.fftax.clear()
        self.fftax.plot(self.fft_freq,self.raw_fft,'b')
        self.plotax.set_ylim(-32768, 32768)
        self.fftax.set_ylim(0.,1.)
        #fill_lines=self.plotax.fill_between(self.x_list,0,self.attentionlist, facecolor='cyan', alpha=0.50)
        #if self.bytesreceived%100<10:
        #plt.pause(0.05)
        plt.draw()
        #plt.show()
        plt.pause(0.0001)
        #time.sleep(0.05)
        #return [self.plotline] + [fill_lines]

    def setup_graph(self):
        self.fig = plt.figure()#figsize=(8,4)
        #plt.subplots_adjust(top=0.95, bottom=0.20)
        #self.fig.set_facecolor('#F2F1F0')
        #self.fig.canvas.set_window_title('MindWave Attention')
        self.plotax = plt.subplot2grid((2,2), (0,0), rowspan=1, colspan=2)
        self.fftax = plt.subplot2grid((2,2), (1,0), rowspan=1, colspan=2)
        self.plotline, = self.plotax.plot([],[])
        self.fftline, = self.fftax.plot([],[])
        self.attentionlist=[100]*self.maxplot
        #self.plotax.set_xlim(60, 0)
        self.plotax.set_ylim(-32768, 32768)
        self.plotax.set_title('MindWave Attention')
        self.plotax.set_ylabel('Attention')
        #self.plotax.set_xlabel('Seconds');
        self.plotax.grid(color='gray', linestyle='dotted', linewidth=1)

    def start_new(self,file_handle=None):
        self.file=file_handle
        self.setup_graph()
        self.waitforsync()
        plt.ion()
        plt.show()
        while True:
            # packet synced by 0xaa 0xaa
            try:
                packet_length = int(self.readbyte())
            except ValueError:
                continue
            packet_code = self.readbyte()
            if packet_code == 'd4':
                # standing by
                self.state = "standby"
            elif packet_code == 'd0':
                self.state = "connected"
            elif packet_code == 'd2':
                #data_len = self.readbyte()
                #headset_id = self.readbyte()
                #headset_id += self.readbyte()
                self.dongle_state = "disconnected"
            else:
                left = packet_length - 2
                while left>0:
                    if packet_code=='aa':
                        continue
                    elif packet_code =='80': # raw value
                        #print('Found raw value')
                        row_length = self.readbyte()
                        a = self.readbyte()
                        b = self.readbyte()
                        value = struct.unpack("<h",a[1]+b[1])[0] #is broken #chr(b)+
                        self.rawvalue=value
                        self.attentionlist.append(value)
                        left -= 2
                    elif packet_code == '02': # Poor signal
                        print('Found poor signal')
                        a = self.readbyte()
                        left -= 1
                    elif packet_code == '04': # Attention (eSense)
                        print('Found attention')
                        a = self.readbyte()
                        # if int(a)>0:
                        #     v = struct.unpack("b",chr(a))[0]
                        #     if 0 < v <= 100:
                        #         self.dispatch_data("attention", v)
                        left-=1
                    elif packet_code == '05': # Meditation (eSense)
                        print('Found meditation')
                        #a = yield
                        # if a>0:
                        #     v = struct.unpack("b",chr(a))[0]
                        #     if 0 < v <= 100:
                        #         self.dispatch_data("meditation", v)
                        left-=1
                    elif packet_code == '16': # Blink Strength
                        print('Found blink strength')
                        quit()
                        #self.current_blink_strength = yield
                        left-=1
                    elif packet_code == '83':
                        print('Found unexpected')
                    #     vlength = yield
                    #     self.current_vector = []
                    #     for row in range(8):
                    #         a = yield
                    #         b = yield
                    #         c = yield
                    #         value = a*255*255+b*255+c
                    #     left -= vlength
                    #     self.dispatch_data("bands", self.current_vector)
                    # packet_code = yield
                    else:
                        print('Unknown packet code {}'.format(packet_code))
                        pass # sync failed
            self.updategraph()
            self.waitforsync()


    def start(self,file_handle=None):
        self.file=file_handle
        self.setup_graph()
        #self.initgraph()
        self.waitforsync()
        #self.animation = FuncAnimation(self.fig, self.updategraph, frames=self.maxplot,
        #            init_func=self.initgraph,  interval=20, blit=True)
        plt.ion()
        plt.show()
        while True:
            #print('in while loop')
            b1 = self.readbyte()
            b2 = self.readbyte()
            b3 = self.readbyte()

            if b1 == '04' and b2 == '80' and b3 == '02':
                #self.attention = int(self.readbyte(), 16)
                row_length=int(self.readbyte(), 16)
                a = int(self.readbyte(), 16)
                b = int(self.readbyte(), 16)
                value = struct.unpack("<h",chr(a)+chr(b))[0]

                x = self.readbyte()  # waste two
                x = self.readbyte()  # waste two
                self.attentionlist.append(value)
                self.datalist.append(value)
                raw_fft = np.fft.rfft(np.array(self.datalist))
                fft_amp = np.abs(raw_fft).astype(np.float32)
                self.raw_fft = np.log10(fft_amp)[1:] / np.log10(fft_amp.max())
                self.fft_freq=np.linspace(0,100,self.raw_fft.shape[0])
                self.updategraph()
                #plt.show()
                #print(self.attentionlist)
            else:
                pass
                print('Out of sync at {}'.format(self.bytesreceived))
                self.waitforsync()

    def waitforsync(self):
        while True:
            x1 = self.readbyte()
            x2 = self.readbyte()
            if x1 == 'aa' and x2 == 'aa':
                # if (self.bytesreceived-self.lastsync)==7:
                print('Synced at byte {}'.format(self.bytesreceived))
                break
            elif x2 == 'aa':
                if self.readbyte() == 'aa':
                    break
    def end(self):
        self.srl.close()
        print('Closed MindWave object')


#srl = serial.Serial('/dev/tty.MindWaveMobile-SerialPo', 57600)
# f=open('collected_data.txt','wb')
# n=0

# while True:
#     # if srl.in_waiting:
#     byte=srl.read(1).encode("hex")
#     print(byte)
#     f.write(str(byte)+'\n')
#     n+=1

# f.close()
# srl.close()

try:
    dev = MindWave('/dev/tty.MindWaveMobile-SerialPo', 57600)
    print('Object created')
    #dev=MindWave(file='collected_data.txt')
    #pdb.set_trace()
    #
    txtfile='collected_data{}.txt'.format(len(os.listdir('./'))+1)
    with open(txtfile,'w') as f:
        print('Logging to {}'.format(txtfile))
        dev.start(f)
        #dev.start_new(f)

finally:
    dev.end()