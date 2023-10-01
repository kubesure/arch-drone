import numpy as np
import cv2
from drone_types import RingColor, Ring, Direction


class ContourFilter:
    def __init__(self):
        self.boundary = 100
        self.frameWidth = 640
        self.frameHeight = 480
        self.startcounter = 0
        self.dir = 0
        pass

    def empty(self, a):
        pass

    # Get Ring Color Range in Numpy
    def get_ring_hsv(self, ring: RingColor):
        lower = None
        upper = None
        known_width = 0
        if ring == RingColor.RED:
            lower = np.array([0, 100, 70])
            upper = np.array([5, 255, 160])
            known_width = 560
        elif ring == RingColor.YELLOW:
            lower = np.array([20, 100, 100])
            upper = np.array([30, 255, 255])
            known_width = 480
        return lower, upper, known_width

    # Get the filter contour from image
    def get_xyz_ring(self, img, ring: RingColor):

        closure_curve = True
        FOCAL_LENGTH = 42

        lower, upper, known_width = self.get_ring_hsv(ring)
        imgHsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        mask = cv2.inRange(imgHsv, lower, upper)
        result = cv2.bitwise_and(img, img, mask=mask)
        mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

        imgBlur = cv2.GaussianBlur(result, (3, 3), 0, borderType=cv2.BORDER_CONSTANT)
        imgGray = cv2.cvtColor(imgBlur, cv2.COLOR_BGR2GRAY)
        imgCanny = cv2.Canny(imgGray, 166, 175)
        kernel = np.ones((5, 5), "uint8")
        imgDil = cv2.dilate(imgCanny, kernel, iterations=1)

        contours, _ = cv2.findContours(imgDil, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        center_x = 0
        center_y = 0
        distance = 0
        area = 0
        bounding_rect_height = 0
        bounding_rect_width = 0
        direction_to_go = Direction.FORWARD

        for cnt in contours:
            area = cv2.contourArea(cnt)
            areaMin = 0
            if ring == RingColor.RED:
                areaMin = 3500
            elif ring == RingColor.YELLOW:
                areaMin = 1500

            peri = cv2.arcLength(cnt, closure_curve)
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, closure_curve)

            if area > areaMin and len(approx) > 4:
                x, y, bounding_rect_width, bounding_rect_height = cv2.boundingRect(approx)
                center_x = int(x + (bounding_rect_width / 2))  # CENTER X OF THE OBJECT
                center_y = int(y + (bounding_rect_height / 2))  # CENTER y OF THE OBJECT
                distance = self.distance_to_camera(known_width, FOCAL_LENGTH, bounding_rect_width)

                # TODO implement in navigator as detector should do only detection
                '''
                if center_x < int(bounding_rect_width / 2):
                    direction_to_go = Direction.LEFT
                elif center_x > int(bounding_rect_width / 2):
                    direction_to_go = Direction.RIGHT
                elif center_y < int(bounding_rect_height / 2):
                    direction_to_go = Direction.UP
                elif center_y > int(bounding_rect_height / 2):
                    direction_to_go = Direction.DOWN
                '''

                cv2.circle(img, (int(center_x), int(center_y)), 3, (0, 0, 0), -1)
                cv2.rectangle(img, (x, y), (x + bounding_rect_width, y + bounding_rect_height), (0, 255, 0), 5)
                cv2.putText(img, "Area: " + str(int(area)), (x + bounding_rect_width + 20, y + 20),
                            cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(img, "Distance: " + str(int(distance)), (x + bounding_rect_height + 20, y + 45),
                            cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)

        r = Ring(x=center_x, y=center_y, z=distance, area=area, color=ring,bounding_width=bounding_rect_width,
                 bounding_height=bounding_rect_height)
        return r, img

    # compute and return the distance from the maker to the camera
    def distance_to_camera(self, knownWidth, focalLenght, perceivedWidth):
        distance = ((knownWidth * focalLenght) / perceivedWidth) * 2.54
        # print(f"distance {distance}")
        return distance
