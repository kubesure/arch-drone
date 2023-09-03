# Developed by Sandip Bhowmik
# Python script that uses OpenCV to perform DJI Tello Drone's camera calibration

import numpy as np
import cv2

image_folder = "/Users/sandipbhowmik/Study/Arch-Drone/DistortedImages"

pattern_size = (7, 7)


objp = np.zeros((pattern_size[0] * pattern_size[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:pattern_size[0], 0:pattern_size[1]].T.reshape(-1, 2)

obj_points = [] 
img_points = []  

import os

for filename in os.listdir(image_folder):
    if filename.endswith(".jpeg"):
        img_path = os.path.join(image_folder, filename)
        img = cv2.imread(img_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)

        ret, corners = cv2.findChessboardCorners(
                gray, pattern_size, cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE
        )

        if ret:
            obj_points.append(objp)
            img_points.append(corners)
            print(f"Detected {len(corners)} corners in {filename}")
            
            img_with_corners = cv2.drawChessboardCorners(img, pattern_size, corners, ret)
            cv2.imshow('Corners', img_with_corners)
            cv2.waitKey(0)
        else:
            print(f"No corners detected in {filename}")
cv2.destroyAllWindows()

ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(obj_points, img_points, gray.shape[::-1], None, None)

if ret:
    print("Camera matrix:")
    print(mtx)
    print("\nDistortion coefficients:")
    print(dist)
    # print(",".join(map(str, dist.ravel())))
    rms = np.sqrt(np.mean(np.array(ret) ** 2))
    print("\nRMS error:", rms)
else:
    print("Calibration failed!")

np.save("camera_matrix.npy", mtx)
np.save("distortion_coefficients.npy", dist)
