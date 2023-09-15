import cv2
import numpy as np
from drone_types import RingDataContour

class ContourDector:
    def __init__(self, config):
        self.config = config

    def get_colored_rings(self, frame):
        red_lower = np.array([0, 120, 70])
        red_upper = np.array([10, 255, 255])
        yellow_lower = np.array([20, 100, 100])
        yellow_upper = np.array([30, 255, 255])
       
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        red_mask = cv2.inRange(hsv, red_lower, red_upper)
        yellow_mask = cv2.inRange(hsv, yellow_lower, yellow_upper)

        kernel = np.ones((5, 5), "uint8")
        red_mask = cv2.dilate(red_mask, kernel)
        yellow_mask = cv2.dilate(yellow_mask, kernel)

        height_red, width_red = red_mask.shape
        height_yellow, width_yellow = yellow_mask.shape

        image_red = np.zeros((height_red, width_red, 3), dtype=np.uint8)
        image_yellow = np.zeros((height_yellow, width_yellow, 3), dtype=np.uint8)

        contours_red, _ = cv2.findContours(red_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours_yellow, _ = cv2.findContours(yellow_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        ##Write filter logic for red and yellow circles 
        
        ring_data = RingDataContour(
            red_mask=image_red, 
            red_contour= contours_red, 
            yellow_mask=image_yellow,
            yellow_contour=contours_yellow)

        return ring_data    
   
        

    

