from djitellopy import Tello
import cv2
import numpy as np


################## TELLO SETTINGS ################################

startCounter = 0

# CONNECT TO TELLO

me = Tello()
#me.connect()

# Direction & Speed Settings
me.for_back_velocity = 0
me.left_right_velocity = 0
me.up_down_velocity = 0
me.yaw_velocity = 0
me.speed = 0

#########################################################################

## CONSTANTS ##
boundry = 100
frameWidth = 640
frameHeight = 480
CloseCurve = False
global dir

def empty(a):
    pass

#GET VIDEO STREAM
#cap = cv2.VideoCapture(0)
#cap = cv2.VideoCapture('./data/videos/scan_2_rinr_angular_1.mov')
cap = cv2.VideoCapture('./data/videos/drone_scan_360.mov')
cap.set(3, frameWidth)
cap.set(4, frameHeight)
cap.set(10,200)


#Tracks for Adjustment
cv2.namedWindow("HSV")
cv2.resizeWindow("HSV",640,240)
cv2.createTrackbar("HUE Min","HSV",0,179,empty) #custom set min to 10
cv2.createTrackbar("HUE Max","HSV",10,179,empty)
cv2.createTrackbar("SAT Min","HSV",120,255,empty) #custom set min to 10
cv2.createTrackbar("SAT Max","HSV",255,255,empty)
cv2.createTrackbar("VALUE Min","HSV",70,255,empty) #custom set min to 10
cv2.createTrackbar("VALUE Max","HSV",255,255,empty)

cv2.namedWindow("Parameters")
cv2.resizeWindow("Parameters",640,240)
cv2.createTrackbar("Threshold1","Parameters",166,255,empty)
cv2.createTrackbar("Threshold2","Parameters",171,255,empty)
cv2.createTrackbar("Area","Parameters",2290,30000,empty) #custom set min to 10


#GET THE RING COLOR RANGE
def getRingHSV(ring_color):
    global lower, upper
    if ring_color == 'RED':
        #lower = np.array([30,150,50])
        #upper = np.array([225, 255, 180])
        lower = np.array([0, 120, 70])
        upper = np.array([10, 255, 255])
    elif ring_color == 'YELLOW':
        lower = np.array([20, 100, 100])
        upper = np.array([30, 255, 255])
    return lower, upper

