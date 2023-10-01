import cv2
import numpy as np
from drone_types import RingDataContour
from detector import common


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

        contours_red, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours_yellow, _ = cv2.findContours(yellow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        ##Write filter logic for red and yellow circles 

        for contour in contours_red:
            result_red = common.filter_contour(contour, 600)

        for contour in contours_yellow:
            result_yellow = common.filter_contour(contour, 600)

        ring_data = RingDataContour

        if result_red is not None:
            ring_data.red_mask = frame
            ring_data.red_contour = contours_red
        else:
            ring_data.red_mask = None
            ring_data.red_contour = None

        if result_yellow is not None:
            ring_data.yellow_mask = frame
            ring_data.yellow_contour = contours_yellow
        else:
            ring_data.yellow_mask = None
            ring_data.yellow_contour = None

        return ring_data
