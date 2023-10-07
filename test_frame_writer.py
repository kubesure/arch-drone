# test reading only 30 FPS and not more in a while loop

import time
import utils
# Desired interval between frames in seconds, for 30 FPS
frame_time = 1.0 / 30
cap_reader_writer = utils.Cv2CapReaderWriter()

start_time = time.time()
while int(time.time() - start_time) < 10:
    start_time = time.time()
    ret, frame = cap_reader_writer.get_frame()
    if not ret:
        break

    cap_reader_writer.write(frame)
    elapsed_time = time.time() - start_time
    print(elapsed_time)
    sleep_time = frame_time - elapsed_time
    print(sleep_time)
    if sleep_time > 0:
        time.sleep(sleep_time)


