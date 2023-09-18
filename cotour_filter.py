from djitellopy import Tello
import cv2
import numpy as np

################## TELLO SETTINGS ################################

startCounter = 0

# CONNECT TO TELLO
me = Tello()
me.connect()

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
RED = 'RED'
YELLOW = 'YELLOW'
ringColor = RED
CloseCurve = False
global dir

#GET VIDEO STREAM
cap = cv2.VideoCapture(0)
#cap = cv2.VideoCapture('./data/videos/scan_2_rinr_angular_1.mov')
cap.set(3, frameWidth)
cap.set(4, frameHeight)
cap.set(10,200)

#GET THE RING COLOR RANGE
def getRingHSV(ring):
    global lower, upper
    if ring == RED:
        lower = np.array([30,150,50])
        upper = np.array([225, 255, 180])
    elif ring == YELLOW :
        lower = np.array([20, 100, 100])
        upper = np.array([30, 255, 255])
    return lower, upper

#GET THE FILTER CONTOURS FROM STREAM 
def getContours(img,imgContour,ringColor):

    #Get all cotours
    contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    #iterate through required cotour
    for cnt in contours:
        area = cv2.contourArea(cnt)
        areaMin = 0 

        #get it from tracker bar
        #areaMin = cv2.getTrackbarPos("Area", "Parameters")
        
        if ringColor == 'RED':
            print(ringColor, area)
            areaMin = 1500
        elif ringColor == 'YELLO':
            print (ringColor, area)
            areaMin = 10

        if area > areaMin:
            
            cv2.drawContours(imgContour, cnt, -1, (255, 0, 255), 7)
            peri = cv2.arcLength(cnt, CloseCurve)
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, CloseCurve)
            print("length",len(approx))
            
            x , y , w, h = cv2.boundingRect(approx)
            cx = int(x + (w / 2))  # CENTER X OF THE OBJECT
            cy = int(y + (h / 2))  # CENTER X OF THE OBJECT

            if (cx <int(frameWidth/2)-boundry):
                cv2.putText(imgContour, " GO LEFT " , (20, 50), cv2.FONT_HERSHEY_COMPLEX,1,(0, 0, 255), 3)
                cv2.rectangle(imgContour,(0,int(frameHeight/2-boundry)),(int(frameWidth/2)-boundry,int(frameHeight/2)+boundry),(0,0,255),cv2.FILLED)
                dir = 1
            elif (cx > int(frameWidth / 2) + boundry):
                cv2.putText(imgContour, " GO RIGHT ", (20, 50), cv2.FONT_HERSHEY_COMPLEX,1,(0, 0, 255), 3)
                cv2.rectangle(imgContour,(int(frameWidth/2+boundry),int(frameHeight/2-boundry)),(frameWidth,int(frameHeight/2)+boundry),(0,0,255),cv2.FILLED)
                dir = 2
            elif (cy < int(frameHeight / 2) - boundry):
                cv2.putText(imgContour, " GO UP ", (20, 50), cv2.FONT_HERSHEY_COMPLEX,1,(0, 0, 255), 3)
                cv2.rectangle(imgContour,(int(frameWidth/2-boundry),0),(int(frameWidth/2+boundry),int(frameHeight/2)-boundry),(0,0,255),cv2.FILLED)
                dir = 3
            elif (cy > int(frameHeight / 2) + boundry):
                cv2.putText(imgContour, " GO DOWN ", (20, 50), cv2.FONT_HERSHEY_COMPLEX, 1,(0, 0, 255), 3)
                cv2.rectangle(imgContour,(int(frameWidth/2-boundry),int(frameHeight/2)+boundry),(int(frameWidth/2+boundry),frameHeight),(0,0,255),cv2.FILLED)
                dir = 4
            else: dir=0

            cv2.line(imgContour, (int(frameWidth/2),int(frameHeight/2)), (cx,cy),(0, 0, 255), 3)
            cv2.rectangle(imgContour, (x, y), (x + w, y + h), (0, 255, 0), 5)
            cv2.putText(imgContour, "Points: " + str(len(approx)), (x + w + 20, y + 20), cv2.FONT_HERSHEY_COMPLEX, .7,(0, 255, 0), 2)
            cv2.putText(imgContour, "Area: " + str(int(area)), (x + w + 20, y + 45), cv2.FONT_HERSHEY_COMPLEX, 0.7,(0, 255, 0), 2)
            cv2.putText(imgContour, " " + str(int(x)) + " " + str(int(y)), (x - 20, y - 45), cv2.FONT_HERSHEY_COMPLEX,0.7,(0, 255, 0), 2)
        else: dir=0
    return result, imgDil, contours, dir

