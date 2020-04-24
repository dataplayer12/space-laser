import cv2
import serial
import numpy as np
import time
import sys

ser=serial.Serial('/dev/cu.HC-05-DevB-2',9600)

def send_frame(ser,frame):
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

def stream_live_video(ser):
	src=cv2.VideoCapture(0)#cv2.VideoCapture('welcome.MOV')
	ret,frame=src.read()
	count=1
	#nframes=src.get(cv2.CAP_PROP_FRAME_COUNT)
	while count<10:
		ret,frame=src.read()
		count+=ret

	cv2.namedWindow('Data sent',cv2.WINDOW_NORMAL)

	try:
		while ret:
			newframe=cv2.resize(frame,(640,360))
			send_frame(ser,newframe)
			print('Sent frame {}'.format(count))
			ret,frame=src.read()
			count+=ret
	finally:
		pass
		cv2.destroyAllWindows()
		ser.close()

def send_string(ser,data,chunksize=128):
	n=0
	front=0
	for x in range(0,len(data),chunksize):
		for i in range(chunksize):
			ser.write(data[n*chunksize+i])
		time.sleep(0.25)
		front=(n+1)*chunksize
		if ser.out_waiting>250: #this depends on bluetooth module
			ser.reset_output_buffer()

	for i in range(len(data)-front):
		ser.write(data[front+i])

	print('Done')


def main():
	nargs=len(sys.argv)
	try:
		if nargs > 1:
			ext=sys.argv[1][sys.argv[1].rfind('.'):]
			if ext in ['jpg','jpeg','png']:
				frame=cv2.imread(sys.argv[1],0)
				send_frame(ser,frame)
			else:
				try:
					with open(sys.argv[1],'rb') as f:
						dataread=str(f.read())
					send_string(ser,dataread)
				except OSError as e:
					print('File not found: {}'.format(str(e)))
				except Exception as e:
					print('An unknown error occured: {}'.format(str(e)))
		else:
			stream_live_video(ser)
	finally:
		ser.close()

if __name__ == '__main__':
	main()