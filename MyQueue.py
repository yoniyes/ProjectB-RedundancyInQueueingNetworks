import unittest as ut

class Queue:
    """This class describes a queue in a network running in discrete time with the ability to add and
    remove workload."""

    ##
    # Given a service and an initial workload, initializes a Queue.
    # Both parameters are integers where service > 0 and workload >= 0.
    ##
    def __init__(self, service=1, workload=0):
        if int(service) <= 0 or int(workload) < 0:
            raise Exception("Illegal arguments for Queue __init__")
        self.service = int(service)
        self.workload = int(workload)
        self.timePassed = 0

    ##
    # Resets the queue to service and workload of 0.
    ##
    def reset(self, service=1):
        self.setService(service)
        self.workload = 0
        self.timePassed = 0

    ##
    # Returns the current workload.
    ##
    def getWorkload(self):
        return self.workload

    ##
    # Sets the workload to the given size. workload is an integer and workload >= 0.
    ##
    def setWorkload(self, workload):
        if int(workload) < 0:
            raise Exception("Illegal arguments for Queue setWorkload")
        self.workload = int(workload)

    ##
    # Adds the given workload to the queue. Makes sure the total workload is >= 0.
    # Notice: this method can be used to decrease the workload if passing a negative value.
    ##
    def addWorkload(self, workload):
        notEmpty = 1
        if self.workload == 0:
            notEmpty = 0
        if self.workload + int(workload) < 0:
            self.workload = 0
        else:
            self.workload += int(workload)
        return notEmpty

    ##
    # Returns the current service.
    ##
    def getService(self):
        return self.service

    ##
    # Sets the service to the given size. service is an integer and it is > 0.
    ##
    def setService(self, service):
        if int(service) <= 0:
            raise Exception("Illegal arguments for Queue setService")
        self.service = int(service)

    ##
    # Reduces the amount of workload in Queue by service.
    ##
    def endTimeSlot(self):
        return self.addWorkload(-self.getService())
        # return self.addWorkload(-1)

    ##
    # Increments the time that passed.
    ##
    def advanceTimeSlot(self):
        self.timePassed += 1


########################################################################################################################
#   TEST
########################################################################################################################
class TestQueue(ut.TestCase):
    def runTest(self):
        with self.assertRaises(Exception):
            Queue(service=0)
        with self.assertRaises(Exception):
            Queue(service=-1)
        with self.assertRaises(Exception):
            Queue(workload=-1)
        q = Queue()
        self.assertEqual(q.getWorkload(), 0)
        self.assertEqual(q.getService(), 1)
        q.setWorkload(100)
        self.assertEqual(q.getWorkload(), 100)
        q.setService(2)
        self.assertEqual(q.getService(), 2)
        with self.assertRaises(Exception):
            q.setWorkload(-1)
        with self.assertRaises(Exception):
            q.setService(0)
        q.addWorkload(100)
        self.assertEqual(q.getWorkload(), 200)
        q.endTimeSlot()
        self.assertEqual(q.getWorkload(), 198)
        q.addWorkload(-7)
        self.assertEqual(q.getWorkload(), 191)
        q.addWorkload(-192)
        self.assertEqual(q.getWorkload(), 0)
        q.endTimeSlot()
        self.assertEqual(q.getWorkload(), 0)
        q.addWorkload(10)
        self.assertEqual(q.getWorkload(), 10)
        q.reset()
        self.assertEqual(q.getService(), 1)
        self.assertEqual(q.getWorkload(), 0)
        print "TestQueue: OK."


if __name__ == '__main__':
    ut.main()
