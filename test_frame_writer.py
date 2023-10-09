import time
import utils
import cv2
import os

def save_frame_as_image(frame, output_folder, frame_count):
    frame_filename = os.path.join(output_folder, f"frame_{frame_count}.jpg")
    cv2.imwrite(frame_filename, frame)

def extract_frames(video_path, output_folder):
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Couldn't open the video file {video_path}")
        return

    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        save_frame_as_image(frame, output_folder, frame_count)
        frame_count += 1

    cap.release()
    print(f"Extracted {frame_count} frames and saved them in {output_folder}")

# orginal code to test reading only 30 FPS and not more in a while loop

frame_time = 1.0 / 30
cap_reader_writer = utils.Cv2CapReaderWriter()

start_time = time.time()
while int(time.time() - start_time) < 10:
    loop_start_time = time.time()
    ret, frame = cap_reader_writer.get_frame()
    if not ret:
        break

    cap_reader_writer.write(frame)
    elapsed_time = time.time() - loop_start_time
    print(elapsed_time)
    sleep_time = frame_time - elapsed_time
    print(sleep_time)
    if sleep_time > 0:
        time.sleep(sleep_time)

video_path = "/Users/sandipbhowmik/Study/Arch-Drone/DistortedVideo/test_run_20231008_151446_red_scanned.mp4"
output_folder = "extracted_frames"
extract_frames(video_path, output_folder)


