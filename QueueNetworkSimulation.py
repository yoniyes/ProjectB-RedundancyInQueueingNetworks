import datetime
import numpy as np
from QueueNetwork import QueueNetwork
from StatsCollector import StatsCollector

# TODO: 1 server, miu = 0.5, sweep lambda up to lambda = 0.99*miu and for every lambda plot running average.
#       Plot for all sims the converged average workload.
# TODO: New convergence condition.
# TODO: Check resolution of python's random capability using big numbers rule.
class QueueNetworkSimulation:
    """Class for simulating a queue network in discrete time with a given dispatch policy."""

    ##
    # Initialize a queue network simulation given a size, services and initial workloads along with a dispatch policy
    # and a converge condition.
    # If only a size and policy were given, all queues will have service = 1, workload = 0.
    ##
    def __init__(self, size, dispatchPolicyStrategy, convergenceConditionStrategy, plotStrategy=None, services=[],
                 workloads=[], userStatsClass=None, inNetworkStatsClass=None, historyWindowSize=10000,
                 verbose=False, T_max=10000000, convergencePrecision=0.05):
        # Member fields init.
        self.network = QueueNetwork(size, services=services, workloads=workloads, historyWindowSize=historyWindowSize,
                                    userDefinedStats=inNetworkStatsClass)
        self.dispatchPolicyStrategy = dispatchPolicyStrategy
        self.convergenceConditionStrategy = convergenceConditionStrategy
        self.plotStrategy = plotStrategy
        self.statsCollector = StatsCollector(windowSize=historyWindowSize,userDefinedStatsClass=userStatsClass)
        self.verbose = verbose
        self.T_max = T_max
        self.T_min = historyWindowSize
        self.epsilon = convergencePrecision

    ##
    # Resets the simulation.
    ##
    def reset(self, historyWindowSize=0):
        self.network.flush(windowSize=historyWindowSize)
        self.statsCollector.reset(windowSize=historyWindowSize)
        if self.verbose:
            print "INFO:    Simulation reset."

    ##
    # Set the dispatch policy.
    ##
    def setDispatchPolicy(self, dispatchPolicyStrategy):
        self.dispatchPolicyStrategy = dispatchPolicyStrategy
        if self.verbose:
            print "INFO:    Simulation dispatch policy set."

    ##
    # Set the convergence check function.
    ##
    def setConvergenceCondition(self, convergenceConditionStrategy):
        self.convergenceConditionStrategy = convergenceConditionStrategy
        if self.verbose:
            print "INFO:    Simulation convergence condition set."

    ##
    # Set the plotting function.
    ##
    def setPlot(self, plotStrategy):
        self.plotStrategy = plotStrategy
        if self.verbose:
            print "INFO:    Simulation plotting scheme set."

    ##
    # Run the simulation.
    ##
    # FIXME: not generic at the moment...
    def run(self, lambdaGranularity=1000):
        start_time = datetime.datetime.now()
        if self.verbose:
            print "INFO:    Starting simulation:"
            print "INFO:        time                            :   " + str(start_time)
            print "INFO:        number of servers               :   " + str(self.network.getSize())
            print "INFO:        starting in time slot           :   " + str(self.network.getTime())
            print "INFO:        policy                          :   " + self.dispatchPolicyStrategy.getName()
            print "INFO:        servers service per time slot   :   " + str(self.network.getServices())
            print "INFO:        servers initial workload        :   " + str(self.network.getWorkloads())

        effectiveServiceRate = self.dispatchPolicyStrategy.getEffectiveServiceRate(self.network)
        if effectiveServiceRate == 0:
            arrivalRates = np.arange(0, 1, 1.0 / lambdaGranularity)
        else:
            arrivalRates = np.arange(0, effectiveServiceRate, 1.0 / lambdaGranularity)
        for arrivalRate in arrivalRates:
            if self.verbose:
                print "INFO:    arrival rate  =   " + str(arrivalRate) + "  [ " + str(100.0 * arrivalRate /
                                                                                      effectiveServiceRate) + "% ]"
                print "INFO:    Round Started at  :   " + str(datetime.datetime.now())
            while self.network.getTime() < self.T_max:
                newArrival = np.random.choice([True, False], p=[arrivalRate, 1.0 - arrivalRate])
                if newArrival:
                    queues, newWork = self.dispatchPolicyStrategy.getDispatch(self.network)
                    self.network.addWorkload(newWork, queues)
                self.network.endTimeSlot()
                if arrivalRate == 0 or self.network.getTime() % self.T_min == 0 and \
                        self.convergenceConditionStrategy.hasConverged(self.network, self.T_min, self.T_max,
                                                                       self.epsilon):
                    self.statsCollector.insert(self.network.getStats().getAverage())
                    break
                self.network.advanceTimeSlot()
            if self.verbose:
                print "INFO:    Round ended at  :   " + str(datetime.datetime.now())
                print "INFO:    Time slot       :   " + str(self.network.getTime())
            self.network.reset()

        end_time = datetime.datetime.now()
        if self.verbose:
            print "INFO:    Simulation ended at:"
            print "INFO:        time                            :   " + str(end_time)

    ##
    # Load a network image to the simulation.
    ##
    def load(self, filename):
        if self.verbose:
            print "INFO:    Loading network from file [ " + filename + " ]"

    ##
    # Save simulation to a file.
    ##
    def save(self, filename="queue_net_sim.dump"):
        if self.verbose:
            print "INFO:    Saving simulation to file [ " + filename + " ]"

    ##
    # Plot results based on given plotting scheme.
    ##
    def plot(self, plotStrategy=None):
        if self.verbose:
            print "INFO:    Plotting..."
        if self.plotStrategy is not None:
            self.plotStrategy.plot(self.statsCollector)
        if plotStrategy is not None:
            plotStrategy.plot(self.statsCollector)


########################################################################################################################
#   MAIN
########################################################################################################################
import DispatchPolicyStrategy
import ConvergenceConditionStrategy
sim = QueueNetworkSimulation(1, DispatchPolicyStrategy.OneQueueFixedServiceRateStrategy(10, 0.25, 0.75),
                             ConvergenceConditionStrategy.STDVConvergenceStrategy(), verbose=True)
sim.run(lambdaGranularity=5)
