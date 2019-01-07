from QueueNetwork import QueueNetwork
from StatsCollector import *
import matplotlib.pyplot as plt
import datetime
from timeit import default_timer as timer
import math

import cProfile


def guessAvgWorkload(arrivalRate, oneQmu, systemMuEffective):
    if arrivalRate >= systemMuEffective:
        return 0.0
    return arrivalRate * math.exp(arrivalRate) / (oneQmu*(systemMuEffective - arrivalRate))

########################################################################################################################
#   STATS CLASS
########################################################################################################################
class AdjacentWindowsAndAverageWorkloadStats:
    """User-defined stats class."""

    ##
    # Init MyStats with 2 statistics windows. The 2 windows are adjacent to each other. This is done in order to provide
    #  a way to compare 2 windows.
    ##
    def __init__(self, windowSize, numOfRounds):
        self.perLambdaStatsCollector = StatsCollector(windowSizes=[windowSize, windowSize])
        self.wholeSimStatsCollector = Stats(windowSize=numOfRounds)
        self.currentWindow = 0

    def insertToWindow(self, value):
        self.perLambdaStatsCollector.getStatNumber(self.currentWindow).insert(value)

    def insertToAvgWorkloadWindow(self, value):
        self.wholeSimStatsCollector.insert(value)

    def resetWindows(self):
        self.perLambdaStatsCollector.reset()
        self.currentWindow = 0

    def resetAll(self):
        self.resetWindows()
        self.wholeSimStatsCollector.reset()

    def getCurrentWindowStats(self):
        return self.perLambdaStatsCollector.getStatNumber(self.currentWindow)

    def getPreviousWindowStats(self):
        return self.perLambdaStatsCollector.getStatNumber(1 - self.currentWindow)

    def getAvgWorkloadWindowStats(self):
        return self.wholeSimStatsCollector

    def switchWindows(self):
        self.currentWindow = (self.currentWindow + 1) % 2
        self.perLambdaStatsCollector.getStatNumber(self.currentWindow).reset()


########################################################################################################################
#   STATS CLASS
########################################################################################################################
class RunningAverageWindowAndAverageWorkloadStats:
    """User-defined stats class."""

    ##
    # Init MyStats with a running average statistics window.
    ##
    def __init__(self, windowSize, numOfRounds):
        self.perLambdaStatsCollector = Stats(windowSize=windowSize)
        self.wholeSimStatsCollector = Stats(windowSize=numOfRounds)

    def insertToWindow(self, value):
        self.perLambdaStatsCollector.insert(value)

    def insertToAvgWorkloadWindow(self, value):
        self.wholeSimStatsCollector.insert(value)

    def resetWindows(self):
        self.perLambdaStatsCollector.reset()

    def resetAll(self):
        self.resetWindows()
        self.wholeSimStatsCollector.reset()

    def getWindowStats(self):
        return self.perLambdaStatsCollector

    def getAvgWorkloadWindowStats(self):
        return self.wholeSimStatsCollector

    def getLastWindowEntry(self):
        return self.perLambdaStatsCollector.window[self.perLambdaStatsCollector.nextOpenSlot - 1]


