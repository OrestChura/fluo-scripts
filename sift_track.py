import os
import cv2
import math
import numpy as np
from view_database import read_rect, draw_circle


class sift_traker(object):
    def __init__(self, image, rect):
        self.mask = np.zeros((960, 1280, 3), np.uint8)
        self.radius = 200
        self.rect = rect[0]
        self.cx = 0.5 * (self.rect[0] + self.rect[2])
        self.cy = 0.5 * (self.rect[1] + self.rect[3])
        self._cx = self.cx
        self._cy = self.cy
        cv2.circle(self.mask, (int(self.cx),int(self.cy)), self.radius,(255,255,255), -1)
        #cv2.rectangle(self.mask, (int(self.cx - self.radius), int(self.cy - self.radius)),
        #              (int(self.cx + self.radius), int(self.cy + self.radius)), (1, 1, 1), -1)
        self.mask = cv2.cvtColor(self.mask, cv2.COLOR_RGB2GRAY)
        #cv2.imwrite("mask.jpg", self.mask)
        self.sift = cv2.SIFT_create(200, 3, 0.01)
        self.fp, self.det = self.sift.detectAndCompute(image, self.mask)
        self.bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=False)
        self.image = image.copy()
    def nearlest_match(self, matches, kp):
        key = matches[0]
        min_d = 1000000
        idx = 0
        mi = 100000
        for match in matches:
            pt = kp[match.trainIdx].pt
            d = math.sqrt((self.cx - pt[0])*(self.cx - pt[0])+(self.cy - pt[1])*(self.cy - pt[1]))
            if d < min_d:
                min_d = d
                mi = idx
            idx += 1
        if matches[mi].distance > 100:
            return matches[0]
        return matches[mi]
    def track(self, image):
        kp, det = self.sift.detectAndCompute(image, self.mask)
        matches = self.bf.match(self.det, det)
        matches = sorted(matches, key=lambda x: x.distance)
        m = matches[0]#self.nearlest_match(matches, kp)
        print(m.distance)
        if matches[0].distance > 200:
            print("skip frame")
        else:
            pt1 = self.fp[m.queryIdx].pt
            pt2 = kp[m.trainIdx].pt
            dx = pt2[0] - pt1[0]
            dy = pt2[1] - pt1[1]
            self.cx = self.cx + dx
            self.cy = self.cy + dy
            self.mask = np.zeros((960, 1280, 3), np.uint8)
            cv2.circle(self.mask, (int(self.cx), int(self.cy)), self.radius, (255, 255, 255), -1)
            self.mask = cv2.cvtColor(self.mask, cv2.COLOR_RGB2GRAY)
            self.fp, self.det = self.sift.detectAndCompute(image, self.mask)

#        print(matches[0].distance)
#       img3 = cv2.drawMatches(self.image, self.fp, image, kp, matches[:1], image)
#        cv2.imshow("match", img3)

    def draw(self, image):
        cv2.rectangle(image, (int(self.rect[0]), int(self.rect[1])),
                      (int(self.rect[2]), int(self.rect[3])), (255, 255, 0))
        w = (self.rect[2] - self.rect[0]) / 2
        h = (self.rect[3] - self.rect[1]) / 2
        cv2.rectangle(image, (int(self.cx - w), int(self.cy - h)),
                      (int(self.cx + w), int(self.cy + h)), (255, 255, 255))
        cv2.circle(image, (int(self.cx), int(self.cy)), self.radius, (255, 255, 255))
        cv2.circle(image, (int(self.cx), int(self.cy)), self.radius, (255, 255, 255))
        image = cv2.drawKeypoints(image, self.fp, image)


def view_track(path):
    tracker = None
    for f in os.listdir(path):
        f = os.path.join(path, f)
        baseName, ext = os.path.splitext(f)
        if ext == '.jpg':
            rect = read_rect(f)
            image = cv2.imread(f)
            if tracker is None:
                tracker = sift_traker(image, rect)
            else:
                tracker.track(image)
                tracker.draw(image)
            if not rect is None:
                draw_circle(rect, image)
            cv2.imshow("track", image)
            key = cv2.waitKey(0)
            if key == 27:
                break


if __name__ == '__main__':
    path = "G:\\database\\fluovisor\\track00029\\"
    view_track(path)
