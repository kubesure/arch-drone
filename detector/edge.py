import cv2
import numpy as np
import math

class EdgeDector:
    def __init__(self, config):
        self.config = config

    def get_x_y_z(self, frame):
        #diameter_red_pixel = self.config['diameter_red_cms']  * self.config['k1']
        area_red_cms = math.pi * (self.config['diameter_red_cms'] / 2)**2
        area_red_pixel = area_red_cms * self.config['k1']**2

        bilateral_filtered_image = cv2.bilateralFilter(frame, 5, 175, 175)
        edge_detected_image = cv2.Canny(bilateral_filtered_image, 75, 200)

        contours, _ = cv2.findContours(edge_detected_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:  
            area = cv2.contourArea(contour)
            if area > 400: 
                if area_red_pixel < area: 
                    (x, y), radius = cv2.minEnclosingCircle(contour)
                    D_image = 2 * radius
                    z = (self.config['fx'] * self.config['diameter_red_cms']) / D_image
                    # Calculate circularity
                    perimeter = cv2.arcLength(contour, True)
                    if perimeter == 0:  
                        circularity = 0
                    else:
                        circularity = 4 * math.pi * area / (perimeter**2)
                        if circularity > 0.4:
                            print(f"Distance: {z} Circularity: {circularity}")
                            cv2.drawContours(frame, [contour],  -1, (255, 0, 0), 2)
                            center_color = (0, 0, 0)  
                            center_radius = 3
                            cv2.circle(frame, (int(x), int(y)), center_radius, center_color, -1)
                            return x,y,z
            else:
                None,None,None


   

