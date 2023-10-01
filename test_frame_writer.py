# test reading only 30 FPS and not more in a while loop

import time
import utils
# Desired interval between frames in seconds, for 30 FPS
frame_time = 1.0 / 30
out_writer, video_reader = utils.get_out_writer(True)

start_time = time.time()
while int(time.time() - start_time) < 10:
    start_time = time.time()
    ret, frame = video_reader.get_frame()
    if not ret:
        break

    out_writer.write(frame)
    elapsed_time = time.time() - start_time
    sleep_time = frame_time - elapsed_time
    if sleep_time > 0:
        time.sleep(sleep_time)


