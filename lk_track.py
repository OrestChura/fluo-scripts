import os
import math
import cv2
import numpy as np
from view_database import read_rect, draw_circle


class lk_tracker(object):
    def __init__(self, image, rect):
        self.old_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        self.fp = cv2.goodFeaturesToTrack(self.old_image, mask=None, maxCorners=200, qualityLevel=0.001, minDistance=9,
                                          blockSize=40)

        self.radius = 150
        self.rect = rect[0]
        self.cx = 0.5 * (self.rect[0] + self.rect[2])
        self.cy = 0.5 * (self.rect[1] + self.rect[3])
        a = []
        for x, y in self.fp[:, 0]:
            r = math.sqrt((x - self.cx) * (x - self.cx) + (y - self.cy) * (y - self.cy))
            if r < self.radius:
                a.append([x, y])
        b = np.array(a)
        self.fp = b.reshape(-1,1,2)
        self.new_image = None
        self.lk_params = dict(winSize=(30, 30),
                              maxLevel=4,
                              criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

        self.p1 = None
        self.p2 = None
        self.status = None
        self.error = None

    def track(self, image):
        self.new_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        if self.fp.size > 0:
            self.p1, self.status, self.error = cv2.calcOpticalFlowPyrLK(self.old_image, self.new_image, self.fp,
                                                                    None, **self.lk_params)
            self.old_image = self.new_image.copy()

            good_new = self.p1[self.status == 1]
            good_old = self.fp[self.status == 1]

            dx = 0
            dy = 0
            for i in range(len(good_new)):
                dx += (good_new[i][0] - good_old[i][0])
                dy += (good_new[i][1] - good_old[i][1])

            l = np.shape(good_old)[0]
            dx = dx / l
            dy = dy / l

            self.cx += dx
            self.cy += dy

            self.p2 = self.fp.copy()
            self.fp = good_new.reshape(-1, 1, 2)



    def draw(self, image):
        cv2.rectangle(image, (int(self.rect[0]), int(self.rect[1])),
                      (int(self.rect[2]), int(self.rect[3])), (255, 255, 0))
        w = (self.rect[2] - self.rect[0]) / 2
        h = (self.rect[3] - self.rect[1]) / 2
        cv2.rectangle(image, (int(self.cx - w), int(self.cy - h)),
                      (int(self.cx + w), int(self.cy + h)), (255, 255, 255))
        cv2.circle(image, (int(self.cx), int(self.cy)), self.radius, (255, 255, 255))
        if self.p1 is not None:
            i = 0
            for x, y in self.p1[:, 0]:
                xy = self.p2[i][0]
                cv2.circle(image, (x, y), 3, (0, 255, 255), -1)
                cv2.line(image, (x, y), (xy[0], xy[1]), (0, 0, 255))
                i += 1
        if self.p2 is not None:
            for x, y in self.p2[:, 0]:
                cv2.circle(image, (x, y), 3, (0, 255, 0), -1)


def view_track(path):
    tracker = None
    for f in os.listdir(path):
        f = os.path.join(path, f)
        baseName, ext = os.path.splitext(f)
        if ext == '.jpg':
            rect = read_rect(f)
            image = cv2.imread(f)
            if tracker is None:
                tracker = lk_tracker(image, rect)
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
