import os
import numpy as np
import cv2 as cv
import argparse
import xml.etree.ElementTree as ET

CLR_GREEN = (0,255,0)
maxIntensity = 255.
frequency = 3
dictParams = {}

def contourManual(pict):
    win = 'manual'
    cv.namedWindow(win, cv.WINDOW_NORMAL)

    global dictParams
    dictParams = {"color": CLR_GREEN,
                  "pictBlanc":
                      (pict * (maxIntensity / max(np.max(pict), 1).astype(np.float32))).astype(np.uint8),
                  "poly": [],
                  "shape": pict.shape,
                  "flgDrawing": False,
                  "thickness": 3}

    if not (len(dictParams["pictBlanc"].shape) == 3 and dictParams["pictBlanc"].shape[2] == 3): # Gray picture
        dictParams["pictBlanc"] = cv.cvtColor(dictParams["pictBlanc"], cv.COLOR_GRAY2RGB)
    dictParams["pictShow"] = dictParams["pictBlanc"].copy()

    def onMouse(event, x, y, _flags, _param):
        global dictParams
        if event == cv.EVENT_LBUTTONDOWN:
            dictParams["flgDrawing"] = True
            dictParams["poly"] = dictParams["poly"] + [[x, y]]
            dictParams["pictShow"] = dictParams["pictBlanc"].copy()
            cv.polylines(dictParams["pictShow"], [np.array(dictParams["poly"], np.int32)],
                         False, dictParams["color"], dictParams["thickness"])
            cv.imshow(win, dictParams["pictShow"])
        elif event == cv.EVENT_MOUSEMOVE:
            if dictParams['flgDrawing'] is True:
                dictParams["poly"] = dictParams["poly"] + [[x, y]]
                cv.line(dictParams["pictShow"],
                        tuple(dictParams["poly"][-2]),
                        tuple(dictParams["poly"][-1]),
                        dictParams["color"], dictParams["thickness"])
                cv.imshow(win, dictParams["pictShow"])
        elif event == cv.EVENT_LBUTTONUP:
            if dictParams['flgDrawing'] is True:
                dictParams["flgDrawing"] = False
                cv.line(dictParams["pictShow"], tuple(dictParams["poly"][0]), tuple(dictParams["poly"][-1]),
                        dictParams["color"], dictParams["thickness"])
                cv.imshow(win, dictParams["pictShow"])
        elif event == cv.EVENT_RBUTTONUP:
            dictParams["poly"] = []
            dictParams["flgDrawing"] = False
            dictParams["pictShow"] = dictParams["pictBlanc"].copy()
            cv.imshow(win, dictParams["pictShow"])

    key = 0
    while not dictParams["poly"]:
        cv.imshow(win, dictParams["pictShow"])
        cv.setMouseCallback(win, onMouse)
        key = cv.waitKey(0)
        if key == 27:
            break
    if key == 27:
        exit(0)
    else:
        return dictParams["poly"]

