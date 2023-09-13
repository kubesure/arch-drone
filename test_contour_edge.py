from detector import contour_edge
from drone_types import RingColor 
import cv2
import config_loader 


cap = cv2.VideoCapture('./data/videos/scan_wihout_bg_1.mov')
#cap = cv2.VideoCapture('./data/videos/scan_2_rinr_angular_1.mov')
#cap = cv2.VideoCapture('./data/videos/scan_2_rinr_angular_1.mov')

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    ring_sequence =  [RingColor.RED,RingColor.YELLOW,RingColor.RED,RingColor.YELLOW],               
    result = contour_edge.get_xyz_rings(ring_sequence)
    pass      
            
    cv2.imshow("Hoops", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()  