#DISPLAY STREAM ON FRAME
def display(img):
    cv2.line(img,(int(frameWidth/2)-boundry,0),(int(frameWidth/2)-boundry,frameHeight),(255,255,0),3)
    cv2.line(img,(int(frameWidth/2)+boundry,0),(int(frameWidth/2)+boundry,frameHeight),(255,255,0),3)
    cv2.circle(img,(int(frameWidth/2),int(frameHeight/2)),5,(0,0,255),5)
    cv2.line(img, (0,int(frameHeight / 2) - boundry), (frameWidth,int(frameHeight / 2) - boundry), (255, 255, 0), 3)
    cv2.line(img, (0, int(frameHeight / 2) + boundry), (frameWidth, int(frameHeight / 2) + boundry), (255, 255, 0), 3)

#COLLATE IMAGES FOR DISPLAY
def stackImages(scale,imgArray):
    rows = len(imgArray)
    cols = len(imgArray[0])
    rowsAvailable = isinstance(imgArray[0], list)
    width = imgArray[0][0].shape[1]
    height = imgArray[0][0].shape[0]
    if rowsAvailable:
        for x in range ( 0, rows):
            for y in range(0, cols):
                if imgArray[x][y].shape[:2] == imgArray[0][0].shape [:2]:
                    imgArray[x][y] = cv2.resize(imgArray[x][y], (0, 0), None, scale, scale)
                else:
                    imgArray[x][y] = cv2.resize(imgArray[x][y], (imgArray[0][0].shape[1], imgArray[0][0].shape[0]), None, scale, scale)
                if len(imgArray[x][y].shape) == 2: imgArray[x][y]= cv2.cvtColor( imgArray[x][y], cv2.COLOR_GRAY2BGR)
        imageBlank = np.zeros((height, width, 3), np.uint8)
        hor = [imageBlank]*rows
        hor_con = [imageBlank]*rows
        for x in range(0, rows):
            hor[x] = np.hstack(imgArray[x])
        ver = np.vstack(hor)
    else:
        for x in range(0, rows):
            if imgArray[x].shape[:2] == imgArray[0].shape[:2]:
                imgArray[x] = cv2.resize(imgArray[x], (0, 0), None, scale, scale)
            else:
                imgArray[x] = cv2.resize(imgArray[x], (imgArray[0].shape[1], imgArray[0].shape[0]), None,scale, scale)
            if len(imgArray[x].shape) == 2: imgArray[x] = cv2.cvtColor(imgArray[x], cv2.COLOR_GRAY2BGR)
        hor= np.hstack(imgArray)
        ver = hor
    return ver

#GIVE INSTRUCTION, DIRECTION TO TELLO DRONE
def instruct_tello():
     
     # FLIGHT
    if startCounter == 0:
       me.takeoff()
       startCounter = 1

    if dir == 1:
       me.yaw_velocity = -60
    elif dir == 2:
       me.yaw_velocity = 60
    elif dir == 3:
       me.up_down_velocity= 60
    elif dir == 4:
       me.up_down_velocity= -60
    else:
       me.left_right_velocity = 0; me.for_back_velocity = 0;me.up_down_velocity = 0; me.yaw_velocity = 0
    
    #SEND VELOCITY VALUES TO TELLO
    if me.send_rc_control:
       me.send_rc_control(me.left_right_velocity, me.for_back_velocity, me.up_down_velocity, me.yaw_velocity)
    print(dir)


while True:

    # GET THE IMAGE FROM TELLO
    #frame_read = me.get_frame_read()
    #myFrame = frame_read.frame
    #img = cv2.resize(myFrame, (width, height))

    #GET THE IMAGE FROM WEBCAM
    _, img = cap.read()
    
    imgOrg = img.copy()

    #Get Lower & Upper range of ring color 
    lower, upper = getRingHSV(ringColor)

    imgHsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(imgHsv,lower,upper)
    result = cv2.bitwise_and(img,img, mask = mask)
    mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

    imgBlur = cv2.GaussianBlur(result, (7, 7), 1)
    imgGray = cv2.cvtColor(imgBlur, cv2.COLOR_BGR2GRAY)
    imgCanny = cv2.Canny(imgGray, 166, 177)
    kernel = np.ones((5, 5),"uint8")
    imgDil = cv2.dilate(imgCanny, kernel, iterations=1)
    getContours(imgDil, imgOrg, ringColor)
    display(imgOrg)
    instruct_tello()

    #set 0.5 to resize image in frame
    stack = stackImages(0.5, ([img, result], [imgDil, imgOrg]))
    cv2.imshow('Horizontal Stacking', stack)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        #me.land()
        break

cap.release()
cv2.destroyAllWindows()



