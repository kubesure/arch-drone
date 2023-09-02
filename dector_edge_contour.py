import cv2
import cv2
import numpy as np

cap = cv2.VideoCapture('./data/drone_scan_360.mov')

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    bilateral_filtered_image = cv2.bilateralFilter(frame, 5, 175, 175)
    edge_detected_image = cv2.Canny(bilateral_filtered_image, 75, 200)

    contours, hierarchy = cv2.findContours(edge_detected_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in contours:  
        cv2.drawContours(frame, [contour],  -1, (255,0,0), 2)

    cv2.imshow("Hoops", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    

cap.release()
cv2.destroyAllWindows()


cv2.imshow('Objects Detected',raw_image)
cv2.waitKey(0)