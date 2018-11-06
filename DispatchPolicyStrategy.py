import abc  # Python's built-in abstract class library
import numpy as np
import math


########################################################################################################################
#   INTERFACE
########################################################################################################################
class DispatchPolicyStrategyAbstract:
    """An abstract class from which all dispatching policies need to inherit."""

    # This is how you define abstract classes in Python.
    __metaclass__ = abc.ABCMeta

    ##
    # Upon an arrival gets a queue network instance and outputs which queues receive it and what's the workload each
    # one of them adds to itself.
    ##
    @abc.abstractmethod
    def getDispatch(self, network):
        """Required Method"""

    ##
    # Get effective service rate of policy.
    ##
    @abc.abstractmethod
    def getEffectiveServiceRate(self, network):
        """Required Method"""

    ##
    # Get name of policy.
    ##
    @abc.abstractmethod
    def getName(self):
        """Required Method"""


########################################################################################################################
#   IMPLEMENTATIONS
########################################################################################################################
class FixedSubsetsStrategy(DispatchPolicyStrategyAbstract):
    """A fixed subsets dispatching policy."""

    def __init__(self, redundancy, alpha, beta, p):
        self.redundancy = redundancy
        self.alpha = alpha
        self.beta = beta
        self.p = p

    ##
    # Randomly choose one of the fixed subsets and determine the workload each one of the queues in it will get.
    # Assumption: network.size % redundancy == 0
    ##
    def getDispatch(self, network):
        n = network.getSize()
        # Choose the subset.
        numOfSubsets = int(math.ceil(n / float(self.redundancy)))
        chosenSubset = np.random.randint(numOfSubsets)
        queuesChosen = filter(lambda x: x < n,
                              range(chosenSubset * self.redundancy, (chosenSubset + 1) * self.redundancy))
        # Randomize the incoming job's workload for each queue chosen.
        randWorkload = np.random.choice([self.alpha, self.beta], self.redundancy, p=[self.p, 1.0 - self.p])
        # Determine the total increment of workload in every queue chosen.
        currWorkload = [network.getWorkloads()[q] for q in queuesChosen]
        min_i = 0
        for i in range(len(currWorkload)):
            if currWorkload[i] + randWorkload[i] < currWorkload[min_i] + randWorkload[min_i]:
                min_i = i
        maxTotalWorkloadInQueue = currWorkload[min_i] + randWorkload[min_i]
        addedWorkload = [np.max(maxTotalWorkloadInQueue - currWorkload[i], 0) for i in range(len(currWorkload))]
        return queuesChosen, addedWorkload

    def getName(self):
        return "fixed subsets"

    def getEffectiveServiceRate(self, network):
        """need to implement"""


class OneQueueFixedServiceRateStrategy(DispatchPolicyStrategyAbstract):
    """A fixed service rate dispatching policy."""

    ##
    # Initialize policy with @alpha being small workload for a job, @miu being the total service rate and @p being the
    # probability to choose alpha.
    ##
    def __init__(self, alpha, miu, p):
        self.alpha = alpha
        self.beta = ((1.0/miu) - float(alpha)*p) / (1.0 - p)
        self.p = p
        self.miu = miu

    ##
    # Randomize arriving job's workload.
    ##
    def getDispatch(self, network):
        return [0], [np.random.choice([self.alpha, self.beta], p=[self.p, 1.0 - self.p])]

    def getName(self):
        return "one queue fixed service rate"

    def getEffectiveServiceRate(self, network):
        return self.miu

    def setP(self, p):
        if p < 0 or p > 1:
            raise Exception("Invalid probability given")
        self.p = p
        self.beta = ((1.0/self.miu) - float(self.alpha)*p) / (1.0 - p)

    def setBeta(self, beta):
        if beta <= self.alpha:
            raise Exception("Invalid beta, should be greater than alpha")
        self.p = (beta - (1.0/self.miu)) / (beta - self.alpha)
        self.beta = beta
