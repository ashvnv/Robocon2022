# ART
# Robocon 2022

# This file is called by the main program to detect the ball.
# frame captured by the webcam is sent to detect(). This function then returns the x,y coordinates.


import cv2
import numpy as np
import pathlib

#============= include the debug file =================
from debug_run import *


# Load Yolo
net = cv2.dnn.readNet(str(pathlib.Path(__file__).parent.absolute() / "custom-yolov4-tiny-detector_best.weights"),
                      str(pathlib.Path(__file__).parent.absolute() / "custom-yolov4-tiny-detector.cfg"))

# Name custom object
classes = ["Ball"]

layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
colors = np.random.uniform(0, 255, size=(len(classes), 3))

def detect(img, minSize = 0):
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
    empty = []
    number = 0.75 #Confidence
    while boxes == empty and number >0.5: 
    #keep running this loop until any target is found or confidence variable is greater than compared confidence
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

                    # check min detection size
                    #print_t(w*h, minSize)
                    if not(w*h > minSize):
                        print_t("Ball skipped!")
                        continue #skip this object

                    # Rectangle coordinates
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)

                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)
                    
                    #Only one target
                    break_loop = True #target found break all the loops
                    break
                
                else:
                    continue
            if break_loop:
                break
            else:
                continue
        if break_loop:
            break
        else:
            number -= 0.15 #dec confidence variable
    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
    #print(indexes)
    font = cv2.FONT_HERSHEY_PLAIN
    center = [0,0,0,(0,0),(0,0)]
    D = 0
    for i in range(len(boxes)):
        if i in indexes:
            x, y, w, h = boxes[i]

            center = [int((x+x+w)/2),int((y+y+h)/2), D,(x,y),(w,h)]
            cv_rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv_circle(img, (center[0],center[1]), 1,(0, 0, 255), 2)
            cv_putText(img,str(i),(center[0],center[1]-7),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,255,255),2)

    if center[0] == 0 and center[1] == 0:
        return 0 # No object found
    else:
        return center #return the center
