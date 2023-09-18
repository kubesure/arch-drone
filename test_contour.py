import cv2
import config_loader
from detector import contour
import numpy as np 
import matplotlib.pyplot as plt

#cap = cv2.VideoCapture('./data/videos/scan_wihout_bg_1.mov')
#cap = cv2.VideoCapture('./data/videos/drone_scan_360.mov')
#cap = cv2.VideoCapture('./data/videos/scan_2_rinr_angular_1.mov')
cap = cv2.VideoCapture('./data/videos/scan_2_rings_linear_1.mov')

red_hoop_inner_diameter = 56
yellow_hoop_inner_diameter  = 48

def draw_and_get_centers(contours, frame, color):   
    for contour in contours:     
        cv2.drawContours(frame, [contour], 0, color, 2)
            
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    detector = contour.ContourDector(config_loader.get_configurations())
    ring_data = detector.get_colored_rings(frame)    

    cv2.drawContours(ring_data.red_mask, ring_data.red_contour, -1, (0, 255, 0), 2)
    cv2.drawContours(ring_data.yellow_mask, ring_data.yellow_contour, -1, (0, 255, 0), 2)

    #cv2.imshow("red Hoops", ring_data.red_mask)
    cv2.imshow("yellow Hoops", ring_data.yellow_mask)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
