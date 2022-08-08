# Agnel Robotics Team
# Robocon 2022

# This file can be used to click pictures for making the dataset

import cv2
import os
import pathlib

# Change the current directory to specified directory. Images will be
# saved here
cwd = pathlib.Path(str(pathlib.Path.cwd()) + "/assets")
os.chdir(cwd)

cam = cv2.VideoCapture(0) #Camera source
img_counter = 1
while True:
    ret, frame = cam.read()
    if not ret:
        print("failed")
        break
    cv2.imshow("cam feed",frame)

    temp_key = cv2.waitKey(0) & 0xFF
    # if the 'q' key is pressed, stop the loop else continue
    if temp_key == ord("q"):
        print("quit!")
        break

    # if the 'c' key is pressed, skip the captured frame and continue the loop
    if temp_key == ord("c"):
        print("skipped!")
        continue

    img_name = "frame_{}.jpg".format(img_counter)   #here var will be the number 1_1 etc
    cv2.imwrite(img_name, frame)
    print("{} written!".format(img_name))
    img_counter +=1 #the var number increaments


cam.release()
cv2.destroyAllWindows()