# -*- coding: utf-8 -*-
"""
Created on Wed Aug  1 12:43:53 2018

@author: install
"""

import cv2
import numpy as np
import pandas as pd
import time
import matplotlib.pyplot as plt

class Centerfinder:
    def __init__(self, minRadius: int=450, maxRadius: int=520, param1 = 50, param2 = 30, threshold: int=150, thresholdmethod = "BINARY"):
        self.minRadius = minRadius
        self.maxRadius = maxRadius
        self.param1 = param1
        self.param2 = param2
        self.threshold = threshold
        if thresholdmethod == "TOZERO":
            self.thresholdmethod = cv2.THRESH_TOZERO
        else:
            self.thresholdmethod = cv2.THRESH_BINARY
        self.counter = 0
        
    
    def find(self,video, n_frames = 5, show_result = False):
        
        start = time.time()
        cap = cv2.VideoCapture(video)
        ret, frame  = cap.read()
        x_av = []
        y_av = []
        r_av = []
        
        ret, frame = cap.read()
        maxframe = frame
        for i in range(n_frames):
            ret, nframe = cap.read()
            maxframe = maxframe + nframe
        
        
        gray, circles = self.detect_circles(maxframe)
        gray = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
        x, y, r  = circles
        x_av.append(x)
        y_av.append(y)
        r_av.append(r)
        
        x = int(np.mean(x_av))
        y = int(np.mean(y_av))
        r = int(np.mean(r_av))
        
        if show_result:
            for im in [gray, frame]:
                cv2.circle(im,(x,y),r,(0,255,0),5)
                # draw the center of the circle
                cv2.circle(im,(x,y),2,(0,0,255),10)

            im = np.hstack([gray, frame])
            cv2.namedWindow("image", cv2.WINDOW_NORMAL)
            cv2.resizeWindow("image", 900,600)
            cv2.imshow("image", im)
#            cv2.imwrite("D:\Circles\Circle_"+str(self.counter).zfill(3)+".jpg", im)
            self.counter+=1
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()       
#            plt.imshow(im, cmap = "gray")
#            plt.show()
        end = time.time()
        print("Time taken: "+ str(end - start))
        print(x,y,r)
        return((x,y,r))


    
    def detect_circles(self, frame):
    #    frame = cv2.GaussianBlur(frame, (9,9), 0)
        try:
            gray = cv2.GaussianBlur(frame,(5,5),0)
            gray = cv2.addWeighted(gray,2.0,frame,-0.5,0)
            gray = cv2.cvtColor(gray, cv2.COLOR_RGB2GRAY) 
            ret,gray = cv2.threshold(gray,self.threshold,255,self.thresholdmethod)

            circles = cv2.HoughCircles(gray,cv2.HOUGH_GRADIENT,1,1200,
                                    param1=self.param1,param2=self.param2,minRadius=self.minRadius,maxRadius=self.maxRadius)
            circles = np.uint16(np.around(circles))
            circles = circles[0,:][0]
            return gray, circles
        except:
            print("result from non_tresholded image")
            gray = cv2.GaussianBlur(frame,(5,5),0)
#            gray = cv2.addWeighted(blur,2.0,frame,-0.5,0)
            gray = cv2.cvtColor(gray, cv2.COLOR_RGB2GRAY) 
#            ret,gray = cv2.threshold(gray,180,255,cv2.THRESH_TOZERO)
            circles = cv2.HoughCircles(gray,cv2.HOUGH_GRADIENT,1,1200,
                                    param1=50,param2=30,minRadius=self.minRadius,maxRadius=self.maxRadius)
            circles = np.uint16(np.around(circles))
            circles = circles[0,:][0]
            return gray, circles
