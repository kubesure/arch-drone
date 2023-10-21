import cv2
import numpy as np
import constants


def un_distort_image(image):
    camera_matrix = np.array([[constants.fx, 0, 948.6125189630379], [0, constants.fy, 948.6125189630379], [0, 0, 1]])
    dist_coeffs = np.array([constants.k1, constants.k2, 0.07210298657979947, 0.028448930285605897, 1.9340687673193722])
    h, w = image.shape[:2]
    new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, dist_coeffs, (w, h), 1, (w, h))

    # Undistort the image
    undistorted_image = cv2.undistort(image, camera_matrix, dist_coeffs, None, new_camera_matrix)

    # Crop the image (optional)
    # x, y, w, h = roi
    # undistorted_image = undistorted_image[y:y+h, x:x+w]
    return undistorted_image
