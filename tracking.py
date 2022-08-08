#! /opt/pyvenv/bin/python

# ART
# Robocon 2022

#This is the main program to be called for IP automation.
#This program calls two other program files defined below
#	1. debug_run.py
#	2. yolo_object_detection.py

COMM_PORT = '/dev/ttyUSB0' # define arduino comm port

ROI_PAD = 10 #Ball will be positioned within this region width
FRAME_RESIZE_WIDTH = 300 #KEEP THIS VALUE SMALL FOR BETTER FPS

ROI_X = (0,0) #ROI IMG LINE FOR X AXIS WITH PADDING
ROI_Y = (0,0) #ROI IMG LINE FOR Y AXIS WITH PADDING 

# import the necessary packages
from imutils.video import VideoStream
import cv2
import imutils
import time
from time import time as tm
import argparse
from importlib import import_module
import numpy as np
import threading
from threading import Thread
from flask import render_template
from turbo_flask import Turbo

#============= include the debug file =================
from debug_run import *

#============== for calling detection algo file =============
filename = "yolo_object_detection"
detect = import_module(filename).detect
print_t("Import: " + filename)

################################# serial comm with Arduino ######################################
# ref https://github.com/PowerBroker2/pySerialTransfer
from pySerialTransfer import pySerialTransfer as txfer

try:
    link = txfer.SerialTransfer(COMM_PORT)
    link.open()
    time.sleep(2) # allow some time for the Arduino to completely reset

except:
    import traceback
    traceback.print_exc()
    
    try:
        link.close()
    except:
        pass

def SerComm(str_):
		#return #remove
		print_t("Sent to controller: ", str_)
		if str_ == 'NULL':
			return
		try:
			###################################################################
			# data to send
			###################################################################
			str_size = link.tx_obj(str_)
			send_size = str_size
			
			###################################################################
			# Transmit all the data to send in a single packet
			###################################################################
			link.send(send_size)
			
			###################################################################
			# Wait for a response and report any errors while receiving packets
			###################################################################
			return #skip ack from arduino
			buff_wait = time.time()
			while not link.available():
				if link.status < 0:
					if link.status == txfer.CRC_ERROR:
						print_t('ERROR: CRC_ERROR')
					elif link.status == txfer.PAYLOAD_ERROR:
						print_t('ERROR: PAYLOAD_ERROR')
					elif link.status == txfer.STOP_BYTE_ERROR:
						print_t('ERROR: STOP_BYTE_ERROR')
					else:
						print_t('ERROR: {}'.format(link.status))
				elif (time.time() - buff_wait) > 0.5:
					print_t('Arduino took too much time to acknowledge!')
					return; #break the loop 
			
			###################################################################
			# Parse response string
			###################################################################
			rec_str_ = link.rx_obj(obj_type=type(str_),
									obj_byte_size=1)

			print_t("Received: " + rec_str_)
			return rec_str_

		except:
			import traceback
			traceback.print_exc()
			
			try:
				link.close()
			except:
				pass

###############################################################################################

#=============================== Init ============================================

center = 0 #ball center coordiantes

global MANV_NUM
MANV_NUM = 0
#This manv assumes Bot unitially points straight between BALL 2 & 3

#MANV_NUM 0 IS ROTATE TO LEFT UNTIL TARGET IS FOUND [HIT BALL 1][SKIP BALL 2]
#MANV_NUM 1 IS ROTATE TO RIGHT UNTIL TARGET IS FOUND [HIT BALL 4][SKIP BALL 2 & 3]
#MANV_NUM 2 IS ROTATE TO LEFT UNTIL TARGET IS FOUND [HIT BALL 3]
#MANV_NUM 3 IS ROTATE TO LEFT UNTIL TARGET IS FOUND [HIT BALL 2]

BALL_HIT_CONFIRM = 0 #if the ball is suddenly out of frame, check 3 consequtive frames
                     # if still no ball is found CONFIRM BALL HIT and move to next manv


