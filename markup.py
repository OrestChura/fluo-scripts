import os
import numpy as np
import cv2 as cv
import argparse
import xml.etree.ElementTree as ET

CLR_GREEN = (0,255,0)
maxIntensity = 255.
kKernelSize = 13
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
                  "thickness": 3,
                  "kernelSize": kKernelSize}

    dictParams["kernel"] = np.ones((dictParams["kernelSize"], dictParams["kernelSize"]), np.uint8)
    if not (len(dictParams["pictBlanc"].shape) == 3 and dictParams["pictBlanc"].shape[2] == 3): # Gray picture
        dictParams["pictBlanc"] = cv.cvtColor(dictParams["pictBlanc"], cv.COLOR_GRAY2RGB)
    dictParams["pictShow"] = dictParams["pictBlanc"]

    def onMouse(event, x, y, _flags, _param):
        global dictParams
        if event == cv.EVENT_LBUTTONDOWN:
            dictParams["flgDrawing"] = True
            dictParams["poly"] = dictParams["poly"] + [[x, y]]
            dictParams["pictShow"] = dictParams["pictBlanc"]
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
            dictParams["pictShow"] = dictParams["pictBlanc"]
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

def markupSeries(subdir):
    images = [os.path.join(subdir, f) for f in os.listdir(subdir)
              if os.path.splitext(f)[1] == '.jpg']
    numImages = len(images)
    i = 0
    for im in images:
        i = i + 1
        if (i - 1) % frequency == 0:
            print('\t\tPoint ' + str((i - 1) // frequency + 1) + '/'
                  + str((numImages - 1) // frequency + 1))
            xmlFile = os.path.splitext(im)[0] + '.xml'
            npyFile = os.path.splitext(im)[0] + '.npy'
            if not os.path.exists(npyFile) and not os.path.isfile(npyFile):
                image = cv.imread(im)
                contour = np.array(contourManual(image))
                np.save(npyFile, contour)
            else:
                ans = input('Contour drawn already. Do you want to draw new?' + ' (y/n)\n')
                while ans != 'y' and ans != 'n':
                    ans = input('Incorrect input. Do you want to draw new?' + ' (y/n)\n')
                if ans is 'y':
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

if __name__ == '__main__':
    cmdParser = argparse.ArgumentParser(
        description='script to manually define ground truth'
                    'on a sequence of frames.\n'
                    'Author: Orest Chura\n'
                    'Date: 2019-2020\n',
        formatter_class=argparse.RawDescriptionHelpFormatter)
    cmdParser.add_argument('path', help='data base directory')
    cmdArgs     = cmdParser.parse_args()

    # directory = "G:\\database\\fluovisor"
    directory = cmdArgs.path
    print("Marking-up database in " + directory)
    for path in [os.path.join(directory, f) for f in os.listdir(directory)
                 if os.path.isdir(os.path.join(directory, f))]:
        print("\tGetting into " + path)
        markupSeries(path)
