from NeuroPy import NeuroPy
from time import sleep
import serial

neuropy = NeuroPy(port='/dev/tty.MindWaveMobile-SerialPo') 

def attention_callback(attention_value):
    """this function will be called everytime NeuroPy has a new value for attention"""
    print "Value of attention is: ", attention_value
    return None

neuropy.setCallBack("attention", attention_callback)

# neuropy.__srl = serial.Serial(
#                    '/dev/tty.MindWaveMobile-SerialPo', 57600)

#neuropy.__srl.flushInput()

neuropy.start()

print('Sleeping for 10 seconds')

sleep(10)

try:
    while True:
        sleep(1)
finally:
    neuropy.stop()