def NO_TARGET_MANV(angle=False):
	global MANV_NUM

	#return 'x' #for testing

	if angle: #return the manv angle code
		if MANV_NUM == 0:
			return 'm' # BALL 1 ANGLE CODE
		elif MANV_NUM == 1:
			return 'm' # BALL 4 ANGLE CODE
		elif MANV_NUM == 2:
			return 'n' # BALL 3 ANGLE CODE
		elif MANV_NUM == 3:
			return 'n' # BALL 2 ANGLE CODE


	#--------------- NO TARGET MANV ALGO SET HERE ------------
	if MANV_NUM == 0:
		return 'l' # LEFT PULSE | ROTATE TO LEFT UNTIL TARGET IS FOUND [HIT BALL 1]
	elif MANV_NUM == 1:
		return 'r' # RIGHT PULSE | ROTATE TO RIGHT UNTIL TARGET IS FOUND [HIT BALL 4]
	elif MANV_NUM == 2:
		return 'l' # LEFT PULSE | ROTATE TO RIGHT UNTIL TARGET IS FOUND [HIT BALL 3]
	elif MANV_NUM == 3:
		return 'l' # LEFT PUSLE | ROTATE TO LEFT UNTIL TARGET IS FOUND [HIT BALL 2]
	
	#MANV_NUM = 2 #reset manv
	#return NO_TARGET_MANV(angle)

	#no more manv left
	return 'x' #arduino will discard this and bot will stop


vs = VideoStream(src=2).start() #Define the webcam source here

# allow the camera to warm up
time.sleep(2.0)

# grab the current frame
frame = vs.read()
frame = imutils.resize(frame, width=FRAME_RESIZE_WIDTH)

#get the height of the frame
frame_height, frame_width, temp = frame.shape
print_t('FRAME HEIGHT: ', frame_height, ', FRAME WIDTH: ', frame_width)

#CALCULATE ROI
ROI_X = (int(frame_width/2)-int(ROI_PAD/2),int(frame_width/2)+int(ROI_PAD/2))
ROI_Y = (0,frame_height)
print_t('ROI_X: ', ROI_X, ', ROI_Y: ', ROI_Y)


###############################################
# handle video streaming using flask
# ref: https://pyimagesearch.com/2019/09/02/opencv-stream-video-to-web-browser-html-page/
#	   https://blog.miguelgrinberg.com/post/dynamically-update-your-flask-web-pages-using-turbo-flask

# import the necessary packages
from flask import Response
from flask import Flask

# initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful when multiple browsers/tabs
# are viewing the stream)
outputFrame = None
lock = threading.Lock()
# initialize a flask object
app = Flask(__name__)
# initialize the video stream and allow the camera sensor to
# warmup
#vs = VideoStream(usePiCamera=1).start()

def generate():
	# grab global references to the output frame and lock variables
	global outputFrame, lock
	# loop over frames from the output stream
	while True:
		# wait until the lock is acquired
		with lock:
			# check if the output frame is available, otherwise skip
			# the iteration of the loop
			if outputFrame is None:
				continue
			# encode the frame in JPEG format
			(flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
			# ensure the frame was successfully encoded
			if not flag:
				continue
		# yield the output frame in the byte format
		yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
			bytearray(encodedImage) + b'\r\n')

#Raw video
@app.route("/video_feed")
def video_feed():
	# return the response generated along with the specific media
	# type (mime type)
	return Response(generate(),
		mimetype = "multipart/x-mixed-replace; boundary=frame")

#---------------------------------------
#show info on webpage
import psutil
turbo = Turbo(app)

def update_load():
	with app.app_context():
		while True:
			time.sleep(10)
			batt_percent = int(psutil.sensors_battery().percent)
			turbo.push(turbo.replace(render_template('load.html',batt = batt_percent), 'load'))

webClientThread = threading.Thread(target=update_load)
#Video with other info displayed
@app.route("/info")
def info():
	# return the rendered template
	if not webClientThread.is_alive():
		webClientThread.start()
		print_t("Thread started!")
	return render_template("index.html")

global RESET_MANV, INC_MANV, DEC_MANV
RESET_MANV = False
INC_MANV = False
DEC_MANV = False

#this URL will be called to RESET MANV_NUM to 0
@app.route("/reset")
def reset():
	global RESET_MANV
	# return the rendered template
	with lock:
		RESET_MANV = True
	return render_template("index.html")

#this URL will be called to INCREMENT MANV_NUM state
@app.route("/incmanv")
def incmanv():
	global INC_MANV
	# return the rendered template
	with lock:
		INC_MANV = True
	return render_template("index.html")

#this URL will be called to DECREMENT MANV_NUM state
@app.route("/decmanv")
def decmanv():
	global DEC_MANV
	# return the rendered template
	with lock:
		DEC_MANV = True
	return render_template("index.html")


# construct the argument parser and parse command line arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--ip", type=str, default="0.0.0.0",
	help="ip address of the device")
ap.add_argument("-o", "--port", type=int, default=8000,
	help="ephemeral port number of the server (1024 to 65535)")
args = vars(ap.parse_args())

def fn():
	app.run(host=args["ip"], port=args["port"], debug=False,
		threaded=True, use_reloader=False)

