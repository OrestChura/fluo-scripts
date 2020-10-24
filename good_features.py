import cv2
import os
from view_database import read_rect, draw_circle

def draw_fearutes(img, p):
    if p is not None:
        for x, y in p[:, 0]:
            cv2.circle(img, (x, y), 3, (0,255,255), -1)

def view_features(path):
    for f in os.listdir(path):
        f = os.path.join(path, f)
        baseName, ext = os.path.splitext(f)
        if ext == '.jpg':
            rect = read_rect(f)
            image = cv2.imread(f)
            feature_points = cv2.goodFeaturesToTrack(cv2.cvtColor(image, cv2.COLOR_RGB2GRAY), mask=None, maxCorners=200, qualityLevel=0.002, minDistance=15, blockSize=15)
            draw_fearutes(image, feature_points)
            if not rect is None:
                draw_circle(rect, image)
            cv2.imshow("track", image)
            key = cv2.waitKey(0)
            if key == 27:
                break

if __name__ == '__main__':
    path = "G:\\database\\fluovisor\\track00019\\"
    view_features(path)
