import cv2
import numpy as np

red_lower = np.array([0, 120, 70])
red_upper = np.array([10, 255, 255])
yellow_lower = np.array([20, 100, 100])
yellow_upper = np.array([30, 255, 255])
red_hoop_inner_diameter = 56
yellow_hoop_inner_diameter  = 48

#cap = cv2.VideoCapture('./data/videos/scan_wihout_bg_1.mov')
#cap = cv2.VideoCapture('./data/videos/drone_scan_360.mov')
#cap = cv2.VideoCapture('./data/videos/scan_2_rinr_angular_1.mov')
cap = cv2.VideoCapture('./data/videos/scan_2_rings_linear_1.mov')

camera_matrix = np.load("./data/camera_matrix.npy")
distortion_coefficients = np.load("./data/distortion_coefficients.npy")

def pixel_cm_ratio(contour):
    pass

def is_our_hoop(contour, hoop_inner_diameter):
    (x, y), radius = cv2.minEnclosingCircle(contour)
   
    diameter_pixels = radius * 2
    pixel_to_cm_ratio = hoop_inner_diameter / diameter_pixels
    diameter_cm = diameter_pixels * pixel_to_cm_ratio

    tolerance = 2

    if (hoop_inner_diameter - tolerance) <= diameter_cm <= (hoop_inner_diameter + tolerance):
        return True

    return False

def draw_and_get_centers(contours, frame, expected_diameter, color, tolerance=2):
    hoop_centers = []

    for contour in contours:
        # Get the bounding rectangle
        x, y, w, h = cv2.boundingRect(contour)
        calculated_diameter = (w + h) / 2

        # Calculate aspect ratio
        aspect_ratio = float(w) / h

        # Compute the area of the contour
        area = cv2.contourArea(contour)
        expected_area = np.pi * (expected_diameter / 2)**2
        #if aspect_ratio == 1:
            #print("Aspect Ratio:", aspect_ratio, "Area:", area, "Expected Area:", expected_area)

        diameter_text = f"Diameter: {calculated_diameter:.2f}"
        area_text = f"Area: {area:.2f}"


        # Filter based on aspect ratio and area
        #if 0.8 <= aspect_ratio <= 1.2 and (expected_area - tolerance) <= area <= (expected_area + tolerance):
        if True:
            hoop_center = (x + w // 2, y + h // 2)
            hoop_centers.append(hoop_center)
            
            # Drawing bounding rectangle for the hoop
            if True:
                cv2.drawContours(frame, [contour], 0, color, 2)
            
                font = cv2.FONT_HERSHEY_SIMPLEX
                #cv2.putText(frame, diameter_text, (x, y), font, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
                #cv2.putText(frame, area_text, (x, y), font, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
                # Drawing the center of the hoop
                #cv2.circle(frame, hoop_center, 3, color, -1)

    return hoop_centers


while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    #un_distored_frame = cv2.undistort(frame, camera_matrix, distortion_coefficients, None)
    # Convert the frame to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Mask for red and yellow colors
    red_mask = cv2.inRange(hsv, red_lower, red_upper)
    yellow_mask = cv2.inRange(hsv, yellow_lower, yellow_upper)

    # Optional: Morphological operations to remove noise
    kernel = np.ones((5, 5), "uint8")
    red_mask = cv2.dilate(red_mask, kernel)
    yellow_mask = cv2.dilate(yellow_mask, kernel)

    contours_red, _ = cv2.findContours(red_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours_yellow, _ = cv2.findContours(yellow_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    red_hoop_centers = draw_and_get_centers(contours_red, frame, red_hoop_inner_diameter, (0, 0, 255))
    yellow_hoop_centers = draw_and_get_centers(contours_yellow, frame, yellow_hoop_inner_diameter, (0, 255, 255))

    cv2.imshow("Hoops", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
