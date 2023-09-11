import cv2
import numpy as np
import math
from calibration import undistort 

class EdgeDector:
    def __init__(self, config):
        self.config = config

    def get_x_y_z(self, frame):
        area_red_cms = math.pi * (self.config['diameter_red_cms'] / 2)**2
        area_red_pixel = area_red_cms * self.config['k1']**2
        KNOWN_RADIUS_RED_CM = 28

        bilateral_filtered_image = cv2.bilateralFilter(frame, 5, 175, 175)
        edge_detected_image = cv2.Canny(bilateral_filtered_image, 75, 200)

        contours, _ = cv2.findContours(edge_detected_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:  
            area = cv2.contourArea(contour)
            #eliminate small contours
            if area > 400: 
                #get red circle closest to red circle area in pixel
                if area_red_pixel < area:
                    perimeter = cv2.arcLength(contour, True)
                    if perimeter == 0:  
                        circularity = 0
                    else:
                        circularity = 4 * math.pi * area / (perimeter**2)
                        # Calculate circularity add aspect ratio if possible 
                        if circularity > 0.4:
                            (x, y), radius_pixel = cv2.minEnclosingCircle(contour)
                            #Calculate pixel radius to cms radius can be used to 
                            #Eliminate anything not red and yellow rings in radius
                            scale_cm_per_pixel = KNOWN_RADIUS_RED_CM / radius_pixel
                            actual_radius_cm = radius_pixel * scale_cm_per_pixel  

                            #Diameter in pixel 
                            D_image = 2 * radius_pixel
                            #Calculate distance
                            z = (self.config['fx'] * self.config['diameter_red_cms']) / D_image
                            print(f"Circulaity {circularity} radius {actual_radius_cm} d_image {D_image} x: {y} y: {y} z: {z} area: {area}" )

                            #draw ring contour
                            cv2.drawContours(frame, [contour],  -1, (255, 0, 0), 2)
                            center_color = (0, 0, 0)  
                            center_radius = 3
                            #draw center black circle
                            cv2.circle(frame, (int(x), int(y)), center_radius, center_color, -1)
                            return x,y,z
            else:
                None,None,None

   

