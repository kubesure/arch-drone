#Developed by Viral Gohil
#import dependent libraries
import cv2

# Load the image classifier which called cascade
face_classifier = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

#access the device camera
video_capture = cv2.VideoCapture(0)


#function to detect faces from vedio stream and draw boxs
def detect_bounding_box(vid):
    #convert the frame into gray
    gray_image = cv2.cvtColor(vid, cv2.COLOR_BGR2GRAY)
    
    #perform the actual facedetection
    #detectMultiScale is use to identify different size of face
    #gray_image convert 2 dimension image
    #scaleFactor scale down the size of the input image to make it easier for the algorithm to detect larger faces.scale factor of 1.1, indicating that we want to reduce the image size by 10%
    faces = face_classifier.detectMultiScale(gray_image, 1.1, 5, minSize=(40, 40))
    for (x, y, w, h) in faces:
        cv2.rectangle(vid, (x, y), (x + w, y + h), (0, 255, 0), 4)
    return faces

#loop the face detection to run through frames
while True:

    result, video_frame = video_capture.read()  # read frames from the video
    if result is False:
        break  # terminate the loop if the frame is not read successfully

    faces = detect_bounding_box(
        video_frame
    )  # apply the function we created to the video frame

    cv2.imshow(
        "My Face Detection Project", video_frame
    )  # display the processed frame in a window named "My Face Detection Project"

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

video_capture.release()
cv2.destroyAllWindows()


