#ART
#Robocon 2022

#This file contains functions which are used to debugging, using these functions will slow down the execution
#This file is called implicitly by the main code

#Debug level. 
# 0: run in full debug mode
# 1: only print in terminal
# 2: discreet running mode
debug_mode = 2

###
print('debug_mode: ' + str(debug_mode))


import cv2

#print in terminal
def print_t(*strg):
    if debug_mode < 2:
        temp = ''
        for arg in strg:
            temp+=str(arg)
        print(temp)
    return

##### OpenCV functions #######
#make a line
def cv_line(frame,p,q,r,s):
    if True or debug_mode < 1:
        cv2.line(frame, (p[0],p[1]), (q[0],q[1]), (r[0],r[1],r[2]), s)
    return

#put a text
def cv_putText(frame, orient, a, b, c, d, e):
    if True or debug_mode < 1:
        cv2.putText(frame,orient,(a[0],a[1]),b,c,(d[0],d[1],d[2]),e)
    return

#display the frame
def cv_imshow(win_name,frame):
    if debug_mode < 1:
        cv2.imshow(win_name, frame)
        key = cv2.waitKey(1) & 0xFF
        # if the 'q' key is pressed, stop the loop
        if key == ord("q"):
            # close all windows
            cv2.destroyAllWindows()
            return 1
    return 0


def cv_rectangle(img,a,b,c,d):
    if True or debug_mode < 1:
        cv2.rectangle(img, (a[0], a[1]), (b[0], b[1]), (c[0], c[1], c[2]), d)
    return


def cv_circle(img,a,b,c,d):
    if True or debug_mode < 1:
        cv2.circle(img, (a[0],a[1]), b,(c[0], c[1], c[2]), d)