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

    ring_sequence = [
                        [RingColor.RED,RingColor.YELLOW],
                    ]
    detector = contour_edge.get_xyz_rings(ring_sequence)
    
    if result is not None:
        x,y,z,area = result
        print(f"x: {x}, y: {y}, z: {z} area: {area}")
    else:
        #print("No suitable contour found")  
        pass      
            
    cv2.imshow("Hoops", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()  

