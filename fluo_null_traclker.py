"""
    null  fluo tracker.
    should track center of mass area of interest on the images taken
    FLOUVISOR device

    author: Alex A.Telnykh
    date: october 2020
"""
from fluo_track_core import fluo_tracker


class fluo_null_track(fluo_tracker):
    """
    a NULL tracker. This tracker don't change start point x,y
    """

    def __init__(self, x, y, radius=100):
        super().__init__(x, y, radius)

    def fluo_predict(self, image, blank=None):
        """
        :param image: next image in the series
        :param blank: image to draw trajectory
        :return: initial point x,y
        """
        return self.x, self.y, True
