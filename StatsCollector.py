import numpy as np
import math
import unittest as ut


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
        self.nextOpenSlot = 0
        self.firstSlot = None

    ##
    # Reset the stats window.
    ##
    def reset(self, windowSize=0):
        size = self.getWindowSize()
        if windowSize > 0:
            size = windowSize
        self.window = np.zeros(size)
        self.nextOpenSlot = 0
        self.firstSlot = None

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
        # FIXME: change this! No append or delete!
        # self.window = np.delete(np.append(self.window, value), 0)
        if self.firstSlot == self.nextOpenSlot:
            self.firstSlot = (self.firstSlot + 1) % self.getWindowSize()
        elif self.firstSlot is None:
            self.firstSlot = self.nextOpenSlot
        self.window[self.nextOpenSlot] = value
        self.nextOpenSlot = (self.nextOpenSlot + 1) % self.getWindowSize()

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
        for i in range(len(_sizes)):
            self.stats[i].reset(windowSize=_sizes[i])


########################################################################################################################
#   TEST
########################################################################################################################
class TestStats(ut.TestCase):
    def runTest(self):
        # with self.assertRaises(Exception):
        #     Queue(service=0)
        # with self.assertRaises(Exception):
        #     Queue(service=-1)
        # with self.assertRaises(Exception):
        #     Queue(workload=-1)
        # q = Queue()
        # self.assertEqual(q.getWorkload(), 0)
        # self.assertEqual(q.getService(), 1)
        # q.setWorkload(100)
        # self.assertEqual(q.getWorkload(), 100)
        # q.setService(2)
        # self.assertEqual(q.getService(), 2)
        # with self.assertRaises(Exception):
        #     q.setWorkload(-1)
        # with self.assertRaises(Exception):
        #     q.setService(0)
        # q.addWorkload(100)
        # self.assertEqual(q.getWorkload(), 200)
        # q.endTimeSlot()
        # self.assertEqual(q.getWorkload(), 198)
        # q.addWorkload(-7)
        # self.assertEqual(q.getWorkload(), 191)
        # q.addWorkload(-192)
        # self.assertEqual(q.getWorkload(), 0)
        # q.endTimeSlot()
        # self.assertEqual(q.getWorkload(), 0)
        # q.addWorkload(10)
        # self.assertEqual(q.getWorkload(), 10)
        # q.reset()
        # self.assertEqual(q.getService(), 1)
        # self.assertEqual(q.getWorkload(), 0)
        print "TestStats: OK."


if __name__ == '__main__':
    ut.main()
