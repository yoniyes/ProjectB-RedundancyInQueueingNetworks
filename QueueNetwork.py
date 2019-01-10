from MyQueue import Queue
import numpy as np
import unittest as ut


class QueueNetwork:
    """Class for operating a queue network in discrete time."""

    ##
    # Initialize a queue network given a size, service rates and initial workloads.
    # If only a size was given, all queues will have service rate = 1, workload = 0.
    # All parameters are integers where size > 0, all service rates > 0 and workloads >= 0.
    ##
    def __init__(self, size, services=[], workloads=[]):
        _size = int(size)
        _services = services
        _workloads = workloads
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

        # Member fields init.
        self.queues = [Queue(_services[i], _workloads[i]) for i in range(_size)]
        self.totalWorkload = np.sum(_workloads)
        self.size = _size
        self.time = 0

    ##
    # Resets all queues to @services and workload of 0.
    ##
    def reset(self, services=[]):
        _services = services
        if len(_services) == 0:
            _services = [1]*self.getSize()
        if len(_services) != self.getSize():
            raise Exception("Services vector size mismatch with queue network size while trying to reset")
        for i in range(self.getSize()):
            self.queues[i].reset(_services[i])
        self.time = 0
        self.totalWorkload = 0
        # assert self.totalWorkload == np.sum(self.getWorkloads()), "lhs = " + str(self.totalWorkload) + " rhs = " + str(np.sum(self.getWorkloads()))

    ##
    # Resets all queues to workload of 0.
    ##
    def flush(self):
        for q in self.queues:
            q.reset(q.getService())
        self.time = 0
        self.totalWorkload = 0
        # assert self.totalWorkload == np.sum(self.getWorkloads()), "lhs = " + str(self.totalWorkload) + " rhs = " + str(np.sum(self.getWorkloads()))

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
        # assert self.totalWorkload == np.sum(self.getWorkloads()), "lhs = " + str(self.totalWorkload) + " rhs = " + str(np.sum(self.getWorkloads()))
        return self.totalWorkload

    ##
    # Returns the number of queues in the network.
    ##
    def getSize(self):
        return self.size

    ##
    # Sets the services to the given sizes. services are integers and are > 0.
    ##
    def setServices(self, services=[]):
        if not services or len(services) != self.size:
            raise Exception("Illegal number of service rates for setServices")
        for i in range(self.size):
            if int(services[i]) < 1:
                raise Exception("Illegal service rates for setServices")
        for i in range(self.size):
            self.queues[i].setService(int(services[i]))

    ##
    # Sets the workloads to the given sizes. Workloads are integers and are >= 0.
    ##
    def setWorkloads(self, workloads=[]):
        if not workloads or len(workloads) != self.size:
            raise Exception("Illegal number of workloads for setWorkloads")
        for i in range(self.size):
            if int(workloads[i]) < 0:
                raise Exception("Illegal workloads for setWorkloads")
        self.totalWorkload = 0
        for i in range(self.size):
            self.queues[i].setWorkload(int(workloads[i]))
            self.totalWorkload += int(workloads[i])
        # assert self.totalWorkload == np.sum(self.getWorkloads()), "lhs = " + str(self.totalWorkload) + " rhs = " + str(np.sum(self.getWorkloads()))


    ##
    # Adds the given workloads to the specified queues.
    # If no index is given, workloads size must be self.getSize() and will be added to all queues accordingly.
    # Notice: this method can be used to decrease the workload if passing a negative value.
    ##
    def addWorkload(self, chosen, workloads):
        if len(chosen) < 1 or len(chosen) != len(workloads):
            raise Exception("Illegal size of queues or workloads for addWorkload")
        _workloads = [int(workload) for workload in workloads]
        if np.sum(workloads) != np.sum(_workloads):
            raise Exception("OUCH!!!")
        for i in range(len(chosen)):
            self.queues[chosen[i]].addWorkload(_workloads[i])
            self.totalWorkload += _workloads[i]
        # assert self.totalWorkload == np.sum(self.getWorkloads()), "lhs = " + str(self.totalWorkload) + " rhs = " + str(np.sum(self.getWorkloads())) + " added = " + str(_workloads)

    ##
    # Reduces the amount of workload in every queue by its service.
    ##
    def endTimeSlot(self):
        for q in self.queues:
            self.totalWorkload -= q.endTimeSlot()
        # assert self.totalWorkload == np.sum(self.getWorkloads()), "lhs = " + str(self.totalWorkload) + " rhs = " + str(np.sum(self.getWorkloads()))

    ##
    # Increments the time that passed.
    ##
    def advanceTimeSlot(self):
        for q in self.queues:
            q.advanceTimeSlot()
        self.time += 1


########################################################################################################################
#   TEST
########################################################################################################################
class TestQueueNetwork(ut.TestCase):
    def runTest(self):
        with self.assertRaises(Exception):
            QueueNetwork(size=0)
        with self.assertRaises(Exception):
            QueueNetwork(size=-1)
        with self.assertRaises(Exception):
            QueueNetwork(size=2, services=[1, 0])
        with self.assertRaises(Exception):
            QueueNetwork(size=2, workloads=[1, -2])
        q = QueueNetwork(size=2)
        self.assertEqual(q.getSize(), 2)
        wlds = q.getWorkloads()
        self.assertEqual(wlds, [0] * len(wlds))
        self.assertEqual(q.getServices(), [1] * len(wlds))
        q.setWorkloads([100, 200])
        wlds = q.getWorkloads()
        self.assertEqual(wlds, [100, 200])
        q.setServices([1, 2])
        self.assertEqual(q.getServices(), [1, 2])
        with self.assertRaises(Exception):
            q.setWorkloads([10, -1])
        with self.assertRaises(Exception):
            q.setServices([0, 1])
        self.assertEqual(q.getTime(), 0)
        q.setTime(10)
        self.assertEqual(q.getTime(), 10)
        q. setTime(0)
        self.assertEqual(q.getTime(), 0)
        self.assertEqual(q.getTotalWorkload(), 300)
        q.addWorkload(index=range(len(wlds)), workloads=[-199] * len(wlds))
        self.assertEqual(q.getWorkloads(), [0, 1])
        self.assertEqual(q.getTotalWorkload(), 1)
        q.endTimeSlot()
        self.assertEqual(q.getWorkloads(), [0] * len(wlds))
        q.addWorkload([-7] * len(wlds))
        self.assertEqual(q.getWorkloads(), [0] * len(wlds))
        q.addWorkload([123] * len(wlds))
        self.assertEqual(q.getWorkloads(), [123] * len(wlds))
        q.endTimeSlot()
        self.assertEqual(q.getWorkloads(), [122, 121])
        q.addWorkload([10] * len(wlds))
        self.assertEqual(q.getWorkloads(), [132, 131])
        q.advanceTimeSlot()
        self.assertEqual(q.getTime(), 1)
        q.flush()
        self.assertEqual(q.getServices(), [1, 2])
        self.assertEqual(q.getWorkloads(), [0] * len(wlds))
        self.assertEqual(q.getTime(), 0)
        self.assertEqual(q.getTotalWorkload(), 0)
        q.reset()
        self.assertEqual(q.getServices(), [1] * len(wlds))
        self.assertEqual(q.getWorkloads(), [0] * len(wlds))
        self.assertEqual(q.getTime(), 0)
        self.assertEqual(q.getTotalWorkload(), 0)
        print "TestQueueNetwork: OK."


if __name__ == '__main__':
    ut.main()