# start the flask app threaded
x = Thread(target=fn)
x.start()

##############################################

def HIDE_MASK(frame):
	#this function masks the regions in the image where the ball cannot be found
	# It helps to prevent multiple detection.
	# If an unwanted object is detected, ESC signal sent from the controller can be
	# used to skip that object and continue the bot manv in the MANV_NUM direction
	#ref: https://pyimagesearch.com/2021/01/19/image-masking-with-opencv/
	
	return frame #to disable this function 
	
	#MASK width and height defined here
	X_PAD = 100
	Y_PAD = 40

	hid_mask = np.zeros(frame.shape[:2], dtype="uint8")

	if NO_TARGET_MANV() == 'l': #left manv
		if center == 0:
			#create default left mask, frame edge till ROI
			#cv2.rectangle(hid_mask, (0, 0), (ROI_X[1] + X_PAD, ROI_Y[1]), 255, -1)
			return frame
		else:
			#create left mask, ball center till ROI
			cv2.rectangle(hid_mask, (center[0] - X_PAD, center[1] - Y_PAD), (ROI_X[1] + X_PAD, center[1] + Y_PAD), 255, -1)

	elif NO_TARGET_MANV() == 'r': #right mask
		if center == 0:
			#create default right mask, frame edge till ROI
			#cv2.rectangle(hid_mask, (ROI_X[0] - X_PAD, ROI_Y[1]), (ROI_X[1] + X_PAD, ROI_Y[1]), 255, -1)
			return frame
		else:
			#create right mask, ball center till ROI
			cv2.rectangle(hid_mask, (ROI_X[0] - X_PAD, center[1] - Y_PAD), (center[0] + X_PAD, center[1] + Y_PAD), 255, -1)
	else:
		return frame
	return cv2.bitwise_and(frame, frame, mask=hid_mask)


#This class defines set of functions and variables which can be used for positioning the 
#	detected ball inside the ROI. Each instance can be curated for different situations.
#	For now only one instance is made and used.
class MockROI:

	#constructor defines default values
	def __init__(self, ROIvalLEFT, ROIvalRIGHT):
		self.mock_ROI_LEFT = ROIvalLEFT
		self.mock_ROI_RIGHT = ROIvalRIGHT
		self.skipFrame = False
		self.skipCount = 0

	#due to delay introduced in processing, bot used to overshoot. In order to prevent that, send
	# micro steps command to arduino. In micro steps, the arduino will make the state pin HIGH for
	# set amount of time and then make it LOW. This causes the main bot to manv in small steps.
	def Calc_MOCK_ROI(self,ROIcenter,frame):
		if self.skipFrame:
			self.skipCount += 1
			if self.skipCount > 2:
				self.skipCount = 0
				self.skipFrame = False
			return 'x'
		
		#draw the mock ROI line in the frame
		cv_line(frame, (self.mock_ROI_LEFT,ROI_Y[0]), (self.mock_ROI_LEFT,ROI_Y[1]), (255, 0, 255), 1)
		cv_line(frame, (self.mock_ROI_RIGHT,ROI_Y[0]), (self.mock_ROI_RIGHT,ROI_Y[1]), (255, 0, 255), 1)

		if ROIcenter[0] <= self.mock_ROI_LEFT and ROIcenter[0] <= ROI_X[0]:
			cv_putText(frame,"LEFT",(30,30),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,255,255),2)
			return 'l'
		elif ROIcenter[0] >= self.mock_ROI_RIGHT and ROIcenter[0] >= ROI_X[1]:
			cv_putText(frame,"RIGHT",(30,30),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,255,255),2)
			return 'r'
			
		#arduino micro steps
		elif ROIcenter[0] >= self.mock_ROI_LEFT and ROIcenter[0] <= ROI_X[0]:
			self.skipFrame = True
			return 'u'
		elif ROIcenter[0] <= self.mock_ROI_RIGHT and ROIcenter[0] >= ROI_X[1]:
			self.skipFrame = True
			return 'v'
		else:
			return 'x'

checkMOCKROI = MockROI(ROI_X[0] - 40,ROI_X[1] + 40) #define here mock ROI region width