#GET THE FILTER CONTOURS FROM STREAM 
def get_xyz_ring(img,ringColor):
    lower, upper = getRingHSV(ring_color)
    imgHsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(imgHsv,lower,upper)
    result = cv2.bitwise_and(img,img, mask = mask)
    mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

    imgBlur = cv2.GaussianBlur(result, (7, 7), 1)
    imgGray = cv2.cvtColor(imgBlur, cv2.COLOR_BGR2GRAY)
    imgCanny = cv2.Canny(imgGray, 166, 177)
    kernel = np.ones((5, 5),"uint8")
    imgDil = cv2.dilate(imgCanny, kernel, iterations=1)


    contours, _ = cv2.findContours(imgDil, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    center_x = 0
    center_y = 0 
    for cnt in contours:
        area = cv2.contourArea(cnt)
        areaMin = 0 
        #get it from tracker bar
        #areaMin = cv2.getTrackbarPos("Area", "Parameters")
        
        if ringColor == 'RED':
            print(ringColor, area)
            areaMin = 5000
        elif ringColor == 'YELLOW':
            print (ringColor, area)
            areaMin = 2200

        if area > areaMin:
            cv2.drawContours(img, cnt, -1, (255, 0, 255), 7)
            peri = cv2.arcLength(cnt, CloseCurve)
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, CloseCurve)
            print("approx length of circle ",len(approx))
            
            x , y , w, h = cv2.boundingRect(approx)
            center_x = int(x + (w / 2))  # CENTER X OF THE OBJECT
            center_y = int(y + (h / 2))  # CENTER y OF THE OBJECT

            '''
            if (cx <int(frameWidth/2)-boundry):
                cv2.putText(img, " GO LEFT " , (20, 50), cv2.FONT_HERSHEY_COMPLEX,1,(0, 0, 255), 3)
                #cv2.rectangle(img,(0,int(frameHeight/2-boundry)),(int(frameWidth/2)-boundry,int(frameHeight/2)+boundry),(0,0,255),cv2.FILLED)
                dir = 1
            elif (cx > int(frameWidth / 2) + boundry):
                cv2.putText(img, " GO RIGHT ", (20, 50), cv2.FONT_HERSHEY_COMPLEX,1,(0, 0, 255), 3)
                #cv2.rectangle(img,(int(frameWidth/2+boundry),int(frameHeight/2-boundry)),(frameWidth,int(frameHeight/2)+boundry),(0,0,255),cv2.FILLED)
                dir = 2
            elif (cy < int(frameHeight / 2) - boundry):
                cv2.putText(img, " GO UP ", (20, 50), cv2.FONT_HERSHEY_COMPLEX,1,(0, 0, 255), 3)
                #cv2.rectangle(img,(int(frameWidth/2-boundry),0),(int(frameWidth/2+boundry),int(frameHeight/2)-boundry),(0,0,255),cv2.FILLED)
                dir = 3
            elif (cy > int(frameHeight / 2) + boundry):
                cv2.putText(img, " GO DOWN ", (20, 50), cv2.FONT_HERSHEY_COMPLEX, 1,(0, 0, 255), 3)
                #cv2.rectangle(img,(int(frameWidth/2-boundry),int(frameHeight/2)+boundry),(int(frameWidth/2+boundry),frameHeight),(0,0,255),cv2.FILLED)
                dir = 4q
            else: dir=0
            '''

            cv2.line(img, (int(frameWidth/2),int(frameHeight/2)), (center_x,center_y),(0, 0, 255), 3)
            #cv2.circle(img, (int(frameWidth/2),int(frameHeight/2)), (center_x,center_y),(0, 0, 255), 3)
            cv2.circle(img, (int(center_x), int(center_y)), 3, (0, 0, 0), -1)
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 5)
            cv2.putText(img, "Points: " + str(len(approx)), (x + w + 20, y + 20), cv2.FONT_HERSHEY_COMPLEX, .7,(0, 255, 0), 2)
            cv2.putText(img, "Area: " + str(int(area)), (x + w + 20, y + 45), cv2.FONT_HERSHEY_COMPLEX, 0.7,(0, 255, 0), 2)
            cv2.putText(img, " " + str(int(x)) + " " + str(int(y)), (x - 20, y - 45), cv2.FONT_HERSHEY_COMPLEX,0.7,(0, 255, 0), 2)
        else: dir=0
    return center_x,center_y

#DISPLAY STREAM ON FRAME
def display(img):
    #cv2.line(img,(int(frameWidth/2)-boundry,0),(int(frameWidth/2)-boundry,frameHeight),(255,255,0),3)
    #cv2.line(img,(int(frameWidth/2)+boundry,0),(int(frameWidth/2)+boundry,frameHeight),(255,255,0),3)
    cv2.circle(img,(int(frameWidth/2),int(frameHeight/2)),5,(0,0,255),5)
    #cv2.line(img, (0,int(frameHeight / 2) - boundry), (frameWidth,int(frameHeight / 2) - boundry), (255, 255, 0), 3)
    #cv2.line(img, (0, int(frameHeight / 2) + boundry), (frameWidth, int(frameHeight / 2) + boundry), (255, 255, 0), 3)
    pass

while True:
    ring_color = 'RED'
    _, img = cap.read()
    get_xyz_ring(img, ring_color)
    display(img)

    #instruct_tello()

    #set 0.5 to resize image in frame
    #stack = stackImages(0.5, ([img, result], [imgDil, imgOrg]))
    cv2.imshow('Horizontal Stacking', img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        #me.land()
        break

cap.release()
cv2.destroyAllWindows()



