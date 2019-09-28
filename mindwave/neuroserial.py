import serial
from time import sleep
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque
import numpy as np
import queue
import time

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
        if self.file:
            x = self.data[self.bytesreceived]
            # print(x)
        else:
            x = self.srl.read(1).encode("hex")
            print(x==0xaa, x)
        self.bytesreceived += 1
        return x

    def initgraph(self):
        self.plotax.set_xlim(60, 0)
        self.plotax.set_ylim(-1, 256)
        self.plotax.set_title('MindWave Attention')
        self.plotax.set_ylabel('Attention')
        self.plotax.set_xlabel('Seconds');
        self.plotax.grid(color='gray', linestyle='dotted', linewidth=1)

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
        #fill_lines=self.plotax.fill_between(self.x_list,0,self.attentionlist, facecolor='cyan', alpha=0.50)
        #if self.bytesreceived%100<10:
        #plt.pause(0.05)
        plt.draw()
        #plt.show()
        plt.pause(0.0001)
        #time.sleep(0.05)
        #return [self.plotline] + [fill_lines]

    def setup_graph(self):
        self.fig = plt.figure(figsize=(8,4))
        plt.subplots_adjust(top=0.95, bottom=0.20)
        self.fig.set_facecolor('#F2F1F0')
        self.fig.canvas.set_window_title('MindWave Attention')
        self.plotax = plt.subplot2grid((1,1), (0,0), rowspan=2, colspan=1)
        self.plotline, = self.plotax.plot([],[])
        self.attentionlist=[100]*self.maxplot

    def start(self,plot=False):
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
                self.attention = int(self.readbyte(), 16)
                self.rawvalue = int(self.readbyte(), 16)
                self.signal = int(self.readbyte(), 16)

                x = self.readbyte()  # waste two
                x = self.readbyte()  # waste two
                #print(self.attention, self.rawvalue, self.signal)
                self.attentionlist.append(self.attention)
                self.datalist.append(self.rawvalue)
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
    dev.start(plot=True)
finally:
    dev.end()