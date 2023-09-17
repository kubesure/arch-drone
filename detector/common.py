import cv2

#eliminate small contours
def filter(contour,size):
    area = cv2.contourArea(contour)

    if area > size: 
        return contour
    return None  