# keep looping
while True:
	milliseconds = int(tm() * 1000) #get the processing time

	# grab the current frame
	frame = vs.read()

	# resize the frame, blur it, and convert it to the HSV
	# color space
	frame = imutils.resize(frame, width=FRAME_RESIZE_WIDTH)

	frame = HIDE_MASK(frame)

	#==== call detect function ==========
	center = detect(frame, 200 if MANV_NUM < 2 else 0) 
	#if MANV_NUM < 2, BALL 1 and 4 is only detected as the passed number is the min size of the ball to be detected

	#--- Confirm ball was hit-------
	if BALL_HIT_CONFIRM > 0 and center == 0:
		BALL_HIT_CONFIRM+=1
		if BALL_HIT_CONFIRM > 3: #wait for 3 frames to check if the ball is detectable after shoot
			MANV_NUM+=1 #go to next manv
			BALL_HIT_CONFIRM = 0

		continue #this statement can make the frame stuck for sometime depending on the processing
				 # speed on cpu
	else:
		BALL_HIT_CONFIRM = 0

	#milliseconds = int(tm() * 1000) #uncomment this line to get the serial comm delay with arduino
	#============================== Track towards ROI ====================================
	"""
	THE ALGO FIRST TRACKS THE BALL'S 'Y' COORDINATE, ONCE THE BALL IS INSIDE THE REGION OF INTEREST (FOR Y), THE ALGO
    THEN SWITCHES TO TRACKING THE BALL'S 'X' COORDINATE UNTIL THE BALL IS INSIDE THE REGION OF INTEREST (FOR X). 
	ONCE THE BALL IS INSIDE BOTH X AN Y ROI, THE POSITION IS CONSIDERED TO BE LOCKED. APPROPRIATE COMMANDS CAN BE SENT
	TO THE MECHANISMS FOR TRACKING THE BALL INSIDE THE ROI AND ONCE THE POSITION IS LOCKED, SHOOT PULSE CAN BE 
	SENT TO THE MECHANISM (CODE YET TO BE IMPLEMENTED).

	Y manv is skipped here.
    """
	#X LINE
	cv_line(frame, (ROI_X[0],ROI_Y[0]), (ROI_X[0],ROI_Y[1]), (0, 0, 255), 1)
	cv_line(frame, (ROI_X[1],ROI_Y[0]), (ROI_X[1],ROI_Y[1]), (0, 0, 255), 1)

	if center != 0:	
		#BRING THE OBJECT INSIDE THE ROI
		yline = False
		xline = False
		#Y LINE
		if True or (center[1] > ROI_Y[0] and center[1] < ROI_Y[1]): #skip Up, Down manv
			yline = True

			#X LINE
			#cv_line(frame, (ROI_X[0],ROI_Y[0]), (ROI_X[0],ROI_Y[1]), (0, 0, 255), 1)
			#cv_line(frame, (ROI_X[1],ROI_Y[0]), (ROI_X[1],ROI_Y[1]), (0, 0, 255), 1)

			if center[0] > ROI_X[0] and center[0] < ROI_X[1]:
				xline = True
			
			else:
				SerComm(checkMOCKROI.Calc_MOCK_ROI(center,frame))
		
		else:
			cv_line(frame, (0,ROI_Y[0]), (frame_width,ROI_Y[0]), (0, 0, 255), 1)
			cv_line(frame, (0,ROI_Y[1]), (frame_width,ROI_Y[1]), (0, 0, 255), 1)
			if center[1] < ROI_Y[0]:
				cv_putText(frame,"down",(30,30),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,255,255),2)
				SerComm('d') #DOWN PULSE
			if center[1] > ROI_Y[1]:
				cv_putText(frame,"up",(30,30),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,255,255),2)
				SerComm('u') # UP PULSE

		if yline == True and xline == True:
			#Target locked
			cv_putText(frame,"LOCKED",(30,30),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255),2)
			SerComm(NO_TARGET_MANV(True)) #send angle code
			BALL_HIT_CONFIRM+=1
	else:
		cv_putText(frame,"NO TARGET",(30,30),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255),2)
		SerComm(NO_TARGET_MANV()) #No target manv
		center = 0 #default mask in HIDE_MASK()

    #show the manv state number
	cv_putText(frame,"MANV: " + str(MANV_NUM),(30,50),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,255,0),2)
	# show the frame to our screen
	if cv_imshow("BALL ON HEAD TRACKER", frame) == 1:
		break
	
	#milliseconds = int(tm() * 1000)
	#add frame to network stream
	#if one of the URLs was called, execute the necessary action
	with lock:
		outputFrame = frame.copy()
		if RESET_MANV:
			MANV_NUM = 0
		RESET_MANV = False

		if INC_MANV:
			MANV_NUM+=1
		INC_MANV = False

		if DEC_MANV:
			if not MANV_NUM < 1:
				MANV_NUM-=1
		DEC_MANV = False
	
	print_t("Processing time: ",int(tm() * 1000) - milliseconds," ms")

vs.stop()

# close serial comm with arduino
try:
	link.close()
except:
	pass
