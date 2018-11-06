import numpy as np


class StatsCollector:
    """Class for storing statistics and information about a queue network."""

    ##
    # Initialize a statistics instance.
    # Gets @windowSize in order to init a sliding window to store queue network history.
    # Gets an optional user-defined stats class for fine-grained statistical analysis.
    # Notice: the user-defined stats class functions can assume it can get as a parameter an array that is the window.
    # Another way to achieve this is to create a new class that instantiates a StatsCollector as a member.
    # The initial window will be filled with 0's.
    ##
    def __init__(self, windowSize=1000, userDefinedStatsClass=None):
        if windowSize <= 0:
            raise Exception("Invalid window size of" + str(windowSize))
        self.window = np.zeros(windowSize)
        self.userDefinedStats = userDefinedStatsClass

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
        return np.average(self.window)

    ##
    # Gets the window standard deviation.
    ##
    def getStdv(self):
        return np.std(self.window)

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
    # Access the user-defined stats class.
    ##
    def getUserDefinedStats(self):
        return self.userDefinedStats
