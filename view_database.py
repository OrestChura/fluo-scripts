import cv2
import os
import xml.etree.ElementTree as ET
from fluo_lk_tracker import fluo_lk_track
from fluo_null_traclker import fluo_null_track
from fluo_tm_tracker import fluo_tm_track

def file_count(path):
    count = 0
    for f in os.listdir(path):
        baseName, ext = os.path.splitext(f)
        if ext == '.jpg':
            count = count + 1
    return count

def read_rect(path):
    rects = []
    thisFile = path
    base = os.path.splitext(path)[0]+'.xml'
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
        r = (rects[i][2] - rects[i][0] ) / 2
        cv2.circle(image, (int(x),int(y)), int(r), (0,255,0))
    return None

def view_database(path):
    print(file_count(path))
    r = None
    tracker = None
    for f in os.listdir(path):
        f = os.path.join(path, f)
        baseName, ext = os.path.splitext(f)
        if ext == '.jpg':
            rect = read_rect(f)
            image = cv2.imread(f)
            if tracker is None:
                tracker = fluo_tm_track((rect[0][0] + rect[0][2]) / 2, (rect[0][1] + rect[0][3]) / 2)
                r = (rect[0][2] - rect[0][0] ) / 2
            else:
                x,y, res = tracker.fluo_predict(image)
                cv2.circle(image, (int(x), int(y)), int(r), (0, 255, 255))
            if not rect is None:
                draw_circle(rect, image)
            cv2.imshow("track", image)
            key = cv2.waitKey(0)
            if key == 27:
                break

if __name__ == '__main__':
    path = "G:\\database\\fluovisor\\track00029\\"
    view_database(path)