def markupTrack(track, start_number=0):
    start_number = max(start_number, 0)
    i = start_number * frequency        # Number of image to start to mark-up
    images = sorted([os.path.join(track, f) for f in os.listdir(track)
                     if os.path.splitext(f)[1] == '.jpg'])[i:] # Cut first images if i > 0
    numImages = len(images)
    for im in images:
        i = i + 1
        if (i - 1) % frequency == 0: # Every <frequency> frame we mark it up
            print('\t\tPoint ' + str((i - 1) // frequency + 1) + '/'
                  + str((numImages - 1) // frequency + 1))
            xmlFile = os.path.splitext(im)[0] + '.xml'
            npyFile = os.path.splitext(im)[0] + '.npy'
            if not os.path.exists(npyFile) and not os.path.isfile(npyFile):
                image = cv.imread(im)
                contour = np.array(contourManual(image))
                np.save(npyFile, contour)
            else:
                ans = input('\t\tContour drawn already. Do you want to draw new?' + ' (y/n)\n')
                while ans != 'y' and ans != 'n':
                    ans = input('\t\tIncorrect input. Do you want to draw new?' + ' (y/n)\n')
                if ans == 'y':
                    image = cv.imread(im)
                    contour = np.array(contourManual(image))
                    np.save(npyFile, contour)
                else:
                    contour = np.load(npyFile)
                del ans

            rect = cv.boundingRect(contour)
            root = ET.Element("rects")
            rectElem = ET.SubElement(root, "rect")
            rectElem.set("top", str(rect[0]))
            rectElem.set("left", str(rect[1]))
            rectElem.set("bottom", str(rect[0] + rect[2] - 1))
            rectElem.set("right", str(rect[1] + rect[3] - 1))
            tree = ET.ElementTree(root)
            tree.write(xmlFile)

def markupIDE(tracks):
    idx = 0
    while True:
        print('\tCurrent track: ', tracks[idx])
        files = sorted([f for f in os.listdir(tracks[idx]) if os.path.isfile(os.path.join(tracks[idx], f))])
        numImages = len([i for i in files if os.path.splitext(i)[1] == '.jpg'])
        numNpys = len([i for i in files if os.path.splitext(i)[1] == '.npy'])
        print('\tTotal images: ', str(numImages))
        total_markups = (numImages - 1) // frequency + 1
        print('\tMarkups done: ', str(numNpys), '/', total_markups)
        ans = ''
        while not (ans in ['x', 'p', 'n', 'r', 'c'] or ans.isdigit() or (ans[1:].isdigit() and ans[0] == 't')):
            ans = input('\tp - previous track, n - next track, '
                        'r - reset markup for the current track, c - continue markup of the current track, '
                        '<int> - zero-based number of markup to begin with for the current track, '
                        't<int> - zero-based number of track to go to, x - exit. Your action: \n')
        if ans == 'x':
            exit(0)
        elif ans == 'p':
            idx = max(idx - 1, 0)
        elif ans == 'n':
            idx = min(idx + 1, len(tracks) - 1)
        elif ans[0] == 't' and ans[1:].isdigit():
            idx = min(max(int(ans[1:]), 0), len(tracks) - 1)
        elif ans == 'r':
            for f in ([i for i in files if os.path.splitext(i)[1] == '.npy'] +
                      [i for i in files if os.path.splitext(i)[1] == '.xml']):
                os.remove(f)
        elif ans == 'c':
            return idx, numNpys
        elif ans.isdigit():
            return idx, min(int(ans), total_markups - 1)
        else:
            exit(-1)

def findFirstUnmarked(tracks):
    for idx in range(len(tracks)):
        files = sorted([f for f in os.listdir(tracks[idx]) if os.path.isfile(os.path.join(tracks[idx], f))])
        numImages = len([i for i in files if os.path.splitext(i)[1] == '.jpg'])
        numNpys = len([i for i in files if os.path.splitext(i)[1] == '.npy'])
        total_markups = (numImages - 1) // frequency + 1
        if numNpys < total_markups:
            return idx, numNpys


if __name__ == '__main__':
    cmdParser = argparse.ArgumentParser(
        description='script to manually define ground truth'
                    'on all frames sequences in the data base.\n'
                    'Author: Orest Chura\n'
                    'Date: 2019-2020\n',
        formatter_class=argparse.RawDescriptionHelpFormatter)
    cmdParser.add_argument('path', help='data base directory')
    cmdParser.add_argument('--search', action='store_true', help='set to choose the directory to begin with')
    cmdParser.add_argument('--continuing', action='store_true', help='set to continue markup')
    cmdArgs     = cmdParser.parse_args()

    # directory = "G:\\database\\fluovisor"
    directory = cmdArgs.path
    to_search = cmdArgs.search
    to_continue = cmdArgs.continuing
    print("Marking-up database in " + directory)
    tracks_ = sorted([os.path.join(directory, t) for t in os.listdir(directory)
                      if os.path.isdir(os.path.join(directory, t)) and t.find('track') != -1])

    markup_number_ = 0
    if to_continue:
        to_search = False
        idx_, markup_number_ = findFirstUnmarked(tracks_)
        tracks_ = tracks_[idx_:]

    if to_search:
        idx_, markup_number_ = markupIDE(tracks_)
        tracks_ = tracks_[idx_:]

    for path in tracks_:
        print("\tGetting into " + path)
        markupTrack(path, markup_number_)
        markup_number_ = 0
