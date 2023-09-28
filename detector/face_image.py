# Developed by Viral Gohil
# import dependent libraries
import cv2
import matplotlib.pyplot as plt

# image path
imagePath = 'E:/Projects/Python/arch-drone/data/images/team.jpeg'

# read image from with OpenCV function
img = cv2.imread(imagePath)

# print the dimension of image
img.shape

# convert the image into grayscale
gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# examine the dimension of image, it would now 2-dimension previously it was 3 dimension
gray_image.shape

# Load the image classifier which called cascade
face_classifier = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# perform the actual facedetection
# detectMultiScale is use to identify different size of face
# gray_image convert 2 dimension image
# scaleFactor scale down the size of the input image to make it easier for the algorithm to detect larger faces.scale factor of 1.1, indicating that we want to reduce the image size by 10%
face = face_classifier.detectMultiScale(
    gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40)
)

# draw the bounty box around faces
for (x, y, w, h) in face:
    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 4)

# prepare for displaying the image
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# use matplotlib to display the image
plt.figure(figsize=(20, 10))
plt.imshow(img_rgb)
plt.axis('off')
