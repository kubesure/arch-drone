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

video_path = "./test_run_20231008_151446_red_scanned.mp4"
output_folder = "extracted_frames"
extract_frames(video_path, output_folder)