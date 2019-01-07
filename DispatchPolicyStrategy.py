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

    ##
    # Get name of policy.
    ##
    @abc.abstractmethod
    def getOneQueueMu(self):
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
        muEffective = 1.0 / (float(self.alpha) * (1.0 - (1.0 - float(self.p))**self.redundancy) +
                             float(self.beta) * (1.0 - self.p)**self.redundancy)
        return muEffective * (float(network.getSize()) / float(self.redundancy))

    def getOneQueueMu(self):
        return 1.0 / (self.alpha*self.p + self.beta*(1.0 - self.p))


class RandomQueueStrategy(DispatchPolicyStrategyAbstract):
    """A random dispatching policy. A random queue will get the job."""

    def __init__(self, alpha, beta, p):
        self.alpha = alpha
        self.beta = beta
        self.p = p
        self.mu = 1.0 / (float(alpha) * float(p) + float(beta) * (1.0 - p))

    ##
    # Randomly choose a queue and determine the workload it will get.
    ##
    def getDispatch(self, network):
        return [np.random.choice(range(network.getSize()))], [np.random.choice([self.alpha, self.beta],
                                                                             p=[self.p, 1.0 - self.p])]

    def getName(self):
        return "random queue"

    def getEffectiveServiceRate(self, network):
        return self.mu * network.getSize()

    def getOneQueueMu(self):
        return self.mu


class OneQueueFixedServiceRateStrategy(DispatchPolicyStrategyAbstract):
    """A fixed service rate dispatching policy."""

    ##
    # Initialize policy with @alpha being small workload for a job, @mu being the total service rate and @p being the
    # probability to choose alpha.
    ##
    def __init__(self, alpha, mu, p):
        if 1.0 / mu <= float(alpha):
            raise Exception("Error: must be [ (1.0 / mu) > alpha ] in order to dispatch correctly.")
        self.alpha = alpha
        self.beta = ((1.0/mu) - float(alpha)*p) / (1.0 - p)
        self.p = p
        self.mu = mu

    ##
    # Randomize arriving job's workload.
    ##
    def getDispatch(self, network):
        workload = self.alpha
        if np.random.binomial(1, self.p) == 0:
            workload = self.beta
        return [0], [workload]
        # return [0], [np.random.choice([self.alpha, self.beta], p=[self.p, 1.0 - self.p])]

    def getName(self):
        return "one queue fixed service rate"

    def getEffectiveServiceRate(self, network):
        return self.mu

    def setP(self, p):
        if p < 0 or p > 1:
            raise Exception("Invalid probability given")
        self.p = p
        self.beta = ((1.0/self.mu) - float(self.alpha)*p) / (1.0 - p)

    def setBeta(self, beta):
        if beta <= self.alpha:
            raise Exception("Invalid beta, should be greater than alpha")
        self.p = (beta - (1.0/self.mu)) / (beta - self.alpha)
        self.beta = beta

    def getOneQueueMu(self):
        return self.mu


class OnlyFirstQueueGetsJobsStrategy(DispatchPolicyStrategyAbstract):

    ##
    # Initialize policy with @alpha being small workload for a job, @mu being the total service rate and @p being the
    # probability to choose alpha.
    ##
    def __init__(self, alpha, beta, p, n):
        self.alpha = alpha
        self.beta = beta
        self.p = p
        self.mu = 1.0 / (float(alpha)*float(p) + float(beta)*(1.0 - p))
        self.n = n

    ##
    # Randomize arriving job's workload.
    ##
    def getDispatch(self, network):
        workload = self.alpha
        if np.random.binomial(1, self.p) == 0:
            workload = self.beta
        return [0], [workload]
        # return [0], [np.random.choice([self.alpha, self.beta], p=[self.p, 1.0 - self.p])]

    def getName(self):
        return "only first queue gets jobs"

    def getEffectiveServiceRate(self, network):
        return self.mu * self.n

    def getOneQueueMu(self):
        return self.mu


class JoinShortestWorkloadStrategy(DispatchPolicyStrategyAbstract):
    """A dispatching policy that gives the job to the queue with the shortest workload."""

    ##
    # Initialize policy with @alpha being small workload for a job, @beta being unusual workload for a job and @p being
    # the probability to choose @alpha.
    ##
    def __init__(self, alpha, beta, p):
        self.alpha = alpha
        self.mu = 1.0 / (float(alpha)*p + float(beta)*(1.0 - p))
        if 1.0 / self.mu <= float(alpha):
            raise Exception("Error: must be [ (1.0 / mu) > alpha ] in order to dispatch correctly.")
        self.beta = beta
        self.p = p

    ##
    # Randomize arriving job's workload.
    ##
    def getDispatch(self, network):
        workload = self.alpha
        if np.random.binomial(1, self.p) == 0:
            workload = self.beta
        return [np.argmin(network.getWorkloads())], [workload]

    def getName(self):
        return "join shortest workload"

    def getEffectiveServiceRate(self, network):
        return self.mu * network.getSize()

    def getOneQueueMu(self):
        return self.mu


class RouteToAllStrategy(DispatchPolicyStrategyAbstract):
    """A dispatching policy that gives the job to all the queues."""

    ##
    # Initialize policy with @alpha being small workload for a job, @beta being unusual workload for a job and @p being
    # the probability to choose @alpha.
    ##
    def __init__(self, alpha, beta, p):
        self.alpha = alpha
        self.mu = 1.0 / (float(alpha)*p + float(beta)*(1.0 - p))
        if 1.0 / self.mu <= float(alpha):
            raise Exception("Error: must be [ (1.0 / mu) > alpha ] in order to dispatch correctly.")
        self.beta = beta
        self.p = p

    ##
    # Randomize arriving job's workload.
    ##
    def getDispatch(self, network):
        workload = np.min(np.random.choice([self.alpha, self.beta], network.getSize(), p=[self.p, 1.0 - self.p]))
        return range(network.getSize()), [workload for i in range(network.getSize())]

    def getName(self):
        return "route to all"

    def getEffectiveServiceRate(self, network):
        return 1.0 / (float(self.beta)*(1.0-self.p)**network.getSize() +
                      float(self.alpha)*(1.0-(1.0-self.p)**network.getSize()))

    def getOneQueueMu(self):
        return self.mu


