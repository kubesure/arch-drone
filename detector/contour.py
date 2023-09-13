import cv2
import numpy as np

def pixel_cm_ratio(contour):
    pass

def is_our_hoop(contour, hoop_inner_diameter):
    (x, y), radius = cv2.minEnclosingCircle(contour)
   
    diameter_pixels = radius * 2
    pixel_to_cm_ratio = hoop_inner_diameter / diameter_pixels
    diameter_cm = diameter_pixels * pixel_to_cm_ratio

    tolerance = 2

    if (hoop_inner_diameter - tolerance) <= diameter_cm <= (hoop_inner_diameter + tolerance):
        return True

    return False



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

