import cv2
import numpy as np

def detect_rings(image_path):
    # Read the image
    image = cv2.imread(image_path)

    # Convert the image to HSV color space
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define the range for red color in HSV
    lower_red_1 = np.array([0, 70, 50])
    upper_red_1 = np.array([10, 255, 255])
    lower_red_2 = np.array([160, 70, 50])
    upper_red_2 = np.array([180, 255, 255])

    # Create masks for both red ranges and merge them
    mask_1 = cv2.inRange(hsv, lower_red_1, upper_red_1)
    mask_2 = cv2.inRange(hsv, lower_red_2, upper_red_2)
    mask = cv2.bitwise_or(mask_1, mask_2)

    # Apply Gaussian blur to the mask
    blurred = cv2.GaussianBlur(mask, (9, 9), 2)

    # Detect circles using the Hough transform
    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=1.2, minDist=50, param1=50, param2=30, minRadius=10, maxRadius=300)

    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for circle in circles:
            # Extract the x, y, and z (radius) values
            x, y, z = circle

            # In this context, z value represents the size (radius) of the ring
            print(f"Ring center: X={x}, Y={y}, Z (approx based on size)={z}")

            # Draw the circle in the output image
            cv2.circle(image, (x, y), z, (0, 255, 0), 4)

        # Show the output image with the detected rings
        cv2.imshow("Detected Rings", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    else:
        print("No rings detected")


image_path = "../data/images/extracted_frames/frame_508.jpg"
detect_rings(image_path)