########################################################################################################################
#   SIMULATION BUILDING
########################################################################################################################
class QueueNetworkSimulation:
    """Class for simulating a queue network in discrete time with a given dispatch policy."""

    ##
    # Initialize a queue network simulation given a size, services and initial workloads along with a dispatch policy
    # and a converge condition.
    # If only a size and policy were given, all queues will have service = 1, workload = 0.
    # NOTICE: Edit this to set a different statistics class for init.
    ##
    def __init__(self, size, dispatchPolicyStrategy, convergenceConditionStrategy, plotStrategy=None, services=[],
                 workloads=[], historyWindowSize=10000, numOfRounds=1000,
                 verbose=False, T_min=0, T_max=10000000, guess=False):
        _T_min = T_min
        if T_min == 0:
            _T_min = historyWindowSize
        # Member fields init.
        self.network = QueueNetwork(size, services=services, workloads=workloads)
        self.dispatchPolicyStrategy = dispatchPolicyStrategy
        self.convergenceConditionStrategy = convergenceConditionStrategy
        self.plotStrategy = plotStrategy
        self.statsCollector = RunningAverageWindowAndAverageWorkloadStats(windowSize=historyWindowSize,
                                                                          numOfRounds=numOfRounds)
        self.verbose = verbose
        self.T_max = T_max
        self.T_min = _T_min
        self.numOfRounds = numOfRounds
        self.guessAvgWorkload = guess

    ##
    # Resets the simulation.
    ##
    def reset(self):
        self.network.flush()
        self.statsCollector.resetAll()
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

    # calculate the next average workload in the avg workload vector
    def calcAvgWorkLoad(self, T, AvgWorkLoad_prev, TotalWorkLoad):
        T = float(T)
        AvgWorkLoad_prev = float(AvgWorkLoad_prev)
        TotalWorkLoad = float(TotalWorkLoad)
        return (1.0 / T) * ((T - 1) * AvgWorkLoad_prev + TotalWorkLoad)

    ##
    # Run the simulation.
    # NOTICE: Edit this to make your simulation advance through time as you expect it to.
    ##
    def run(self):
        start_time = datetime.datetime.now()
        initialWorkloadStr = str(self.network.getWorkloads())
        if self.verbose:
            print "INFO:    Starting simulation:"
            print "INFO:        time                            :   " + str(start_time)
            print "INFO:        number of servers               :   " + str(self.network.getSize())
            print "INFO:        starting in time slot           :   " + str(self.network.getTime())
            print "INFO:        policy                          :   " + self.dispatchPolicyStrategy.getName()
            print "INFO:        servers service per time slot   :   " + str(self.network.getServices())
            print "INFO:        servers initial workload        :   " + str(self.network.getWorkloads()) + "\n"

        effectiveServiceRate = self.dispatchPolicyStrategy.getEffectiveServiceRate(self.network)
        arrivalRates = [0]*self.numOfRounds
        if effectiveServiceRate != 0:
            arrivalRates = np.arange(0, effectiveServiceRate, float(effectiveServiceRate) / float(self.numOfRounds))

        # Round operating loop.
        simTimeAnalysis = []
        for arrivalRate in arrivalRates:
            if self.verbose:
                print "INFO:    arrival rate  =   " + str(arrivalRate) + "  [ " + str(100.0 * arrivalRate /
                                                                                      effectiveServiceRate) + "% ]"
                print "INFO:    Round Started at  :   " + str(datetime.datetime.now())
            start = timer()
            # Try and guess avg workload for faster convergence.
            # TODO: test this feature and this guess function.
            if self.guessAvgWorkload:
                guess = int(guessAvgWorkload(arrivalRate, self.dispatchPolicyStrategy.getOneQueueMu(),
                                             effectiveServiceRate))
                initWorkloads = [int(guess / self.network.getSize()) for i in range(self.network.getSize())]
                self.network.setWorkloads(initWorkloads)
                if self.verbose:
                    print "INFO:    Guessed avg workload  =   " + str(guess)

            # runningAvg = [0]
            # Time-slot operating loop.
            while self.network.getTime() < self.T_max:
                t = self.network.getTime()
                # Determine whether a new job arrived or not.
                if np.random.binomial(1, arrivalRate) == 1:
                    queues, newWork = self.dispatchPolicyStrategy.getDispatch(self.network)
                    self.network.addWorkload(queues, newWork)
                # End the time-slot.
                self.network.endTimeSlot()
                # Check for convergence.
                if arrivalRate == 0:
                    self.statsCollector.insertToAvgWorkloadWindow(0.0)
                    self.statsCollector.resetWindows()
                    break
                # Is it time to check for convergence?
                elif t >= self.T_min and (t + 1) % self.statsCollector.getWindowStats().getWindowSize() == 0:
                    # If converged, record stats and end round.
                    if self.convergenceConditionStrategy.hasConverged(self.network,
                            [self.statsCollector.getWindowStats().getWindow()],
                            self.T_min, self.T_max):
                        self.statsCollector.insertToAvgWorkloadWindow(
                            self.calcAvgWorkLoad(
                                t+1,
                                self.statsCollector.getLastWindowEntry(),
                                self.network.getTotalWorkload()
                            )
                        )
                        self.statsCollector.resetWindows()
                        break
                    # # If didn't converge, switch the windows.
                    # self.statsCollector.switchWindows()

                # Gather stats of this time-slot.
                self.statsCollector.insertToWindow(
                    self.calcAvgWorkLoad(
                        t+1,
                        self.statsCollector.getLastWindowEntry(),
                        self.network.getTotalWorkload()
                    )
                )
                # runningAvg.append(self.calcAvgWorkLoad(t+1, runningAvg[t], self.network.getTotalWorkload()))
                # Advance simulation time.
                self.network.advanceTimeSlot()

            if self.verbose:
                print "INFO:    Round ended at  :   " + str(datetime.datetime.now())
                print "INFO:    Time slot       :   " + str(self.network.getTime() + 1) + "\n"
            end = timer()   # Time in seconds
            simTimeAnalysis.append(float(end) - float(start))
            # plt.plot(runningAvg)
            # plt.show()
            self.network.reset()

        end_time = datetime.datetime.now()
        if self.verbose:
            print "INFO:    Simulation ended at:"
            print "INFO:        time                            :   " + str(end_time)

        # Save results to file.
        if self.verbose:
            print "INFO:    Saving results to file [ " + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + "_queue_net_sim.dump ]"
        fd = open(datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + '_queue_net_sim.dump', 'w')
        for val in arrivalRates:
            fd.write(str(val) + ",")
        fd.write("\n")
        for val in self.statsCollector.getAvgWorkloadWindowStats().getWindow():
            fd.write(str(val) + ",")
        fd.write("\n")
        fd.write("\n")
        fd.write("INFO:        time started                    :   " + str(start_time) + "\n")
        fd.write("INFO:        time ended                      :   " + str(end_time) + "\n")
        fd.write("INFO:        number of servers               :   " + str(self.network.getSize()) + "\n")
        fd.write("INFO:        dispatch policy                 :   " + self.dispatchPolicyStrategy.getName() + "\n")
        fd.write("INFO:        convergence condition           :   " + self.convergenceConditionStrategy.getName() + "\n")
        fd.write("INFO:        convergence precision           :   " + str(self.convergenceConditionStrategy.getPrecision()) + "\n")
        fd.write("INFO:        servers service per time slot   :   " + str(self.network.getServices()) + "\n")
        fd.write("INFO:        servers initial workload        :   " + initialWorkloadStr + "\n")
        fd.close()

        # FIXME: Move the plotting to a plot strategy.
        if self.verbose and len(arrivalRates) != len(self.statsCollector.getAvgWorkloadWindowStats().getWindow()):
            print "WARN:    length of arrivalRates != length of stats collected"
        plt.plot(arrivalRates, self.statsCollector.getAvgWorkloadWindowStats().getWindow()[:len(arrivalRates)])
        plt.show()

        plt.plot(simTimeAnalysis, 'rx')
        plt.xlabel("arrival rate as % of service effective rate")
        plt.ylabel("simulation time [sec]")
        plt.show()

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
            print "INFO:    Saving simulation to file [ " + str(datetime.datetime.now()) + "_" + filename + " ]"

    ##
    # Plot results based on given plotting scheme.
    ##
    def plot(self, x, y, plotStrategy=None):
        if self.verbose:
            print "INFO:    Plotting..."
        if plotStrategy is not None:
            plotStrategy.plot(x, y)
        elif self.plotStrategy is not None:
            self.plotStrategy.plot(x, y)

    ##
    # Plot results from file based on given plotting scheme.
    ##
    def plotFromFile(self, resultsFile, plotStrategy=None):
        if self.verbose:
            print "INFO:    Getting data from [ " + resultsFile + " ]"
        with open(resultsFile, "r") as fd:
            x = [float(val) for val in fd.readline().split(',')[:-1]]
            y = [float(val) for val in fd.readline().split(',')[:-1]]
            if self.verbose:
                print "INFO:    Results metadata:"
                print "################################################################"
                print fd.read()
                print "################################################################"
        self.plot(x, y, plotStrategy=plotStrategy)


