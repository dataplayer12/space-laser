import cv2
import serial
import numpy as np
import time

ser=serial.Serial('/dev/cu.HC-05-DevB-1',9600)

src=cv2.VideoCapture('welcome.MOV')

ret,frame=src.read()
count=1
nframes=src.get(cv2.CAP_PROP_FRAME_COUNT)

def send_frame(frame):
	gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
	x,y=gray.shape
	for i in range(x):
		for j in range(y):
			ser.write(gray[i,j])


while ret:
	send_frame(frame)
	print('Sent frame {} of {}'.format(count,nframes))
	ret,frame=src.read()
	count+=ret