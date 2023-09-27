import numpy as np
import cv2

class ContourFilter:

    def __init__(self):
        self.boundry = 100
        self.frameWidth = 640
        self.frameHeight = 480
        self.startcounter = 0
        self.dir = 0
        pass

    def empty(a):
        pass

    #Get Ring Color Range in Numpy
    def getRingHSV(self, ring_color):
        lower = None
        upper = None
        known_width = 0
        if ring_color == 'RED':
            #lower = np.array([30,150,50])
            lower = np.array([0, 100, 70])
            #upper = np.array([10, 255, 255])
            upper = np.array([5, 255, 160])
            known_width = 560 #(in mm) #56(in cm)
        elif ring_color == 'YELLOW':
            lower = np.array([20, 100, 100])
            upper = np.array([30, 255, 255])
            known_width = 480 #(in mm) #48(cm)
        return lower,upper,known_width


    #Get the filter contour from image
    def get_xyz_ring(self,img,ringColor):

        closure_curve = True
        #FOCAL_LENGTH =   1987.7588924985816 #(in mm) #198.7758892
        FOCAL_LENGTH =  42 #41.36695970020233

        imgOrg = img.copy()
        
        lower,upper,known_width = self.getRingHSV(ring_color)
        imgHsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        mask = cv2.inRange(imgHsv,lower,upper)
        result = cv2.bitwise_and(img,img,mask=mask)
        mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

        imgBlur = cv2.GaussianBlur(result, (3,3),0,borderType=cv2.BORDER_CONSTANT)
        imgGray = cv2.cvtColor(imgBlur, cv2.COLOR_BGR2GRAY)
        imgCanny = cv2.Canny(imgGray, 166, 175)
        kernel = np.ones((5, 5),"uint8")
        imgDil = cv2.dilate(imgCanny, kernel, iterations=1)
        
        contours, _ = cv2.findContours(imgDil,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
        center_x = 0
        center_y = 0
        distance = 0

        print("Total Contour detected: ",len(contours))

        for cnt in contours:
            area = cv2.contourArea(cnt) 
            areaMin = 0
            
            if ringColor == 'RED':
                areaMin = 2500
            elif ringColor == 'YELLOW':
                areaMin = 1500

            peri = cv2.arcLength(cnt, closure_curve)
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, closure_curve)

            print("Ring Area, AreaMin, length: ", area, areaMin, len(approx))
            if area > areaMin and len(approx) > 4: 
            
                x , y , w, h = cv2.boundingRect(approx)
                center_x = int(x + (w / 2))  # CENTER X OF THE OBJECT
                center_y = int(y + (h / 2))  # CENTER y OF THE OBJECT
                distance = self.distance_to_camera(known_width, FOCAL_LENGTH, w)
                print (x,y,w,h)
                print("Approx center of X: ",center_x)
                print("Approx center of Y:",center_y)
                print("Distance: ",distance)

                
                if (center_x <int(self.frameWidth/2)-self.boundry):
                #    cv2.putText(img, " GO LEFT " , (20, 50), cv2.FONT_HERSHEY_COMPLEX,1,(0, 0, 255), 3)
                #    cv2.rectangle(img,(0,int(self.frameHeight/2-self.boundry)),(int(self.frameWidth/2)-self.boundry,int(self.frameHeight/2)+self.boundry),(0,0,255),cv2.FILLED)
                    dir = 1
                elif (center_x > int(self.frameWidth / 2) + self.boundry):
                #   cv2.putText(img, " GO RIGHT ", (20, 50), cv2.FONT_HERSHEY_COMPLEX,1,(0, 0, 255), 3)
                #    cv2.rectangle(img,(int(self.frameWidth/2+self.boundry),int(self.frameHeight/2-self.boundry)),(self.frameWidth,int(self.frameHeight/2)+self.boundry),(0,0,255),cv2.FILLED)
                    dir = 2
                elif (center_y < int(self.frameWidth / 2) - self.boundry):
                #    cv2.putText(img, " GO UP ", (20, 50), cv2.FONT_HERSHEY_COMPLEX,1,(0, 0, 255), 3)
                #    cv2.rectangle(img,(int(self.frameWidth/2-self.boundry),0),(int(self.frameWidth/2+self.boundry),int(self.frameHeight/2)-self.boundry),(0,0,255),cv2.FILLED)
                    dir = 3
                elif (center_y > int(self.frameWidth / 2) + self.boundry):
                #    cv2.putText(img, " GO DOWN ", (20, 50), cv2.FONT_HERSHEY_COMPLEX, 1,(0, 0, 255), 3)
                #    cv2.rectangle(img,(int(self.frameWidth/2-self.boundry),int(self.frameHeight/2)+self.boundry),(int(self.frameWidth/2+self.boundry),self.frameHeight),(0,0,255),cv2.FILLED)
                    dir = 4
                else: dir=0
                #cv2.line(img, (int(frameWidth/2),int(frameHeight/2)), (center_x,center_y),(0, 0, 255), 3)
                #cv2.circle(img, (int(frameWidth/2),int(frameHeight/2)), (center_x,center_y),(0, 0, 255), 3)
                cv2.circle(img, (int(center_x), int(center_y)), 3, (0, 0, 0), -1)
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 5)
                #cv2.putText(img, "Points: " + str(len(approx)), (x + w + 20, y + 20), cv2.FONT_HERSHEY_COMPLEX, .7,(0, 255, 0), 2)
                cv2.putText(img, "Area: " + str(int(area)), (x + w + 20, y + 20), cv2.FONT_HERSHEY_COMPLEX, 0.7,(0, 255, 0), 2)
                cv2.putText(img, "Dist: " + str(int(distance)), (x + w + 20, y + 45), cv2.FONT_HERSHEY_COMPLEX, 0.7,(0, 255, 0), 2)
                #cv2.putText(img, " " + str(int(x)) + " " + str(int(y)), (x - 20, y - 45), cv2.FONT_HERSHEY_COMPLEX,0.7,(0, 255, 0), 2)
            else: dir=0
        return center_x,center_y,distance,img

    def distance_to_camera(self, knownWidth, focalLenght, perceivedWidth):
        # compute and return the distance from the maker to the camera
        return ((knownWidth * focalLenght) / perceivedWidth) * 2.54

cap = cv2.VideoCapture('./data/videos/test_run_20230925_191002.mp4')
cl = ContourFilter()

while True:

    ring_color = 'YELLOW'
    _, img = cap.read()
 
    center_x,center_y,dis,output_img = cl.get_xyz_ring(img,ring_color)
    print(center_x,center_y,dis)

    cv2.imshow("Test",output_img);

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()