########################################################################################################################
#   MAIN
########################################################################################################################
import DispatchPolicyStrategy
import ConvergenceConditionStrategy

# Operate your simulation here.

# Init simulation instance.
# n=1
# dispatch policy = one queue, fixed service rate
#   alpha=10
#   mu=0.5
#   p=0.75
# convergence condition = window delta percent change.
#   precision = 0.05 (5%)
# sweep over 100 arrival rates.
# statistics history window size = 50000

# d=[1, 2, 4]
# sim = QueueNetworkSimulation(4, DispatchPolicyStrategy.FixedSubsetsStrategy(d[0], 10, 1000, 0.75),
#                              ConvergenceConditionStrategy.DeltaConvergenceStrategy(epsilon=0.05),
#                              verbose=True, numOfRounds=100, historyWindowSize=50000)
# for redundancy in d:
#     sim.setDispatchPolicy(DispatchPolicyStrategy.FixedSubsetsStrategy(redundancy, 10, 1000, 0.75))
#     sim.run()

# sim = QueueNetworkSimulation(1, DispatchPolicyStrategy.OneQueueFixedServiceRateStrategy(alpha=10, mu=0.05, p=0.75),
#                              ConvergenceConditionStrategy.VarianceConvergenceStrategy(epsilon=0.01),
#                              verbose=True, numOfRounds=100, historyWindowSize=10000, T_min=100000)
# cProfile.run('sim.run()')

