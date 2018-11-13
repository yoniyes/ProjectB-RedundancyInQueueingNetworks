import numpy as np
import math

##
# This class is a building block for stats. See example below.
# It's recommended that this should be as a member of a user-defined statistics class.
##
class Stats:
    """Class for storing statistics."""

    ##
    # Initialize a statistics instance.
    # Gets @windowSize in order to init a sliding window to store queue network history.
    # Gets an optional user-defined stats class for fine-grained statistical analysis.
    # Notice: the user-defined stats class functions can assume it can get as a parameter an array that is the window.
    # Another way to achieve this is to create a new class that instantiates a StatsCollector as a member.
    # The initial window will be filled with 0's.
    ##
    def __init__(self, windowSize=10000):
        if windowSize <= 0:
            raise Exception("Invalid window size of" + str(windowSize))
        self.window = np.zeros(windowSize)

    ##
    # Reset the stats window.
    ##
    def reset(self, windowSize=0):
        size = self.getWindowSize()
        if windowSize > 0:
            size = windowSize
        self.window = np.zeros(size)

    ##
    # Gets the window size.
    ##
    def getWindowSize(self):
        return len(self.window)

    ##
    # Gets the window average.
    ##
    def getAverage(self):
        return np.mean(self.window)

    ##
    # Gets the window standard deviation.
    ##
    def getStdv(self):
        return math.sqrt(np.var(self.window))

    ##
    # Gets the window variance.
    ##
    def getVar(self):
        return np.var(self.window)

    ##
    # Slides the window by 1 and inserts a new value.
    ##
    def insert(self, value):
        self.window = np.delete(np.append(self.window, value), 0)

    ##
    # Get the whole window history.
    ##
    def getWindow(self):
        return self.window


##
# This should be as a member of a user-defined statistics class.
##
class StatsCollector:
    """Class for storing statistics and information about a queue network."""

    def __init__(self, windowSizes=[]):
        _sizes = windowSizes
        if not _sizes:
            _sizes = [10000]
        self.stats = [Stats(windowSize=size) for size in _sizes]

    def getStatNumber(self, num):
        if num < 0 or num >= len(self.stats):
            return None
        return self.stats[num]

    def reset(self, windowSizes=[]):
        _sizes = windowSizes
        if not _sizes:
            _sizes = [0]*len(self.stats)
        [self.stats[i].reset(windowSize=_sizes[i]) for i in range(len(_sizes))]
