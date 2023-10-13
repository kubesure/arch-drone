import cv2
from detector import contour
from drone_types import RingColor

cap = cv2.VideoCapture('./data/videos/test_run_20231008_155428.mp4')
cl = contour.ContourFilter()

while True:
    _, img = cap.read()
    r, frame = cl.get_xyz_ring(img, RingColor.RED)
    height, width, _ = frame.shape
    print(r.x, r.y, r.z)
    cv2.imshow("Test", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
