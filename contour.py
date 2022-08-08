#https://www.authentise.com/post/detecting-circular-shapes-using-contours
import cv2

def detect(frame):
    bilateral_filtered_image = cv2.bilateralFilter(frame, 5, 175, 175)

    edge_detected_image = cv2.Canny(bilateral_filtered_image, 75, 200)

    contours, hierarchy = cv2.findContours(edge_detected_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    contour_list = []
    for contour in contours:
        approx = cv2.approxPolyDP(contour,0.01*cv2.arcLength(contour,True),True)
        area = cv2.contourArea(contour)
        if ((len(approx) > 8) & (len(approx) < 23) & (area > 30) ):
            contour_list.append(contour)
    print(contour_list)

    cv2.drawContours(frame, contour_list,  -1, (255,0,0), 2)
    return 0
