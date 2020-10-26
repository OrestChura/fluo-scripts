import os
import time
import math
import cv2
import argparse
from view_database import read_rect
from draw_gt import draw_ground_truth
from fluo_track_create import create_tracker

the_tracker = "null"

def calc_loss(x, y, x1, y1):
    return math.sqrt((x1 - x) * (x1 - x) + (y1 - y) * (y1 - y))


def get_loss(dir_name, tracker_name):
    loss_min = 1000
    loss_max = 0
    loss_average = 0
    items_count = 0
    tracker = None
    blank_image = draw_ground_truth(dir_name)
    t = 0
    num_skip = 0
    for f in [os.path.join(dir_name, f) for f in sorted(os.listdir(dir_name))
              if os.path.splitext(f)[1] == '.jpg']:
        rects = read_rect(f)
        if rects is not None:
            items_count += 1
            x = (rects[0][0] + rects[0][2]) / 2
            y = (rects[0][1] + rects[0][3]) / 2
            if tracker is None:
                print("try to create tracker: " + the_tracker)
                tracker = create_tracker(tracker_name, x, y)
                if tracker is None:
                    raise Exception("cannot create tracker: " + tracker_name)
                print("done")
            else:
                image = cv2.imread(f)
                t_start = time.time()
                _x, _y, res = tracker.fluo_predict(image, blank_image)
                if res:
                    t_end = time.time()
                    loss = calc_loss(x, y, _x, _y)
                    if loss_max < loss:
                        loss_max = loss
                    if loss_min > loss:
                        loss_min = loss
                    loss_average += loss
                    t += (t_end - t_start)
                else:
                    num_skip += 1
    if items_count != 0:
        loss_average /= items_count
        t /= items_count
        return items_count, loss_min, loss_max, loss_average, blank_image, t, num_skip
    else:
        return 0, 0, 0, 0, None, 0, 0


def process_database(dir_name):
    file_name = os.path.join(dir_name, the_tracker + ".txt")
    with open(file_name, "w") as file_out:
        for f in os.listdir(dir_name):
            f = os.path.join(dir_name, f)
            if os.path.isdir(f):
                try:
                    ic, lmin, lmax, lavg, img, t, sk = get_loss(f, the_tracker)
                except Exception as e:
                    print(e)
                    exit()
                print(f, "{:8.3f}".format(ic), "{:8.3f}".format(lmin), "{:8.3f}".format(lmax), "{:8.3f}".format(lavg), "{0:5.0f}".format(1000*t),"{0:8.0f}".format(sk))
                print(f, "{:8.3f}".format(ic), "{:8.3f}".format(lmin), "{:8.3f}".format(lmax), "{:8.3f}".format(lavg), "{0:5.0f}".format(1000*t),"{0:8.0f}".format(sk),
                      file=file_out)
                if img is not None:
                    pos = f.find('track')
                    if pos > 0:
                        s = f[pos:len(f):1] + ".jpg"
                        file_name = dir_name + "\\" + s
                        cv2.imwrite(file_name, img)

    file_out.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="FLUO LOSS RESEARCH")
    parser.add_argument('path', help='data base directory')
    parser.add_argument("-tracker", "--tracker", help="specify name of tracker", default="null", type=str, required=True)
    args = parser.parse_args()
    the_tracker = args.tracker
    # path = 'G:\\database\\fluovisor\\'
    path = args.path
    process_database(path)
