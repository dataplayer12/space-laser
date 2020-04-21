import cv2
import serial
import numpy as np
import time

ser=serial.Serial('/dev/cu.HC-05-DevB-1',9600)

src=cv2.VideoCapture(0)#cv2.VideoCapture('welcome.MOV')

ret,frame=src.read()
count=1
#nframes=src.get(cv2.CAP_PROP_FRAME_COUNT)
while count<10:
	ret,frame=src.read()
	count+=ret

cv2.namedWindow('Data sent',cv2.WINDOW_NORMAL)

def send_frame(frame):
	gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
	x,y=gray.shape

	for i in range(x):
		for j in range(y):
			ser.write(str(gray[i,j]))
			if ser.out_waiting>250:
				#while ser.out_waiting>200:
				#	pass
				ser.reset_output_buffer()
				#print('Data flushed')
		
		time.sleep(0.25)
		print('Sent row {}, waiting={}'.format(i,ser.out_waiting))
		frame[i,:,:]=127
		cv2.imshow('Data sent',frame)
		k=cv2.waitKey(1)
		if k==32:
			cv2.destroyAllWindows()
			break

try:
	while ret:
		newframe=cv2.resize(frame,(640,360))
		send_frame(newframe)
		print('Sent frame {}'.format(count))
		ret,frame=src.read()
		count+=ret
finally:
	pass
	ser.close()