from Queue import Queue
from StatsCollector import StatsCollector
import numpy as np


########################################################################################################################
#   USER DEFINED STATS
########################################################################################################################
# TODO: This should probably be an abstract interface...
class RunningAverageStats:
    """Collects running average workload for a network."""

    def __init__(self, size):
        self.size = size
        self.values = []

    def insert(self, args):
        window = args[0]
        time = args[1]
        if time > 0 and time % self.size == 0:
            self.values.append(float(np.sum(window)) / float(self.size))

    def get(self):
        return self.values

    def reset(self, windowSize=0):
        if windowSize > 0:
            self.size = windowSize
        self.values = []

    def name(self):
        return """running average"""


########################################################################################################################
#   CLASS
########################################################################################################################
class QueueNetwork:
    """Class for operating a queue network in discrete time."""

    ##
    # Initialize a queue network given a size, service rates and initial workloads.
    # If only a size was given, all queues will have service rate = 1, workload = 0.
    # All parameters are integers where size > 0, all service rates > 0 and workloads >= 0.
    ##
    def __init__(self, size, services=[], workloads=[], historyWindowSize=10000, userDefinedStats=None):
        _size = int(size)
        _services = services
        _workloads = workloads
        _userDefinedStats = userDefinedStats
        if _size < 1:
            raise Exception("Illegal size for QueueNetwork")
        for i in range(len(_services)):
            _services[i] = int(_services[i])
            if _services[i] < 1:
                raise Exception("Illegal service rates for QueueNetwork")
        for i in range(len(_workloads)):
            _workloads[i] = int(_workloads[i])
            if _workloads[i] < 0:
                raise Exception("Illegal workloads for QueueNetwork")
        if not _services:
            _services = [1 for i in range(_size)]
        if not _workloads:
            _workloads = [0 for i in range(_size)]
        if not _userDefinedStats:
            _userDefinedStats = RunningAverageStats()

        # Member fields init.
        self.queues = [Queue(_services[i], _workloads[i]) for i in range(_size)]
        self.size = _size
        self.time = 0
        self.stats = StatsCollector(windowSize=historyWindowSize, userDefinedStatsClass=_userDefinedStats)

    ##
    # Resets all queues to services and workload of 0.
    ##
    def reset(self, services=[]):
        _services = services
        if len(_services) == 0:
            _services = [1 for i in range(self.getSize())]
        if len(_services) != self.getSize():
            raise Exception("Services vector size mismatch with queue network size while trying to reset")
        [self.queues[i].reset(_services[i]) for i in range(self.getSize())]
        self.getStats().reset()
        self.time = 0

    ##
    # Resets all queues to workload of 0.
    ##
    def flush(self, windowSize=0):
        [q.reset(q.getService()) for q in self.queues]
        self.getStats().reset(windowSize=windowSize)
        self.time = 0

    ##
    # Get the time passed in the network.
    ##
    def getTime(self):
        return self.time

    ##
    # Set the time passed in the network.
    ##
    def setTime(self, time):
        if int(time) < 0:
            raise Exception("Trying to set the network time to a negative value")
        self.time = int(time)

    ##
    # Returns a list of the current services.
    ##
    def getServices(self):
        services = [q.getService() for q in self.queues]
        return services

    ##
    # Returns a list of the current workloads.
    ##
    def getWorkloads(self):
        workloads = [q.getWorkload() for q in self.queues]
        return workloads

    ##
    # Returns the total workload in the network.
    ##
    def getTotalWorkload(self):
        return np.sum(self.getWorkloads())

    ##
    # Returns the number of queues in the network.
    ##
    def getSize(self):
        return self.size

    ##
    # Returns the StatsCollector class for this network.
    ##
    def getStats(self):
        return self.stats

    ##
    # Sets the services to the given sizes. services are integers and are > 0.
    ##
    def setServices(self, services=[]):
        if not services or len(services) != self.size:
            raise Exception("Illegal number of service rates for setServices")
        for i in range(self.size):
            if int(services[i]) < 1:
                raise Exception("Illegal service rates for setServices")
        [self.queues[i].setService(int(services[i])) for i in range(self.size)]

    ##
    # Sets the workloads to the given sizes. Workloads are integers and are >= 0.
    ##
    def setWorkloads(self, workloads=[]):
        if not workloads or len(workloads) != self.size:
            raise Exception("Illegal number of workloads for setWorkloads")
        for i in range(self.size):
            if int(workloads[i]) < 0:
                raise Exception("Illegal workloads for setWorkloads")
        [self.queues[i].setWorkload(int(workloads[i])) for i in range(self.size)]

    ##
    # Adds the given workloads to the specified queues.
    # If no index is given, workloads size must be self.getSize() and will be added to all queues accordingly.
    # Notice: this method can be used to decrease the workload if passing a negative value.
    ##
    def addWorkload(self, workloads, index=[]):
        _index = []
        if len(index) == 0:
            _index = range(self.getSize())
        else:
            for i in range(len(index)):
                if int(index[i]) < 0 or int(index[i]) > self.size - 1:
                    raise Exception("Illegal index for addWorkload")
                _index.append(int(index[i]))
        _workloads = [int(workload) for workload in workloads]
        if len(_workloads) != len(_index):
            raise Exception("Length of workloads doesn't match length of indices in addWorkload")
        [self.queues[_index[i]].addWorkload(_workloads[i]) for i in range(len(_index))]

    ##
    # Reduces the amount of workload in every queue by its service rate and increments the time that passed.
    ##
    def endTimeSlot(self):
        # Time slot is over - collect stats for this slot.
        [q.endTimeSlot() for q in self.queues]
        stats = self.getStats()
        stats.insert(self.getTotalWorkload())
        if stats.getUserDefinedStats().name() == "running average":
            # Default behaviour.
            stats.getUserDefinedStats().insert([stats.getWindow(), self.getTime()])
        else:
            stats.getUserDefinedStats().insert(self)

    def advanceTimeSlot(self):
        # Advance.
        [q.advanceTimeSlot() for q in self.queues]
        self.time += 1
