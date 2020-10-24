"""
    abstract fluo tracker.
    should track center of mass area of interest on the images taken
    FLOUVISOR device

    author: Alex A.Telnykh
    date: october 2020
"""
class fluo_tracker(object):
    """an abstract point tracker

      any other tracker implementation must subclass it. All subclasses
      must implement 'fluo_predict', that return a predicted point
      position
    """
    def __init__(self, x, y, radius=100):
        """
        initialise fluo trackers
        :param x: x start position
        :param y: y start position
        """
        self.x = x
        self.y = y
        self.radius = radius

    def fluo_predict(self, image, blank = None):
        """
        this function calculates new positioin of the point self.x and self.y
        :param image:
        :return: coordinats of given point
        """
        raise NotImplementedError
