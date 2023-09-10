import cv2
import cv2
import numpy as np
import math

cap = cv2.VideoCapture('./data/videos/drone_scan_360.mov')
cap = cv2.VideoCapture('./data/videos/scan_wihout_bg_1.mov')
#cap = cv2.VideoCapture('./data/videos/scan_2_rinr_angular_1.mov')


fx = 1987.7588924985816
k1 = 0.3683688689823332
k2 = -0.1940751373413739

diameter_red_cms = 56 
diameter_yellow_cms = 48

diameter_red_pixel = diameter_red_cms * k1

area_red_cms = math.pi * (diameter_red_cms / 2)**2
area_red_pixel = area_red_cms * k1**2


def reduce_fov(frame, fov_scale=0.5):
   
    h, w, _ = frame.shape
    
    new_w = int(w * fov_scale)
    new_h = int(h * fov_scale)
    
    left = (w - new_w) // 2
    right = left + new_w
    top = (h - new_h) // 2
    bottom = top + new_h
    
    return frame[top:bottom, left:right]


while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
  
    
    bilateral_filtered_image = cv2.bilateralFilter(frame, 5, 175, 175)
    edge_detected_image = cv2.Canny(bilateral_filtered_image, 75, 200)

    contours, _ = cv2.findContours(edge_detected_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in contours:  
        area = cv2.contourArea(contour)
        if area > 400: 
            if area_red_pixel < area: 
                (x, y), radius = cv2.minEnclosingCircle(contour)
                D_image = 2 * radius
                Z_red = (fx * diameter_red_cms) / D_image
                # Calculate circularity
                perimeter = cv2.arcLength(contour, True)
                if perimeter == 0:  
                    circularity = 0
                else:
                    circularity = 4 * math.pi * area / (perimeter**2)
                    if circularity > 0.4:
                        print(f"Distance: {Z_red} Circularity: {circularity}")
                        cv2.drawContours(frame, [contour],  -1, (255, 0, 0), 2)
                        center_color = (0, 0, 0)  
                        center_radius = 3
                        cv2.circle(frame, (int(x), int(y)), center_radius, center_color, -1) 

               
    cv2.imshow("Hoops", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    
cap.release()
cv2.destroyAllWindows()
