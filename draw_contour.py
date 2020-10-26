import numpy as np
import cv2 as cv

CLR_GREEN = (0,255,0)
maxIntensity = 255.
kKernelSize = 13
frequency = 3
dictParams = {}

def contourManual(pict):
    win = 'manual (Any key: confirm; ESC: exit)'
    cv.namedWindow(win, cv.WINDOW_NORMAL)

    global dictParams
    dictParams = {"color": CLR_GREEN,
                  "pictBlanc":
                      (pict * (maxIntensity / max(np.max(pict), 1).astype(np.float32))).astype(np.uint8),
                  "poly": [],
                  "shape": pict.shape,
                  "flgDrawing": False,
                  "thickness": 1,
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
        cv.destroyWindow(win)
        return dictParams["poly"]
