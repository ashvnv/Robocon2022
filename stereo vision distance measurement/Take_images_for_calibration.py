###################################
##### Authors:                #####
##### Stephane Vujasinovic    #####
##### Frederic Uhrweiller     ##### 
#####                         #####
##### Creation: 2017          #####
###################################

import numpy as np
import cv2

print('Starting the Calibration. Press and maintain the space bar to exit the script\n')
print('Push (s) to save the image you want and push (c) to see next frame without saving the image')

id_image=0

# termination criteria
criteria =(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# Call the two cameras
CamR= cv2.VideoCapture(0)   # 0 -> Right Camera
CamL= cv2.VideoCapture(2)   # 2 -> Left Camera
#CamL = CamR #for testing in 1 cam

while True:
    retR, frameR= CamR.read()
    retL, frameL= CamL.read()

    ###
    #frameR = cv2.imread("kFM1C.jpg")
    #frameL = frameR
    ###
    #retL, frameL= CamL.read()
    #grayR= cv2.cvtColor(frameR,cv2.COLOR_BGR2GRAY)
    #grayL= cv2.cvtColor(frameL,cv2.COLOR_BGR2GRAY)
    

###
    lwr = np.array([0, 48, 109])
    upr = np.array([200, 148, 254])
    #lwr = np.array([0, 0, 143])
    #upr = np.array([179, 61, 252])
    hsv = cv2.cvtColor(frameR, cv2.COLOR_BGR2HSV)
    msk = cv2.inRange(hsv, lwr, upr)

    # Extract chess-board
    krn = cv2.getStructuringElement(cv2.MORPH_RECT, (50, 30))
    dlt = cv2.dilate(msk, krn, iterations=5)
    res = 255 - cv2.bitwise_and(dlt, msk)

    # Displaying chess-board features
    grayR = np.uint8(res)

#
    lwr = np.array([0, 48, 109])
    upr = np.array([200, 148, 254])
    #lwr = np.array([0, 0, 143])
    #upr = np.array([179, 61, 252])
    hsv = cv2.cvtColor(frameL, cv2.COLOR_BGR2HSV)
    msk = cv2.inRange(hsv, lwr, upr)

    # Extract chess-board
    krn = cv2.getStructuringElement(cv2.MORPH_RECT, (50, 30))
    dlt = cv2.dilate(msk, krn, iterations=5)
    res = 255 - cv2.bitwise_and(dlt, msk)

    # Displaying chess-board features
    grayL = np.uint8(res)
    

    #grayL = grayR

###


    # Find the chess board corners
    retR, cornersR = cv2.findChessboardCorners(grayR,(7,7),None)  # Define the number of chess corners (here 9 by 6) we are looking for with the right Camera
    retL, cornersL = cv2.findChessboardCorners(grayL,(7,7),None)  # Same with the left camera
    cv2.imshow('imgR',grayR)
    cv2.imshow('imgL',grayL)

    # If found, add object points, image points (after refining them)
    if (retR == True) & (retL == True):
        corners2R= cv2.cornerSubPix(grayR,cornersR,(11,11),(-1,-1),criteria)    # Refining the Position
        corners2L= cv2.cornerSubPix(grayL,cornersL,(11,11),(-1,-1),criteria)

        # Draw and display the corners
        cv2.drawChessboardCorners(grayR,(9,6),corners2R,retR)
        cv2.drawChessboardCorners(grayL,(9,6),corners2L,retL)
        cv2.imshow('VideoR',grayR)
        cv2.imshow('VideoL',grayL)

        if cv2.waitKey(0) & 0xFF == ord('s'):   # Push "s" to save the images and "c" if you don't want to
            str_id_image= str(id_image)
            print('Images saved for right and left cameras')
            cv2.imwrite('chessboard-R'+str_id_image+'.png',grayR) # Save the image in the file where this Programm is located
            cv2.imwrite('chessboard-L'+str_id_image+'.png',grayL)
            id_image=id_image+1
        else:
            print('Images not saved')

    # End the Programme
    if cv2.waitKey(1) & 0xFF == ord('q'):   # Push the space bar and maintan to exit this Programm
        break

# Release the Cameras
CamR.release()
CamL.release()
cv2.destroyAllWindows()    
