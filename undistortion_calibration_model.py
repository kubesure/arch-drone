# Developed by Sandip Bhowmik
# Python script that uses OpenCV to undistort a video taken by the DJI Tello Drone using the same camera matrix and distortion coefficients obtained during image calibration

import numpy as np
import cv2

camera_matrix = np.load("./data/camera_matrix.npy")
distortion_coefficients = np.load("./data/distortion_coefficients.npy")

input_video_path = "./data/videos/drone_scan_360.mov"

cap = cv2.VideoCapture(input_video_path)

if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

frame_width = int(cap.get(3))
frame_height = int(cap.get(4))

output_video_path = "./data/videos/undistorted_drone_scan_360.mov"
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_video_path, fourcc, 30, (frame_width, frame_height))

while True:
    ret, frame = cap.read()

    if not ret:
        break

    undistorted_frame = cv2.undistort(frame, camera_matrix, distortion_coefficients, None)

    out.write(undistorted_frame)

    cv2.imshow("Undistorted Frame", undistorted_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
out.release()

cv2.destroyAllWindows()
