"""
    Lucas_Kanade  fluo tracker.
    should track center of mass area of interest on the images taken
    FLOUVISOR device

    author: Alex A.Telnykh
    date: october 2020
"""
import cv2
from fluo_track_core import fluo_tracker
import numpy as np
import math


class fluo_lk_track(fluo_tracker):
    def __init__(self, x, y, radius=100):
        super(fluo_lk_track, self).__init__(x, y, radius)
        self.features = None
        self.old_image = None
        self.new_image = None
        self.status = None
        self.p1 = None
        self.error = None
        # Parameters for lucas kanade optical flow
        self.lk_params = dict(winSize=(30, 30),
                              maxLevel=12,
                              criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

    def fluo_predict(self, image, blank=None):
        if self.features is None:
            self.old_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            self.features = cv2.goodFeaturesToTrack(self.old_image, mask=None, maxCorners=100, qualityLevel=0.001,
                                                    minDistance=15, blockSize=15)

            a = []
            for x, y in self.features[:, 0]:
                r = math.sqrt((x - self.x) * (x - self.x) + (y - self.y) * (y - self.y))
                if r < self.radius:
                    a.append([x, y])
            b = np.array(a)
            self.features = b.reshape(-1, 1, 2)

        else:
            self.new_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            if self.features.size > 0:
                self.p1, self.status, self.error = cv2.calcOpticalFlowPyrLK(self.old_image, self.new_image,
                                                                            self.features,
                                                                            None, **self.lk_params)
                # Select good points
                good_new = self.p1[self.status == 1]
                good_old = self.features[self.status == 1]
                dx = 0
                dy = 0
                for i in range(len(good_new)):
                    dx += (good_new[i][0] - good_old[i][0])
                    dy += (good_new[i][1] - good_old[i][1])

                l = np.shape(good_old)[0]
                dx = dx / l
                dy = dy / l
                if not blank is None:
                    cv2.line(blank, (int(self.x), int(self.y)), (int(self.x + dx), int(self.y + dy)), (0, 255, 255))
                self.x += dx
                self.y += dy

                # Now update the previous frame and previous points
                self.old_image = self.new_image.copy()
                self.features = good_new.reshape(-1, 1, 2)

        return self.x, self.y, True
