from QueueNetwork import QueueNetwork

class QueueNetworkSimulation:
    """Class for simulating a queue network in discrete time with a given dispatch policy."""

    ##
    # Initialize a queue network simulation given a size, services and initial workloads along with a dispatch policy
    # and a converge condition.
    # If only a size and policy were given, all queues will have service = 1, workload = 0.
    ##
    def __init__(self, size, dispatchPolicyStrategy, convergenceConditionStrategy, plotStrategy=None, services=[],
                 workloads=[]):
        # Member fields init.
        self.network = QueueNetwork(size, services=services, workloads=workloads)
        self.dispatchPolicyStrategy = dispatchPolicyStrategy
        self.convergenceConditionStrategy = convergenceConditionStrategy
        self.plotStrategy = plotStrategy

    ##
    # Initialize a queue network simulation given a size, services and initial workloads along with a dispatch policy.
    ##
    def reset(self):
        self.network.flush()

    ##
    # Set the dispatch policy.
    ##
    def setDispatchPolicy(self, dispatchPolicyStrategy):
        self.dispatchPolicyStrategy = dispatchPolicyStrategy

    ##
    # Set the convergence check function.
    ##
    def setConvergenceCondition(self, convergenceConditionStrategy):
        self.convergenceConditionStrategy = convergenceConditionStrategy

    ##
    # Set the plotting function.
    ##
    def setPlot(self, plotStrategy):
        self.plotStrategy = plotStrategy

    ##
    # Run the simulation.
    ##
    def run(self):
        pass

    ##
    # Load a network image to the simulation.
    ##
    def load(self, network):
        pass

    ##
    # Save simulation to a file.
    ##
    def save(self, name="queue_net_sim.dump"):
        pass

    ##
    # Plot results based on given plotting scheme.
    ##
    def plot(self, plotStrategy=None):
        if self.plotStrategy is not None:
            self.plotStrategy.plot(self.network)
        if plotStrategy is not None:
            plotStrategy.plot(self.network)
