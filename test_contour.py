import cv2
from detector import contour
from drone_types import RingColor

cap = cv2.VideoCapture('./data/videos/drone_scan_360.mov')
cl = contour.ContourFilter()

while True:
    _, img = cap.read()
    r, frame = cl.get_xyz_ring(img, RingColor.YELLOW)
    print(r.x, r.y, r.z, r.bounding_height, r.bounding_width)
    cv2.imshow("Test", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
