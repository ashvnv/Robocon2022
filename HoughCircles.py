# import the necessary packages
import numpy as np
import cv2


#Detect Ball using shape
#Ref:#https://docs.opencv.org/4.x/da/d53/tutorial_py_houghcircles.html 
     #https://www.pyimagesearch.com/2015/09/14/ball-tracking-with-opencv/
"""
MINIMUM RADIUS IS SET FOR FILTERING SMALL UNWANTED OBJECTS
Function returns 0 if not object is found, else returns centre tuple
"""
def detect(frame):
	center = (1000,1000) #used for storing the target's xy value
	targetINFO = (0,0) #for storing target num and radius
	img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Find circles
	circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 1.3, 100)
    #If some circle is found
	if circles is not None:
		# Get the (x, y, r) as integers
		circles = np.round(circles[0, :]).astype("int")
		print(circles)
		# loop over the circles
		for k in range (len(circles)):
			(x,y,r) = circles[k]
			if r > 1:
				if center[1] > y:
					center = (x,y)
					targetINFO = (k,r)
				cv2.circle(frame, (x, y), r, (0, 255, 255), 2)
				cv2.putText(frame,str(k),(x,y-7),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,255,255),2)
		
		if center != (1000,1000):
			cv2.putText(frame,'Target: ' + str(targetINFO[0]),(30,50),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255),2)
			return center
	return 0
