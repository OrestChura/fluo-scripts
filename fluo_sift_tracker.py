"""
    SIFT  fluo tracker.
    should track center of mass area of interest on the images taken
    FLOUVISOR device

    author: Alex A.Telnykh
    date: october 2020
"""

import cv2
from fluo_track_core import fluo_tracker
import numpy as np
import math


class fluo_sift_track(fluo_tracker):
    def __init__(self, x, y, radius=100):
        super(fluo_sift_track, self).__init__(x, y, radius)
        self.mask = np.zeros((960, 1280, 3), np.uint8)
        self._cx = self.x
        self._cy = self.y
        cv2.circle(self.mask, (int(self.x), int(self.y)), self.radius, (255, 255, 255), -1)
        self.mask = cv2.cvtColor(self.mask, cv2.COLOR_RGB2GRAY)
        self.sift = cv2.SIFT_create(200, 3, 0.02)
        self.bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=False)
        self.fp = None
        self.det = None
        self.image = None

    #        self.fp, self.det = self.sift.detectAndCompute(image, self.mask)
    #        self.image = image.copy()

    def nearlest_match(self, matches, kp):
        key = matches[0]
        min_d = 1000000
        idx = 0
        mi = 100000
        for match in matches:
            pt = kp[match.trainIdx].pt
            d = math.sqrt((self.x - pt[0])*(self.x - pt[0])+(self.y - pt[1])*(self.y - pt[1]))
            if d < min_d:
                min_d = d
                mi = idx
            idx += 1
        if matches[mi].distance > 100:
            return matches[0]
        return matches[mi]

    def fluo_predict(self, image, blank=None):
        if self.image is None:
            self.fp, self.det = self.sift.detectAndCompute(image, self.mask)
            self.image = image.copy()
        else:
            kp, det = self.sift.detectAndCompute(image, self.mask)
            matches = self.bf.match(self.det, det)
            matches = sorted(matches, key=lambda x: x.distance)
            m = self.nearlest_match(matches, kp)
            #print(m.distance)
            if matches[0].distance > 200:
                return 0,0, False
            else:
                pt1 = self.fp[m.queryIdx].pt
                pt2 = kp[m.trainIdx].pt
                dx = pt2[0] - pt1[0]
                dy = pt2[1] - pt1[1]
                if blank is not None:
                    cv2.line(blank, (int(self.x), int(self.y)), (int(self.x + dx), int(self.y + dy)), (0, 255, 255))

                self.x = self.x + dx
                self.y = self.y + dy
                self.mask = np.zeros((960, 1280, 3), np.uint8)
                cv2.circle(self.mask, (int(self.x), int(self.y)), self.radius, (255, 255, 255), -1)
                self.mask = cv2.cvtColor(self.mask, cv2.COLOR_RGB2GRAY)
                self.fp, self.det = self.sift.detectAndCompute(image, self.mask)
        return self.x, self.y, True
