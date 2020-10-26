from fluo_null_tracker import fluo_null_track
from fluo_lk_tracker import fluo_lk_track
from fluo_sift_tracker import fluo_sift_track
from fluo_tm_tracker import fluo_tm_track

def create_tracker(name, x, y):
    if name == 'null':
        return fluo_null_track(x, y)
    elif name == 'lk':
        return fluo_lk_track(x, y)
    elif name == 'sift':
        return fluo_sift_track(x, y, 200)
    elif name == 'tm':
        return fluo_tm_track(x, y)
    else:
        return None
