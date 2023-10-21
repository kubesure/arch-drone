import cv2
import numpy as np

cap = cv2.VideoCapture('./data/videos/scan_without_bg_1.mov')

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Convert to HSV and apply color mask
    grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Blur the mask
    blurred = cv2.GaussianBlur(grey, (5, 5), 0)

    # Apply Hough Circle Transform
    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, 1, 20, param1=50, param2=30, minRadius=0, maxRadius=0)

    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for (x, y, r) in circles:
            cv2.circle(frame, (x, y), r, (0, 255, 0), 2)

    cv2.imshow("Hoops", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
