import cv2
import config_loader
from detector import contour 

#cap = cv2.VideoCapture('./data/videos/scan_wihout_bg_1.mov')
#cap = cv2.VideoCapture('./data/videos/drone_scan_360.mov')
#cap = cv2.VideoCapture('./data/videos/scan_2_rinr_angular_1.mov')
cap = cv2.VideoCapture('./data/videos/scan_2_rings_linear_1.mov')

red_hoop_inner_diameter = 56
yellow_hoop_inner_diameter  = 48

def draw_and_get_centers(contours, frame, expected_diameter, color, tolerance=2):   
    for contour in contours:     
        cv2.drawContours(frame, [contour], 0, color, 2)
            
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    detector = contour.ContourDector(config_loader.get_configurations())
    contours_red, contours_yellow = detector.get_color_frame(frame)    
    red_hoop_centers = draw_and_get_centers(contours_red, frame, red_hoop_inner_diameter, (0, 0, 255))
    yellow_hoop_centers = draw_and_get_centers(contours_yellow, frame, yellow_hoop_inner_diameter, (0, 255, 255))

    cv2.imshow("Color Hoops", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
