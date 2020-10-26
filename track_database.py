import os
import argparse
import numpy as np
import cv2
from draw_contour import contourManual
from fluo_track_create import create_tracker

def track_database(path_, tracker_name):
    images = [os.path.join(path_, f) for f in sorted(os.listdir(path_))
              if os.path.splitext(f)[1] == '.jpg']
    print(len(images))
    tracker = None
    contour = []
    x_0 = y_0 = None
    cv2.namedWindow("track", cv2.WINDOW_NORMAL)
    for f in images:
        image = cv2.imread(f)
        if tracker is None:
            contour = np.array(contourManual(image))
            if contour.any():
                rect = list(cv2.boundingRect(contour))
                rect[2] = rect[0] + rect[2] - 1
                rect[3] = rect[1] + rect[3] - 1
                x_0 = (rect[0] + rect[2]) / 2
                y_0 = (rect[1] + rect[3]) / 2
                tracker = create_tracker(tracker_name, x_0, y_0)
                if tracker is None:
                    raise Exception("cannot create tracker: " + tracker_name)
                cv2.polylines(image, [np.array(contour, np.int32)], True, (0,255,255), 1)
            else:
                raise Exception("Contour is not given")
        else:
            x, y, _ = tracker.fluo_predict(image)
            dx = x - x_0
            dy = y - y_0
            contour_cur = [[x_c + dx, y_c + dy] for [x_c, y_c] in contour]
            cv2.polylines(image, [np.array(contour_cur, np.int32)], True, (0, 255, 255), 1)
        cv2.imshow("track", image)
        key = cv2.waitKey(0)
        if key == 27:
            break

if __name__ == '__main__':
    cmdParser = argparse.ArgumentParser(
        description='script to track a series by one of implemented trackers.\n'
                    'Authors: Alex A.Telnykh & Orest Chura\n'
                    'Date: 10.2020\n',
        formatter_class=argparse.RawDescriptionHelpFormatter)
    cmdParser.add_argument('path', help='a track directory')
    cmdParser.add_argument("-tracker", "--tracker", help="specify name of tracker. Options: null, tm, lk, sift",
                           default="null", type=str, required=True)
    cmdArgs = cmdParser.parse_args()
    path = cmdArgs.path
    the_tracker = cmdArgs.tracker
    # path = "G:\\database\\fluovisor\\track00029\\"
    track_database(path, the_tracker)
