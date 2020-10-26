import cv2
import os
import argparse
import xml.etree.ElementTree as ET
from fluo_track_create import create_tracker

def read_rect(path_):
    rects = []
    # thisFile = path_
    base = os.path.splitext(path_)[0] + '.xml'
    if not os.path.exists(base):
        return None
    if not os.path.isfile(base):
        return None
    # parse an xml file by name
    tree = ET.parse(base)
    root = tree.getroot()
    #print(root.attrib)
    for elem in root:
        left = int(elem.get('left'))
        right = int(elem.get('right'))
        top = int(elem.get('top'))
        bottom = int(elem.get('bottom'))
        rects.append([left, top, right, bottom])
    return rects

def draw_circle(rects, image):
    for i in range(len(rects)):
        x = (rects[i][0] + rects[i][2]) / 2
        y = (rects[i][1] + rects[i][3]) / 2
        r = (rects[i][2] - rects[i][0]) / 2
        cv2.circle(image, (int(x),int(y)), int(r), (0,255,0))
    return None

def view_database(path_, tracker_name):
    r = None
    tracker = None
    cv2.namedWindow("track", cv2.WINDOW_NORMAL)

    images = [os.path.join(path_, f) for f in sorted(os.listdir(path_))
              if os.path.splitext(f)[1] == '.jpg']
    print(len(images))

    for f in images:
        image = cv2.imread(f)
        rect = read_rect(f)
        if rect is not None:
            draw_circle(rect, image)
            if tracker is None:
                tracker = create_tracker(tracker_name, (rect[0][0] + rect[0][2]) / 2, (rect[0][1] + rect[0][3]) / 2)
                r = (rect[0][2] - rect[0][0]) / 2
            else:
                x, y, res = tracker.fluo_predict(image)
                cv2.circle(image, (int(x),int(y)), int(r), (0,255,255))
        cv2.imshow("track", image)
        key = cv2.waitKey(0)
        if key == 27:
            break

if __name__ == '__main__':
    cmdParser = argparse.ArgumentParser(
        description='script to view a track.\n'
                    'Author: Alex A.Telnykh\n'
                    'Date: 10.2020\n',
        formatter_class=argparse.RawDescriptionHelpFormatter)
    cmdParser.add_argument('path', help='a track directory')
    cmdParser.add_argument("-tracker", "--tracker", help="specify name of tracker. Options: null, tm, lk, sift",
                           default="null", type=str, required=True)
    cmdArgs = cmdParser.parse_args()
    path = cmdArgs.path
    the_tracker = cmdArgs.tracker
    # path = "G:\\database\\fluovisor\\track00029\\"
    view_database(path, the_tracker)