class VolunteerOrTeamworkStrategy(DispatchPolicyStrategyAbstract):
    """A dispatching policy that gives the job to all queues with probability @q or to 1 random queue with probability
    1-@q."""

    ##
    # Initialize policy with @alpha being small workload for a job, @beta being unusual workload for a job and @p being
    # the probability to choose @alpha. @q is the probability to route to all.
    ##
    def __init__(self, alpha, beta, p, q):
        self.routeToAll = RouteToAllStrategy(alpha, beta, p)
        self.q = q

    ##
    # Randomize arriving job's workload.
    ##
    def getDispatch(self, network):
        # FIXME: wrong assumption in route-to-all. Not all queues have the same workload!
        if np.random.binomial(1, self.q) == 0:
            return self.routeToAll.getDispatch(network)
        return [np.random.choice(range(network.getSize()))], \
               [np.random.choice([self.routeToAll.alpha, self.routeToAll.beta],
                                 p=[self.routeToAll.p, 1.0 - self.routeToAll.p])]

    def getName(self):
        return "volunteer or teamwork"

    ##
    # Capacity region unknown so why not give it extra 20% :)?
    ##
    def getEffectiveServiceRate(self, network):
        return 1.2 * self.routeToAll.mu * network.getSize()

    def getOneQueueMu(self):
        return self.routeToAll.getOneQueueMu()


class RandomDStrategy(DispatchPolicyStrategyAbstract):
    """A dispatching policy that chooses d queues at random and dispatches the job to them."""

    ##
    # Initialize policy with @alpha being small workload for a job, @beta being unusual workload for a job and @p being
    # the probability to choose @alpha. @d is the redundancy level.
    ##
    def __init__(self, alpha, beta, p, d):
        self.alpha = int(alpha)
        self.mu = 1.0 / (float(alpha) * p + float(beta) * (1.0 - p))
        if 1.0 / self.mu <= float(alpha):
            raise Exception("Error: must be [ (1.0 / mu) > alpha ] in order to dispatch correctly.")
        self.beta = int(beta)
        self.p = float(p)
        self.d = int(d)

    ##
    # Randomize arriving job's workload.
    ##
    def getDispatch(self, network):
        # get network state.
        currWlds = network.getWorkloads()
        n = network.getSize()
        # choose queues to receive the job.
        chosenQueues = np.random.choice(range(n), self.d, replace=False, p=[1.0/n]*n)
        # randomize incoming workload for each queue.
        incomingWlds = np.random.choice([self.alpha, self.beta], self.d, p=[self.p, 1.0 - self.p])
        speculation = [currWlds[chosenQueues[i]] + incomingWlds[i] for i in range(self.d)]
        min_i = int(np.argmin(speculation))
        added = [np.max([speculation[min_i] - currWlds[chosenQueues[i]], 0]) for i in range(self.d)]
        return chosenQueues, added

    def getName(self):
        return "random-d out of n"

    ##
    # Capacity region unknown. Returns cap. region of d=1.
    ##
    def getEffectiveServiceRate(self, network):
        return self.mu * network.getSize()

    def getOneQueueMu(self):
        return self.mu


class GeometricDeltaRandomDStrategy(DispatchPolicyStrategyAbstract):
    """A dispatching policy that chooses d queues at random and dispatches the job to them. Job size is determined as
    a + geometric(p)"""

    ##
    # Initialize policy with @alpha being constant workload for a job, @p being a geometric distribution parameter from
    # which a job's random workload part will be drawn, @n being the number of servers in the system. @d is the
    # redundancy level.
    ##
    def __init__(self, alpha, p, d, n):
        if p >= 1.0 / 2.0*int(n):
            raise Exception("Error: must be [ (1.0 / 2*n) > p ] in order to dispatch correctly.")
        self.p = float(p)
        self.n = int(n)
        self.alpha = int(alpha)
        self.delta = np.random.RandomState()
        self.mu = 1.0 / (int(alpha) + (1.0 / float(p)))
        if 1.0 / self.mu <= float(alpha):
            raise Exception("Error: must be [ (1.0 / mu) > alpha ] in order to dispatch correctly.")
        self.d = int(d)

    ##
    # Randomize arriving job's workload.
    ##
    def getDispatch(self, network):
        # get network state.
        currWlds = network.getWorkloads()
        n = network.getSize()
        # choose queues to receive the job.
        chosenQueues = np.random.choice(range(n), self.d, replace=False, p=[1.0/n]*n)
        # randomize incoming workload for each queue.
        incomingWlds = self.alpha + self.delta.geometric(p=self.p, size=self.d)
        speculation = [currWlds[chosenQueues[i]] + incomingWlds[i] for i in range(self.d)]
        min_i = int(np.argmin(speculation))
        added = [np.max([speculation[min_i] - currWlds[chosenQueues[i]], 0]) for i in range(self.d)]
        return chosenQueues, added

    def getName(self):
        return "geometric delta random-d"

    ##
    # Capacity region unknown. Returns cap. region of d=1.
    ##
    def getEffectiveServiceRate(self, network):
        return self.mu * network.getSize()

    def getOneQueueMu(self):
        return self.mu
