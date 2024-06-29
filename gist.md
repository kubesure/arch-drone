#### Introduction
This project involves creating an autonomous drone using the DJI Tello and the OpenCV library for a navigation competition. 

#### Project Description
##### Objective
The goal was to build a drone that can navigate autonomously through a sequence of vertically colored rings using computer vision
techniques.

##### Hardware Setup
- **Drone:** DJI Tello

##### Software Components
- **Programming Language:** Python
- **Libraries:** OpenCV, `djitellopy`

#### Implementation Steps
1. **Setting Up:** Development environment setup and Tello calibration using [DJI app](https://apps.apple.com/ae/app/tello/id1330559633) . 
2. **Integrating OpenCV:** Use OpenCV and develop algorithms for object detection.
3. **Autonomous Navigation:** Implement drone navigation through rings.

##### Broad steps of detection and navigation
1. Drone takes off   
2. Hovers or throttles to Y-axis   
3. Detects next in sequence the nearest colored ring i.e., its X-axis (Roll - left right), Y-axis (throttle up down) and Z-axis(Pitch up down)   
4. Corrects its position by rolling, throttling to the detected ring 
5. Pitches forward only to the ring   
6. Repeats Hover, Detect, Correct and Pitch until all rings are passed through and lands
#####

##### Step 1—Main controller—Launch Hover Detect Navigate Loop (refer to complete code in launch.py)
This code snippet shows the main controller launch, hover, detect, correct and move loop 
```python
drone.takeoff()
navigator.common.hover_time(1)
drone.set_speed(constants.speed)
if not drone.is_flying:
    raise DroneException("Take off error", DroneErrorCode.TakeOffError)

q = queue.Queue()
last_ring_navigated = Ring(x=0, y=0, z=0, area=0, color=RingColor.YELLOW)

# Iterate through the ring sequence and navigate to each ring
for index, ring in enumerate(ring_sequence):
    logger.info(f"Running sequence for ring color {ring} at index {index}")
    flight_input = NavigatorInput(ring_color=ring,
                                  q=q,
                                  duration=3,
                                  last_ring_navigated=last_ring_navigated,
                                  ring_position=index)
    detected, ring = hover_and_get_ring(flight_input, drone, cap_reader_writer)
    if detected:
        logger.info(f"Ring detected, navigating to {ring}")
        _, last_navigated_ring = simple.navigate_to(flight_input, ring, drone, cap_reader_writer)
    else:
        logger.info("No rings detected")
```

##### Step 2 and 3 - Object / Ring detection 1—(refer to complete code in launch.py)
Get the closest colored ring in sequence. Drone hover and ring detection take place simultaneously. Hover thread 
(navigator/common.py.hover_at)completes after hover duration, during the hover period, plotter (plotter.py) gets multiple 
rings which are filtered to get a single ring by utils.get_avg_distance (utils.py)
```python
def hover_and_get_ring(inn: NavigatorInput, dronee, cap_read_write) -> (bool, Ring):
    """
    Hover the drone and detect rings in the surroundings.

    Parameters:
    inn (NavigatorInput): Input containing details about the navigation.
    dronee (Tello): Drone object to control movements.
    cap_read_write: Object to read and write data for ring detection.

    Returns:
    tuple: A tuple containing a boolean indicating detection success and the detected Ring object.

    Process:
    1. Initialize attempt count and detection status.
    2. Start a thread to hover the drone and detect rings.
    3. Plotter detects rings and join the hover thread.
    4. Return the average distance of detected ring.

    The method hovers the drone at a specified position and captures video frames to detect rings.
    It then processes the detected rings to find the average position of all detected rings and returns
    the average ring's position and detection status.
    """
    attempts = 1
    is_detected = False
    rings_detected: List[Ring] = []

    # Start a thread to hover the drone and detect rings
    while not is_detected:
        drone_hover = Thread(target=navigator.common.hover_at, args=(inn, dronee, attempts))
        drone_hover.start()

        # Capture and plot the detected rings
        rings_detected = plotter.plot(inn, cap_read_write)
        drone_hover.join()

        if attempts == 1:
            break

    # Return the average distance of the nearest ring out the detected rings
    return utils.get_avg_distance(rings_detected)
```

##### Step 2 and 3 - Object / Ring Detection 2 using OpenCV (refer to complete code in detector/contour.py)
This code snippet shows how to detect objects using OpenCV. This functions returns multiple rings and their x,y,z distance.
Only rings in the drone's camera frame are captured.
```python
def get_xyz_ring(self, img, ring: RingColor):
        """
        Get the position of the ring in the image.

        Parameters:
        img (numpy.ndarray): The input image.
        ring (RingColor): The color of the ring to identify.

        Returns:
        tuple: A Ring object with the x, y, z coordinates and area, and the processed image with annotations.
        """
        closure_curve = True  # Indicates whether the contour is closed
        focal_length = constants.focal_length_camera  # Focal length of the camera is 42

        # Get HSV color range, known width, and iteration count for the specified ring color
        lowers, uppers, known_width, iteration = self.get_ring_hsv(ring)

        # Convert the image from BGR to HSV color space
        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        mask = None  # Initialize the mask
        # Create a mask for the specified ring color
        for lower, upper in zip(lowers, uppers):
            if mask is None:
                mask = cv2.inRange(img_hsv, lower, upper)
            else:
                mask = cv2.bitwise_or(mask, cv2.inRange(img_hsv, lower, upper))

        # Apply the mask to the original image
        result = cv2.bitwise_and(img, img, mask=mask)

        # Apply Gaussian Blur to the result
        img_blur = cv2.GaussianBlur(result, (3, 3), 0, borderType=cv2.BORDER_CONSTANT)

        # Convert the blurred image to grayscale
        img_gray = cv2.cvtColor(img_blur, cv2.COLOR_BGR2GRAY)

        # Perform Canny edge detection
        img_canny = cv2.Canny(img_gray, 166, 175)

        # Define a kernel for dilation
        kernel = np.ones((5, 5), dtype=np.uint8)

        # Dilate the edges
        img_dil = cv2.dilate(img_canny, kernel, iterations=iteration)

        # Find contours in the dilated image
        contours, _ = cv2.findContours(img_dil, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        center_x = 0  # Initialize x-coordinate of the ring center
        center_y = 0  # Initialize y-coordinate of the ring center
        distance = 0  # Initialize distance to the ring
        area = 0  # Initialize the area of the ring

        # Iterate through the detected contours
        for cnt in contours:
            area = cv2.contourArea(cnt)  # Calculate the area of the contour
            area_min = 0  # Minimum area threshold
            if ring == RingColor.RED:
                area_min = 12000 # interested area found after multiple trial runs
            elif ring == RingColor.YELLOW:
                area_min = 7000 # interested area found after multiple trial runs

            peri = cv2.arcLength(cnt, closure_curve)  # Calculate the perimeter of the contour
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, closure_curve)  # Approximate the contour

            # Filter contours based on area and number of vertices
            if area > area_min and len(approx) > 4:
                x, y, bounding_rect_width, bounding_rect_height = cv2.boundingRect(approx)  # Get bounding rectangle
                center_x = int(x + (bounding_rect_width / 2))  # Calculate the center x-coordinate of the object
                center_y = int(y + (bounding_rect_height / 2))  # Calculate the center y-coordinate of the object
                distance = self.distance_to_camera(known_width, focal_length,
                                                   bounding_rect_width)  # Calculate distance to the camera

                # Draw annotations on the image
                cv2.circle(img, (int(center_x), int(center_y)), 3, (0, 0, 0), -1)
                cv2.rectangle(img, (x, y), (x + bounding_rect_width, y + bounding_rect_height), (0, 255, 0), 5)
                cv2.putText(img, "A: " + str(int(area)), (x + bounding_rect_width + 20, y + 20),
                            cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(img, "X: " + str(int(center_x)), (x + bounding_rect_width + 20, y + 20),
                            cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(img, "Y: " + str(int(center_y)), (x + bounding_rect_width + 20, y + 20),
                            cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(img, "Z: " + str(int(distance)), (x + bounding_rect_height + 20, y + 45),
                            cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)

        # Normalize the x-coordinate for consistency
        center_x = int(center_x / 10)
        
        # Create a Ring object with the detected attributes
        r = Ring(x=center_x, y=center_y, z=distance, area=area, color=ring)

        return r, img  # Return the Ring object and the annotated image
```

        
##### Step 4—Navigate to ring 
After y-axis correction, the drone is aligned on x-axis in relation to the center of the ring and moves forward    
#####
```python (Refer to navigator/simple.py for complete code)
def navigate_to(inn: NavigatorInput, ring: Ring, drone: Tello, cap_reader_writer) -> (bool, Ring):
    """
    Navigate the drone to the specified ring position.

    Parameters:
    inn (NavigatorInput): Input containing details about the target ring.
    ring (Ring): Current ring status and position.
    drone (Tello): Drone object to control movements.
    cap_reader_writer: Object to read and write frames to record the video of navigation.

    Returns:
    tuple: A tuple containing a boolean indicating success and the updated ring object.

    Process:
    1. Log the navigation start.
    2. Hover for a second to stabilize the drone.
    3. Calculate the distance + buffer to travel and log the information.
    4. Move the drone forward by the calculated distance.    
    5. Return success status and the ring object.
    """
    logger.info(f"Navigating to ring {inn.ring_color} at position {inn.ring_position}")
    hover_time(1)  # Hover to stabilize the drone

    # Calculate the distance to travel add buffer to move beyond the edge of the ring 
    distance_to_travel = ring.z + constants.buffer_distance
    logger.info(f"Moving forward -- {distance_to_travel} = {ring.z} + {constants.buffer_distance}")

    # Move the drone forward
    drone.move_forward(distance_to_travel)

    #... more code in simple.py
```

#### Challenges and Solutions
We faced several challenges, from setting up the drone's SDK to debugging the navigation algorithms. 

- **Challenge and Solution:**
  - Integrating the Tello drone with OpenCV.
    - We used the `djitellopy` library to facilitate communication with the Tello drone and handled video with OpenCV.
    - Used version 2.4.0 for better camera support or else red and yellow colors appear blue. 
  - Navigation algorithms and Drone API.
    - If the drone crashes or behaves cranky, re-calibrate using the Tello app. 
    - After a crash or for unknown reasons if Tello drone responds with out-of-range errors do re-calibration.
      Tello sensors and firmware assume the drone is operating out of range on x-axis and y-axis. 
    - Only take off if the drone battery is 80% charged or else it can impact throttle and roll.
    - It's highly recommended to use a PID controller to avoid the out of range errors even when you re-calibrate. 
      Refer to common.py for the PID controller. We could not implement as we ran out of time for testing.
  - Developing reliable object detection algorithms.
    - We experimented with different detection techniques to identify objects before finalizing 
      detection through contours as that work best for a colored rings. 
    - Better approach could be would be to use Yolo + OpenCV 
  - Focal length for Distance calculation or Z-axis or pitch distance.   
    - The focal length of 42 is accurate for Tello drone.     
    - However, a better approach would be to use camera calibration and chessboard pattern technique.
      Refer to calibration/calibrate.py and data/images/chessboard. The code calculates the correct camera 
      calibration. But, Drone camera focal length using calibration matrix and coefficients needs more work.

#### Results and Demonstration
The outcome was a fully functional autonomous drone capable of navigating through yellow rings. Below are some key 
highlights from the video demonstration:

1. **Takeoff and Initialization (0:00 - 0:10)**
   - The drone takes off smoothly and initializes for its first pitch.

2. **Object Detection in Action (Throughout the video)**
   - The drone successfully identifies objects in its path using the OpenCV-based detection algorithm. The contours of 
     the objects are highlighted in the video.

3. **Navigation Decisions (0:30–0:50)**
   - Based on the detected objects, the drone makes decisions to move left, right, adjustments.  

4. **Distance Calculation (Throughout the video)**
   - The drone calculates the distance to the nearest ring. Watch distance besides letter 'Z'

5. **Successful Navigation and landing (1:18 - 1:23)**
   - The drone successfully navigates through the yellow rings and land, demonstrating its ability to avoid obstacles 
     and follow a path autonomously.

[Watch the video demonstration](https://youtu.be/L_odr1_XLm4)

#### Conclusion
This project taught us a lot about the intricacies of computer vision and quadcopters. We are excited about the future 
possibilities and improvements we can make, like using Yolo + OpenCv, re-enforcement learning and building our own [drone](https://www.amazon.ae/gp/cart/view.html?ref_=nav_top_cart)
with Raspberry Pi     

#### Acknowledgments
Special thanks to Viral Gohil for his contribution as a team member and to the critical distance calculation. 
