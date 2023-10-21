import cv2
from detector import edge as ed

# cap = cv2.VideoCapture(0)
# cap = cv2.VideoCapture('./data/videos/drone_scan_360.mov')
cap = cv2.VideoCapture('../data/videos/drone_scan_360.mov')
# cap = cv2.VideoCapture('./data/videos/scan_2_ring_angular_1.mov')
# cap = cv2.VideoCapture('./data/videos/scan_2_ring_angular_1.mov')
# cap = cv2.VideoCapture('./data/videos/scan_2_ring_angular_1.mov')

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    detector = ed.EdgeDetector()
    result = detector.get_x_y_z(frame)

    if result is not None:
        x, y, z, area = result
        print(f"x: {x}, y: {y}, z: {z} area: {area}")
    else:
        # print("No suitable contour found")
        pass

    cv2.imshow("Hoops", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
