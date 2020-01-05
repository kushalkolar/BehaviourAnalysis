# -*- coding: utf-8 -*-
"""
Created on Thu Jul 12 13:37:46 2018

@author: install
"""

import cv2
import numpy as np
import pandas as pd
import time



def detect_circles(frame):
#    frame = cv2.GaussianBlur(frame, (9,9), 0)
    circles = cv2.HoughCircles(frame,cv2.HOUGH_GRADIENT,1,1200,
                            param1=50,param2=30,minRadius=450,maxRadius=550)
    circles = np.uint16(np.around(circles))
    circles = circles[0,:][0]
    return circles

vid = "D:\\amphi.avi"

cap = cv2.VideoCapture(vid)

#w, h = (7680, 4320)qq
#cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
#cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)

cv2.namedWindow('frame',cv2.WINDOW_NORMAL)
cv2.resizeWindow("frame", 1600,800)
f = []
ret = True
while ret:
 
    ret, frame = cap.read()
#    
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
#    
    blur = cv2.GaussianBlur(frame,(5,5),0)
    gray = cv2.addWeighted(blur,2.0,frame,-0.5,0)
#    gray = cv2.cvtColor(gray, cv2.COLOR_RGB2GRAY) 
    ret,gray = cv2.threshold(gray,253,255,cv2.THRESH_TOZERO)
    

##   
#
    x, y, r = detect_circles(gray)

    gray = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
    
    # draw the outer circle
    cv2.circle(gray,(x,y),r,(0,255,0),2)
    # draw the center of the circle
    cv2.circle(gray,(x,y),2,(0,0,255),3)
#        f.append(5500 / (i[2]*2))
        

#    frame = np.hstack([frame, gray])

    cv2.imshow("frame", gray)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()






