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
    # Checks if a queue network has converged.
    ##
    @abc.abstractmethod
    def hasConverged(self, args):
        """Required Method"""


########################################################################################################################
#   IMPLEMENTATIONS
########################################################################################################################
class STDVConvergenceStrategy(ConvergenceConditionStrategyAbstract):
    """Checks if (standard deviation / average) is small enough."""

    ##
    # Gets in @args the standard deviation, average and epsilon and returns a boolean.
    ##
    def hasConverged(self, args):
        if len(args) != 3:
            raise Exception("Missing arguments for convergence check")
        stdv = args[0]
        avg = args[1]
        epsilon = args[2]
        return float(avg) > 0.00001 and (float(stdv) / float(avg)) < float(epsilon)