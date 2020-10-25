"""
    script to draw ground truth

    author: Alex A.Telnykh
    date: october 2020
"""
import os
import cv2
import numpy as np
import argparse
from view_database import read_rect

def draw_ground_truth(path_):
    blank_image = np.zeros((920, 1280, 3), np.uint8)
    p1 = None
    p2 = None
    for f in os.listdir(path_):
        f = os.path.join(path_, f)
        baseName, ext = os.path.splitext(f)
        if ext == '.jpg':
            rects = read_rect(f)
            if rects is not None:
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
        if os.path.isdir(f):
            img = draw_ground_truth(f)
            if img is not None:
                pos = f.find('track')
                if pos > 0:
                    s = f[pos:len(f):1] + ".jpg"
                    file_name = dir_name + "\\" + s
                    cv2.imwrite(file_name, img)


if __name__ == '__main__':
    cmdParser = argparse.ArgumentParser(
        description='script to draw ground truth.\n'
                    'Author: Alex A.Telnykh\n'
                    'Date: 10.2020\n',
        formatter_class=argparse.RawDescriptionHelpFormatter)
    cmdParser.add_argument('path', help='data base directory')
    cmdArgs     = cmdParser.parse_args()

    # path = "G:\\database\\fluovisor"
    path = cmdArgs.path
    process_db(path)
