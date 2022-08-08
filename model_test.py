# ART
# ROBOCON 2022
# This program can be used to test the models

FRAME_RESIZE_WIDTH = 1000 #KEEP THIS VALUE SMALL FOR BETTER FPS
#CALCULATED BELOW
ROI_X = (0,0) #ROI IMG LINE FOR X AXIS WITH PADDING
ROI_Y = (0,0) #ROI IMG LINE FOR Y AXIS WITH PADDING 

# import the necessary packages
from cgi import print_arguments
from tkinter import Y
from imutils.video import VideoStream
import cv2
import imutils
import time
from time import time as tm

#============= include the debug file =================
from debug_run import *

#============== for calling detection algo file =============
import numpy as np
import pathlib

# Load Yolo
net = cv2.dnn.readNet(str(pathlib.Path(__file__).parent.absolute() / "custom-yolov4-tiny-detector_best.weights"),
                      str(pathlib.Path(__file__).parent.absolute() / "custom-yolov4-tiny-detector.cfg"))

# Name custom object
classes = ["Ball"]

layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
colors = np.random.uniform(0, 255, size=(len(classes), 3))

def detect(img):
	cv_putText(img,"Model Test",(30,20),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,0,255),2)
	#return [0,0,0]
	height, width, channels = img.shape

	# Detecting objects
	blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
	net.setInput(blob)
	outs = net.forward(output_layers)

	class_ids = []
	break_loop = False
	confidences = []
	boxes = []
	obj_num = [0]
	number = 0.75 #Confidence
	y_plot = 80
	while number >0.5: #keep running this loop until mentioned confidence
		print_t("confidence "+ str(number))
		for out in outs:
			for detection in out:
				scores = detection[5:]
				class_id = np.argmax(scores)
				confidence = scores[class_id]
				if confidence > number:
					# Object detected
					center_x = int(detection[0] * width)
					center_y = int(detection[1] * height)
					w = int(detection[2] * width)
					h = int(detection[3] * height)

					# Rectangle coordinates
					x = int(center_x - w / 2)
					y = int(center_y - h / 2)

					boxes.append([x, y, w, h])
					confidences.append(float(confidence))
					class_ids.append(class_id)
					
					break_loop = False #target found break all the loops
					#break
				
				else:
					continue
			if break_loop:
				break
			else:
				continue
		if break_loop:
			break
		else:
			if len(boxes) > 0 and len(boxes) != obj_num[-1]:
				obj_num.append(len(boxes) - obj_num[-1])
				cv_putText(img,"Confidence: " + str(number) + " | New obj: " + str(obj_num[-1] - obj_num[-2]),(30,y_plot),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,255,255),2)
				y_plot += 20
			number -= 0.15 #dec confidence variable
	#print(obj_num)
	#print(boxes)
	#remove repeated same boxes
	indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
	center = [0,0,0,(0,0),(0,0)]
	D = 0
	for i in range(len(boxes)):
		if i in indexes:
			x, y, w, h = boxes[i]

			#D = distance(img, w) #find the distance
			
			center = [int((x+x+w)/2),int((y+y+h)/2), D,(x,y),(w,h)]
			cv_rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
			cv_circle(img, (center[0],center[1]), 1,(0, 0, 255), 2)
			cv_putText(img,str(i),(center[0],center[1]-7),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,255,255),2)
	cv_putText(img,"Total objects: " + str(len(indexes)),(30,60),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255),2)

	if center[0] == 0 and center[1] == 0:
		return 0 # No object found
	else:
		return center #return the center


#=============================== Init ============================================
vs = VideoStream(src=0).start()

# allow the camera to warm up
time.sleep(2.0)

# grab the current frame
frame = vs.read()
frame = imutils.resize(frame, width=FRAME_RESIZE_WIDTH)

#get the height of the frame
frame_height, frame_width, temp = frame.shape
print_t('FRAME HEIGHT: ', frame_height, ', FRAME WIDTH: ', frame_width)

# keep looping
while True:
	milliseconds = int(tm() * 1000) #get the processing time

	# grab the current frame
	frame = vs.read()

	# resize the frame, blur it, and convert it to the HSV
	# color space
	frame = imutils.resize(frame, width=FRAME_RESIZE_WIDTH)

	#==== call detect function ==========
	center = detect(frame)

	if cv_imshow("BALL ON HEAD TRACKER", frame) == 1:
		break
	
	print_t("Processing time: ",int(tm() * 1000) - milliseconds," ms")

vs.stop()
# close all windows
#cv2.destroyAllWindows()