# sim = QueueNetworkSimulation(2, DispatchPolicyStrategy.OnlyFirstQueueGetsJobsStrategy(n=2, alpha=10, beta=1000, p=0.75),
#                              ConvergenceConditionStrategy.VarianceConvergenceStrategy(epsilon=0.01),
#                              verbose=True, numOfRounds=10, historyWindowSize=10000, T_min=100000)
# cProfile.run('sim.run()')

# sim = QueueNetworkSimulation(2, DispatchPolicyStrategy.JoinShortestWorkloadStrategy(alpha=10, beta=1000, p=0.75),
#                              ConvergenceConditionStrategy.VarianceConvergenceStrategy(epsilon=0.01),
#                              verbose=True, numOfRounds=50, historyWindowSize=10000, T_min=100000)
# cProfile.run('sim.run()')

# FIXME: REMEMBER - HISTORY WINDOW SIZE IS PREFERRED TO BE 10*(1-p)*T_min. THE REASON IS WE WANT A WINDOW TO PROPERLY REFLECT AN AVERAGE SERIES OF EVENTS IN THE SYSTEM.
# sim = QueueNetworkSimulation(2, DispatchPolicyStrategy.RouteToAllStrategy(alpha=10, beta=1000, p=0.8),
#                              ConvergenceConditionStrategy.VarianceConvergenceStrategy(epsilon=0.05),
#                              verbose=True, numOfRounds=20, historyWindowSize=20000, T_min=100000, T_max=20000000)
# cProfile.run('sim.run()')

# sim = QueueNetworkSimulation(2, DispatchPolicyStrategy.JoinShortestWorkloadStrategy(alpha=10, beta=1000, p=0.75),
#                              ConvergenceConditionStrategy.RunForXSlotsConvergenceStrategy(1000000),
#                              verbose=True, numOfRounds=20, historyWindowSize=100000, T_min=100000)
# cProfile.run('sim.run()')

# sim = QueueNetworkSimulation(2, DispatchPolicyStrategy.VolunteerOrTeamworkStrategy(alpha=10, beta=1000, p=0.8, q=0.5),
#                              ConvergenceConditionStrategy.VarianceConvergenceStrategy(epsilon=0.05),
#                              verbose=True, numOfRounds=20, historyWindowSize=20000, T_min=100000, T_max=20000000)
# cProfile.run('sim.run()')

# sim = QueueNetworkSimulation(2, DispatchPolicyStrategy.RandomQueueStrategy(alpha=10, beta=1000, p=0.8),
#                              ConvergenceConditionStrategy.VarianceConvergenceStrategy(epsilon=0.05),
#                              verbose=True, numOfRounds=20, historyWindowSize=20000, T_min=1000000, T_max=20000000)
# cProfile.run('sim.run()')

# sim = QueueNetworkSimulation(4, DispatchPolicyStrategy.RouteToAllStrategy(alpha=1, beta=1000, p=0.9),
#                              ConvergenceConditionStrategy.VarianceConvergenceStrategy(epsilon=0.001),
#                              verbose=True, numOfRounds=10, historyWindowSize=10000, T_min=1000000, T_max=150000000)
# cProfile.run('sim.run()')

sim = QueueNetworkSimulation(3, DispatchPolicyStrategy.RandomDStrategy(alpha=1, beta=1000, p=0.9, d=2),
                             ConvergenceConditionStrategy.VarianceConvergenceStrategy(epsilon=0.001),
                             verbose=True, numOfRounds=100, historyWindowSize=20000, T_min=500000, T_max=150000000)
cProfile.run('sim.run()')
