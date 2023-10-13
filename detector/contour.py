import numpy as np
import cv2
from drone_types import RingColor, Ring


class ContourFilter:

    def __init__(self):
        pass

    def empty(self, a):
        pass

    # Get Ring Color Range in Numpy
    def get_ring_hsv(self, ring: RingColor):
        lower = []
        upper = []
        known_width = 0
        iteration = 0
        if ring == RingColor.RED:
            lower.append(np.array([0, 100, 100], dtype=np.uint8))
            upper.append(np.array([5, 255, 255], dtype=np.uint8))
            lower.append(np.array([175, 100, 100], dtype=np.uint8))
            upper.append(np.array([180, 255, 255], dtype=np.uint8))
            known_width = 560
            iteration = 3
        elif ring == RingColor.YELLOW:
            lower.append(np.array([20, 100, 100], dtype=np.uint8))
            upper.append(np.array([30, 255, 255], dtype=np.uint8))
            known_width = 480
            iteration = 1

        return lower, upper, known_width, iteration

    # compute and return the distance from the maker to the camera

    # Get the filter contour from image
    def get_xyz_ring(self, img, ring: RingColor):

        closure_curve = True
        focal_length = 42

        lowers, uppers, known_width, iteration = self.get_ring_hsv(ring)
        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        mask = None
        for lower, upper in zip(lowers, uppers):
            if mask is None:
                mask = cv2.inRange(img_hsv, lower, upper)
            else:
                mask = cv2.bitwise_or(mask, cv2.inRange(img_hsv, lower, upper))

        result = cv2.bitwise_and(img, img, mask=mask)
        img_blur = cv2.GaussianBlur(result, (3, 3), 0, borderType=cv2.BORDER_CONSTANT)
        img_gray = cv2.cvtColor(img_blur, cv2.COLOR_BGR2GRAY)
        img_canny = cv2.Canny(img_gray, 166, 175)
        kernel = np.ones((5, 5), dtype=np.uint8)
        img_dil = cv2.dilate(img_canny, kernel, iterations=iteration)

        contours, _ = cv2.findContours(img_dil, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        center_x = 0
        center_y = 0
        distance = 0
        area = 0

        for cnt in contours:
            area = cv2.contourArea(cnt)
            area_min = 0
            if ring == RingColor.RED:
                area_min = 12000
            elif ring == RingColor.YELLOW:
                area_min = 7000

            peri = cv2.arcLength(cnt, closure_curve)
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, closure_curve)

            if area > area_min and len(approx) > 4:
                x, y, bounding_rect_width, bounding_rect_height = cv2.boundingRect(approx)
                center_x = int(x + (bounding_rect_width / 2))  # CENTER X OF THE OBJECT
                center_y = int(y + (bounding_rect_height / 2))  # CENTER y OF THE OBJECT
                distance = self.distance_to_camera(known_width, focal_length, bounding_rect_width)

                cv2.circle(img, (int(center_x), int(center_y)), 3, (0, 0, 0), -1)
                cv2.rectangle(img, (x, y), (x + bounding_rect_width, y + bounding_rect_height), (0, 255, 0), 5)
                cv2.putText(img, "A: " + str(int(area)), (x + bounding_rect_width + 20, y + 20),
                            cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(img, "X: " + str(int(center_x)), (x + bounding_rect_width + 20, y + 20),
                            cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(img, "Y: " + str(int(center_y)), (x + bounding_rect_width + 20, y + 20),
                            cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(img, "Z: " + str(int(distance)), (x + bounding_rect_height + 20, y + 45),
                            cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)
        # error should only return of collect in if condition
        center_x = int(center_x / 10)
        r = Ring(x=center_x, y=center_y, z=distance, area=area, color=ring)
        return r, img

    def distance_to_camera(self, known_width, focal_length, perceived_width):
        distance = ((known_width * focal_length) / perceived_width) * 2.54
        return int(distance)
