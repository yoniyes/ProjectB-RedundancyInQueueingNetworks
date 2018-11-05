import datetime
from QueueNetwork import QueueNetwork

class QueueNetworkSimulation:
    """Class for simulating a queue network in discrete time with a given dispatch policy."""

    ##
    # Initialize a queue network simulation given a size, services and initial workloads along with a dispatch policy
    # and a converge condition.
    # If only a size and policy were given, all queues will have service = 1, workload = 0.
    ##
    def __init__(self, size, dispatchPolicyStrategy, convergenceConditionStrategy, plotStrategy=None, services=[],
                 workloads=[], verbose=False):
        # Member fields init.
        self.network = QueueNetwork(size, services=services, workloads=workloads)
        self.dispatchPolicyStrategy = dispatchPolicyStrategy
        self.convergenceConditionStrategy = convergenceConditionStrategy
        self.plotStrategy = plotStrategy
        self.verbose = verbose

    ##
    # Resets the simulation.
    ##
    def reset(self):
        self.network.flush()
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
    def run(self):
        if self.verbose:
            print "INFO:    Starting simulation:"
            print "INFO:        time                            :   " + str(datetime.datetime.now())
            print "INFO:        number of servers               :   " + str(self.network.getSize())
            print "INFO:        starting in time slot           :   " + str(self.network.getTime())
            print "INFO:        policy                          :   " + self.dispatchPolicyStrategy.getName()
            print "INFO:        servers service per time slot   :   " + str(self.network.getServices())
            print "INFO:        servers initial workload        :   " + str(self.network.getWorkloads())

        if self.verbose:
            print "INFO:    Simulation ended at:"
            print "INFO:        time                            :   " + str(datetime.datetime.now())

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
            self.plotStrategy.plot(self.network)
        if plotStrategy is not None:
            plotStrategy.plot(self.network)
