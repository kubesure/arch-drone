import numpy as np
import cv2

import constants
from drone_types import RingColor, Ring


class ContourFilter:
    """
    A class used to filter contours and identify rings based on their color.

    Methods
    -------
    get_ring_hsv(ring: RingColor):
        Returns the HSV color range for the specified ring color.

    get_xyz_ring(img, ring: RingColor):
        Processes the image to identify and locate the specified ring color, returning the ring's position and the processed image.

    distance_to_camera(known_width, focal_length, perceived_width):
        Computes and returns the distance from the camera / drone to the ring.
    """

    def __init__(self):
        """Initialize the ContourFilter class."""
        pass

    def empty(self, a):
        """A placeholder method that does nothing."""
        pass

    def get_ring_hsv(self, ring: RingColor):
        """
        Get the HSV color range for the specified ring color.

        Parameters:
        ring (RingColor): The color of the ring to identify.

        Returns:
        tuple: A tuple containing lists of lower and upper HSV bounds, the known width of the ring, and the number of
        iterations for dilation.
        """
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

    def get_xyz_ring(self, img, ring: RingColor):
        """
        Get the position of the ring in the image.

        Parameters:
        img (numpy.ndarray): The input image.
        ring (RingColor): The color of the ring to identify.

        Returns:
        tuple: A Ring object with the x, y, z coordinates and area, and the processed image with annotations.
        """
        closure_curve = True  # Indicates whether the contour is closed
        focal_length = constants.focal_length_camera  # Focal length of the camera

        # Get HSV color range, known width, and iteration counts for the specified ring color
        lowers, uppers, known_width, iteration = self.get_ring_hsv(ring)

        # Convert the image from BGR to HSV color space
        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        mask = None  # Initialize the mask
        # Create a mask for the specified ring color
        for lower, upper in zip(lowers, uppers):
            if mask is None:
                mask = cv2.inRange(img_hsv, lower, upper)
            else:
                mask = cv2.bitwise_or(mask, cv2.inRange(img_hsv, lower, upper))

        # Apply the mask to the original image
        result = cv2.bitwise_and(img, img, mask=mask)

        # Apply Gaussian Blur to the result
        img_blur = cv2.GaussianBlur(result, (3, 3), 0, borderType=cv2.BORDER_CONSTANT)

        # Convert the blurred image to grayscale
        img_gray = cv2.cvtColor(img_blur, cv2.COLOR_BGR2GRAY)

        # Perform Canny edge detection
        img_canny = cv2.Canny(img_gray, 166, 175)

        # Define a kernel for dilation
        kernel = np.ones((5, 5), dtype=np.uint8)

        # Dilate the edges
        img_dil = cv2.dilate(img_canny, kernel, iterations=iteration)

        # Find contours in the dilated image
        contours, _ = cv2.findContours(img_dil, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        center_x = 0  # Initialize x-coordinate of the ring center
        center_y = 0  # Initialize y-coordinate of the ring center
        distance = 0  # Initialize distance to the ring
        area = 0  # Initialize the area of the ring

        # Iterate through the detected contours
        for cnt in contours:
            area = cv2.contourArea(cnt)  # Calculate the area of the contour
            area_min = 0  # Minimum area threshold
            if ring == RingColor.RED:
                area_min = constants.red_ring_minimum_area_threshold
            elif ring == RingColor.YELLOW:
                area_min = constants.yellow_ring_minimum_area_threshold

            peri = cv2.arcLength(cnt, closure_curve)  # Calculate the perimeter of the contour
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, closure_curve)  # Approximate the contour

            # Filter contours based on area and number of vertices
            if area > area_min and len(approx) > 4:
                x, y, bounding_rect_width, bounding_rect_height = cv2.boundingRect(approx)  # Get bounding rectangle
                center_x = int(x + (bounding_rect_width / 2))  # Calculate the center x-coordinate of the object
                center_y = int(y + (bounding_rect_height / 2))  # Calculate the center y-coordinate of the object
                distance = self.distance_to_camera(known_width, focal_length,
                                                   bounding_rect_width)  # Calculate distance to the camera

                # Draw annotations on the image
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

        # Normalize the x-coordinate for consistency
        center_x = int(center_x / 10)

        # Create a Ring object with the detected attributes
        r = Ring(x=center_x, y=center_y, z=distance, area=area, color=ring)

        return r, img  # Return the Ring object and the annotated image

    def distance_to_camera(self, known_width, focal_length, perceived_width):
        """
        Calculate the distance from the camera to the ring.

        Parameters:
        known_width (float): The known width of the ring.
        focal_length (float): The focal length of the camera.
        perceived_width (float): The perceived width of the ring in the image.

        Returns:
        int: The calculated distance from the camera to the ring.
        """
        distance = ((known_width * focal_length) / perceived_width) * 2.54
        return int(distance)
