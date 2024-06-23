#### Introduction
This project involves creating an autonomous drone using the DJI Tello and the OpenCV library for a navigation competition. 
We developed algorithms to allow the drone to navigate and avoid obstacles using computer vision techniques.

#### Project Description
##### Objective
The goal was to build a drone that can navigate autonomously through rings (see video) using computer vision techniques.  

##### Hardware Setup
- **Drone:** DJI Tello

##### Software Components
- **Programming Language:** Python
- **Libraries:** OpenCV, `djitellopy`

#### Implementation Steps
1. **Setting Up:** We started by setting up the development environment and ensuring the Tello drone was ready for programming.
   Install the  [DJI app](https://apps.apple.com/ae/app/tello/id1330559633) and calibrate the drone. 
2. **Integrating OpenCV:** Using OpenCV, we developed algorithms for object detection and navigation.
3. **Autonomous Navigation:** Implemented computer vision techniques to allow the drone to navigate and avoid obstacles.

##### Broad steps of detection and navigation (refer to launch.py to follow the code path for complete detection navigation)

1. Drone takes off   
2. Hovers at a preset Y-axis   
3. Detects the nearest ring (X, Y, Z are found)  
4. Corrects its position on x and y, moves forward z distance through the center of the ring  
5. Repeats Hover, Detect, Correct and Navigate until all rings are over and lands
#####

##### Object Detection (refer to complete code in launch.py)
This code snippet shows launch and hover, detect, correct and move loop 
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
#####

##### Object (ring) Detection (refer to complete code in detector/contour.py)
This code snippet shows how to detect objects using OpenCV. Gets rings x,y,z in the frame during the hover duration.  
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
        focal_length = 42  # Focal length of the camera

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
                area_min = 12000
            elif ring == RingColor.YELLOW:
                area_min = 7000

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

##### Navigation  
These code snippet shows how to navigate the drone to the detected ring. 

```python (Refer to common.py for complete code)
def hover_at(inn: NavigatorInput, drone: Tello, attempt):
    """
    Hover the drone at a specific height Y-axis and perform scanning routines while in hover for detection to get rings.

    Parameters:
    inn (NavigatorInput): Input containing details about the navigation.
    drone (Tello): Drone object to control movements.
    attempt (int): The current attempt number for hovering and scanning.

    Process:
    1. Log the current attempt and ring color.
    2. Perform height adjustment for attempts other than 4.
    3. Execute different scanning routines based on the attempt number.
    """
    logger.debug(f"Attempt {attempt} on ring {inn.ring_color} with duration {inn.duration}")
  
    if attempt != 4:
        y_direction, y_movement = get_optimum_hover_height(drone, inn)
        move_to_y(drone, inn, y_direction, y_movement)

        # move code in common.py....
```        
        
After y-axis correction drone is aligned on x-axis in relation to the center of ring and moves forward

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
    3. Calculate the distance to travel and log the information.
    4. Move the drone forward by the calculated distance.
    5. Perform x-axis correction.
    6. Return success status and the ring object.
    """
    logger.info(f"Navigating to ring {inn.ring_color} at position {inn.ring_position}")
    hover_time(1)  # Hover to stabilize the drone

    # Calculate the distance to travel
    distance_to_travel = ring.z + constants.buffer_distance
    logger.info(f"Moving forward -- {distance_to_travel} = {ring.z} + {constants.buffer_distance}")

    # Move the drone forward
    drone.move_forward(distance_to_travel)

    # Perform x-axis correction
    do_x_correction(cap_reader_writer, drone, inn, ring)

    return True, ring
    #... more code in simple.py
```


#### Challenges and Solutions
We faced several challenges, from setting up the drone's SDK to debugging the navigation algorithms. Our persistence and
collaborative effort helped us overcome these hurdles, leading to a successful project.

- **Challenge:** Integrating the Tello drone with OpenCV.
  - **Solution:** We used the `djitellopy` library to facilitate communication with the Tello drone and handled video streaming with OpenCV.
- **Challenge:** Navigation algorithms. 
  - or else you drone will not navigate well with DJI tello library. If its crashes behave cranky re-calibrate. 
  - Its highly recommend to use a PID controller to avoid the out calibration errors even when you re-calibrate sometime.
- **Challenge:** Developing reliable object detection algorithms.
  - **Solution:** We experimented with different thresholding and contour detection techniques to identify objects and navigate accordingly.

#### Results and Demonstration
The outcome was a fully functional autonomous drone capable of navigating through various environments. Below are some key highlights from the video demonstration:

1. **Takeoff and Initialization (0:00 - 0:10)**
   - The drone takes off smoothly and initializes its systems, preparing for autonomous navigation.

2. **Object Detection in Action (0:20 - 0:30)**
   - The drone successfully identifies objects in its path using the OpenCV-based detection algorithm. The contours of the objects are highlighted in the video.

3. **Navigation Decisions (0:30 - 0:40)**
   - Based on the detected objects, the drone makes decisions to move left, right, or forward. This part of the video shows the drone avoiding obstacles effectively.

4. **Distance Calculation (0:40 - 0:50)**
   - The drone calculates the distance to nearby objects using a simple linear relationship. This helps it maintain a safe distance while navigating.

5. **Successful Navigation (0:50 - 1:00)**
   - The drone successfully navigates through the environment, demonstrating its ability to avoid obstacles and follow a path autonomously.

6. **Landing (1:10 - 1:20)**
   - After completing its navigation task, the drone lands safely, showing the effectiveness of the landing procedures implemented.

[Watch the video demonstration](https://youtu.be/L_odr1_XLm4)

#### Conclusion
This project taught us a lot about the intricacies of computer vision and quadcopters. We are excited about the future possibilities
and improvements we can make like using Yolo + OpenCv, re-enforcement Learning and building our [drone](https://www.amazon.ae/gp/cart/view.html?ref_=nav_top_cart)
with Raspberry Pi     

#### Acknowledgments
Special thanks to Viral Gohil for his invaluable contribution object detection and distance calculation. 
