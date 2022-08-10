## Authors:
- Bryan Ronad [GitHub](https://github.com/BryanRonad)
- Ashwin Vallaban [GitHub](https://github.com/ashvnv)
---

## This repository contains bot automation files
![](https://img.shields.io/badge/Robot-R1-yellow) ![](https://img.shields.io/badge/Status-STABLE-green)
<br>
![](https://img.shields.io/badge/implementation-Python%203.8-red)
![](https://img.shields.io/badge/object%20detection-YOLO%20%26%20OpenCV-blue)

## Automation task
- Ball on Head shooting

## BOH algo flow
![diagram](https://raw.githubusercontent.com/ashvnv/Robocon2022/main/assets/BOH_aim_flow.png)

#### BALL HIT FLOW
- Hit Ball 1 -> Ball 4 -> Ball 3 -> Ball 2
- **MANV STATES (Assuming bot initially points between Ball 2 & 3)**
    - MANV 0: Rotate anticlk | Skip Ball 2 | Hit Ball 1
    - MANV 1: Rotate clk | Skip Ball 2 & 3 | Hit Ball 4
    - MANV 2: Rotate anticlk | Hit Ball 3
    - MANV 3: Rotate anticlk | Hit Ball 2

## tracking.py
- This is the main file which can be ran using python 3 interpreter.
- This file captures the frame from the webcam (webcam source has to be mentioned in this file) and adjusts the frame width and height according to the configurations set in the program. This frame is sent to the detection file mentioned in program. This file also logs the process on the terminal and the displayed frame window according to the debug value set in the debug_run.py file. The detection file is expected to return the detected objects coordinates according to the sent frame. This coordinate is then used by tracking.py to send the commands to arduino to position the bot properly.
- This file also displays the processing time required to detect the object in the frame.

## Mask created in tracking.py for tracking the ball
![diagram](https://raw.githubusercontent.com/ashvnv/Robocon2022/main/assets/ROI_masks.png)


## debug_run.py
- This file is used to control how much logs are displayed by the program.
- Logs can be displayed on terminal window and the frame output on the screen.
- Debug level can be set inside this file which can be used to control the logging.
	- Debug levels
		- 0: run in full debug mode
			- Logs are displayed on terminal window and the frame is displayed on the screen with additional information
		- 1: only print in terminal
			- Logs are only printed on the terminal window. In this mode the output frame window is not shown.
		- 2: discreet running mode
			- Logs are disabled completely.

## yolo_object_detection.py
- This file is used to detect the object. This file is called by tracking.py and a frame is sent. 
- This file loads the weights and cfg files which are used to detect the object on the sent frame.
- This file returns the position of the object to tracking.py file.

---

## serial comm between arduino and linux
- tracking.py file does the processing on frame captured by the webcam.
- Once the target is found, tracking.py sends the command serially to arduino.
- arduino.ino function keeps polling the serial line and once a commands is found, it returns the appropriate value to the code which called the arduino function.
- once the command is received, arduino send ack() back to computer serially. tracking.py waits till it received ack() from arduino.
- If Arduino does not receive any manoeuvre command from the computer for more than 1000ms, it times out and returns error 7.
 
## Orientation pins and state change pins
 - The arduino is used to isolate the pc and main bot controller.
 - The arduino will read the sent command serially and accordingly make it's orientation pins high or low.
 - Total 3 pins are used to show the orientation commands. State change pin will complement it's output whenever the orientation pins changes its states.

#### Orientation pin states and description |bit2|bit1|bit0|
 * 0|0|0 - No command
 * 0|0|1 - Left
 * 0|1|0 - Right
 * 0|1|1 - Angle 1
 * 1|0|0 - Angle 2
 * 1|0|1 - Reserved
 * 1|1|0 - Reserved
 * 1|1|1 - Reserved

## How to use arduino.ino
- Call the start() inside arduino.ino. This is necessary to ack() the old data sent by computer as computer wont process the next frame untill it receives the ack().
- start() will return 'q' once ack is sent. If it returns 'z', it means computer did not send any data serially.
- Once 'q' is received after calling start(), call the readManv(). It will return a code. Codes info is given below. readManv() can be called any number of times. Once tracking work is done, dont call the readManv(). In this way ack() is not sent back and tracking function on the linux is paused. Next time if tracking is needed, call the start() function followed by readManv().

## arduino_MEGA
- This is the base code which will be integrated with the R1 main code. It defines a function which can be called by the main controller for automation.

---

## beta files
- These files have \__beta_ suffix. Beta files have new features or modifications which were ony tested locally and further testing in real environment is required.

## clicking.py
- This file can be used to click pictures and save it for making the dataset

## model_test.py
- This file can be used to test the models. This program does not send any signals to arduino.
