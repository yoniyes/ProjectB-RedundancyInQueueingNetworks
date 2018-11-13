import abc  # Python's built-in abstract class library
import numpy as np
import math


########################################################################################################################
#   INTERFACE
########################################################################################################################
class ConvergenceConditionStrategyAbstract:
    """An abstract class from which all convergence conditions need to inherit."""

    # This is how you define abstract classes in Python.
    __metaclass__ = abc.ABCMeta

    ##
    # Initialize a convergence condition instance.
    # @epsilon is the precision of the convergence check.
    ##
    def __init__(self, epsilon=0.05):
        self.epsilon = float(epsilon)

    ##
    # Checks if a queue network has converged.
    ##
    @abc.abstractmethod
    def hasConverged(self, network, stats, startFrom, deadline):
        """Required Method"""


########################################################################################################################
#   IMPLEMENTATIONS
########################################################################################################################
class STDVConvergenceStrategy(ConvergenceConditionStrategyAbstract):
    """Checks if (standard deviation / average) is small enough."""

    ##
    # Gets stats, edge times and epsilon and returns a boolean.
    # @stats is a list.
    ##
    def hasConverged(self, network, stats, startFrom, deadline):
        avg = np.mean(stats)
        stdv = np.std(stats)
        return (network.getTime() >= startFrom and float(avg) > 0.00001 and
                (float(stdv) / float(avg)) < float(self.epsilon)) or network.getTime() > deadline


class DeltaConvergenceStrategy(ConvergenceConditionStrategyAbstract):
    """Checks if (window delta / average) is small enough."""

    ##
    # Gets stats, edge times and epsilon and returns a boolean.
    # @stats is a list of 2 lists. The first element is the current window and the second is the previous.
    ##
    def hasConverged(self, network, stats, startFrom, deadline):
        currWindow = stats[0]
        prevWindow = stats[1]
        avgPrev = np.mean(prevWindow)
        avgCurr = np.mean(currWindow)
        return network.getTime() > deadline or (network.getTime() >= startFrom and float(avgPrev) > 0.00001 and
                                                math.fabs((float(avgCurr) - float(avgPrev)) / float(avgPrev)) <
                                                float(self.epsilon))
