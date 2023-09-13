import cv2
import numpy as np

class ContourDector:
    def __init__(self, config):
        self.config = config

    def get_color_frame(self, frame):
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

        contours_red, _ = cv2.findContours(red_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours_yellow, _ = cv2.findContours(yellow_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        return contours_red,contours_yellow

