"""
    Template matching  fluo tracker.
    should track center of mass area of interest on the images taken
    FLOUVISOR device

    author: Alex A.Telnykh
    date: october 2020
"""
import cv2
import numpy as np
from fluo_track_core import fluo_tracker

class fluo_tm_track(fluo_tracker):
    def __init__(self, x, y, radius=100):
        super().__init__(x, y, radius)
        self.Tmpl = None

    def fluo_predict(self, image, blank=None):
        if self.Tmpl is None:
            """
                make template 
            """
            self.Tmpl = image[int(self.y - self.radius):int(self.y+self.radius), int(self.x - self.radius):int(self.x + self.radius)]
        else:
            result = cv2.matchTemplate(image, self.Tmpl, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            #print(max_val, min_val, max_loc)
            _x = max_loc[0] + self.radius
            _y = max_loc[1] + self.radius
            self.x = _x
            self.y = _y

        return self.x, self.y, True