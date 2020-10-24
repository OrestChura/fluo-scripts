"""
    script to draw ground truth

    author: Alex A.Telnykh
    date: october 2020
"""
import os
import cv2
import numpy as np
from view_database import read_rect

def draw_ground_truth(path):
    blank_image = np.zeros((920, 1280, 3), np.uint8)
    p1 = None
    p2 = None
    for f in os.listdir(path):
        f = os.path.join(path, f)
        baseName, ext = os.path.splitext(f)
        if ext == '.jpg':
            rects = read_rect(f)
            if not rects is None:
                if p1 is None:
                    x = (rects[0][0] + rects[0][2]) / 2
                    y = (rects[0][1] + rects[0][3]) / 2
                    p2 = (int(x), int(y))
                    p1 = p2
                else:
                    p1 = p2
                    x = (rects[0][0] + rects[0][2]) / 2
                    y = (rects[0][1] + rects[0][3]) / 2
                    p2 = (int(x), int(y))
                    cv2.line(blank_image, p1, p2, (0, 255, 0))
    return blank_image


def process_db(dir_name):
    for f in os.listdir(dir_name):
        f = os.path.join(dir_name, f)
        baseName, ext = os.path.splitext(f)
        if os.path.isdir(f):
            img = draw_ground_truth(f)
            if not img is None:
                pos = f.find('track')
                if pos > 0:
                    s = f[pos:len(f):1] + ".jpg"
                    file_name = dir_name + "\\" + s
                    cv2.imwrite(file_name, img)


if __name__ == '__main__':
    path = "G:\\database\\fluovisor"
    process_db(path)
