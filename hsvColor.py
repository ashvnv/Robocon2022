# import the necessary packages
import cv2
import imutils

#===========================================================================================================
#Detects ball using colour
#Ref: #https://www.pyimagesearch.com/2015/09/14/ball-tracking-with-opencv/

"""
CODE CAN DETECT OBJECT USING HSV COLOR SPACE. HSV UPPER AND LOWER VALUES CAN BE CALCULATED USING THE RANGE DETECTOR
    SCRIPT: https://github.com/PyImageSearch/imutils/blob/master/bin/range-detector
CODE CAN DETECT MORE THAN 1 OBJECT (NOT EFFICIENT IF MANY OBJECTS ARE DETECTED), UPPER MOST OBJECT IN THE CAM FRAME
    IS ONLY TRACKED.
MINIMUM RADIUS IS SET FOR FILTERING SMALL UNWANTED OBJECTS
Function returns 0 if not object is found, else returns centre tuple
"""
#HSV COLOUR SPACE
HSVLOWER = (0, 19, 122)
HSVUPPER = (33, 132, 239)

def detect(frame):
	#TODO: OPTIMISATION 1
	"""
	AFTER DETECTING THE BALL'S X Y COORDINATE AND KNOWING WHERE THE BALL'S CENTER SHOULD BE NEXT WHILE
	TRYING TO BRING THE BALL INSIDE ROI, MASK OTHER REGIONS IN THE FRAME
	"""
	
	blurred = cv2.GaussianBlur(frame, (11, 11), 0)
	hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

	# construct a mask for the color, then perform
	# a series of dilations and erosions to remove any small
	# blobs left in the mask
	mask = cv2.inRange(hsv, HSVLOWER, HSVUPPER)
	mask = cv2.erode(mask, None, iterations=2)
	mask = cv2.dilate(mask, None, iterations=2)

	# find contours in the mask and initialize the current
	# (x, y) center of the ball
	cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)
	center = (1000,1000) #used for storing the target's xy value
	targetINFO = (0,0) #for storing target num and radius
	# only proceed if at least one contour was found
	if len(cnts) > 0:
		for k in range(len(cnts)):
			# find the largest contour in the mask, then use
			# it to compute the minimum enclosing circle and
			# centroid
			#c = max(cnts, key=cv2.contourArea)
			((x, y), radius) = cv2.minEnclosingCircle(cnts[k])
			M = cv2.moments(cnts[k])
			centerRAW = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

			# only proceed if the radius meets a minimum size
			if radius > 60:
				# draw the circle and centroid on the frame

				cv2.circle(frame, (int(x), int(y)), int(radius),(0, 255, 255), 2)
				cv2.circle(frame, centerRAW, 5, (0, 0, 255), -1)
				#NUMBER THE OBJECTS
				cv2.putText(frame,str(k),(centerRAW[0],centerRAW[1]-7),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,255,255),2)

				if centerRAW[1] < center[1]: #TOP MOST BALL
					center = centerRAW
					targetINFO = (k,radius)
		
		#SHOW THE TARGET OBJECT NUMBER
		if center != (1000,1000):
			cv2.putText(frame,'Target: ' + str(targetINFO[0]),(30,50),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255),2)
			return center
	return 0

