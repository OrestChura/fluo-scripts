
import numpy as np
import cv2 as cv



img = cv.imread('G:\\database\\fluovisor\\2.png')
gray= cv.cvtColor(img,cv.COLOR_BGR2GRAY)
sift = cv.SIFT_create(500,4,0.05)
kp = sift.detect(gray,None)
print(kp)
img=cv.drawKeypoints(gray,kp,img)
cv.imwrite('sift_keypoints.jpg',img)
cv.imshow('result',img)
cv.waitKey(0)

