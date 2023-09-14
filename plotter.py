from detector import contour_edge
import cv2
import datetime

def plot(drone,sequence):
    print(drone.address)
    drone_video_url = 'udp://@0.0.0.0:11111'
    cap = cv2.VideoCapture(drone_video_url)
    current_time_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_video_path = f"./data/videos/test_run_{current_time_str}.mp4"
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    ret, frame = cap.read()
    if not ret:
        print("Error: Couldn't read a frame from video.")
        return
    height, width, _ = frame.shape
    out_writer = cv2.VideoWriter(output_video_path, fourcc, 30, (width, height))

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        _ = contour_edge.get_xyz_rings(frame,sequence)
        out_writer.write(frame)
        cv2.imshow("Drone Video Feed", frame)
        
        # Press 'q' to exit the video window
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
    cap.release()    
    out_writer.release()    
    cv2.destroyAllWindows()