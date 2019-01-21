import time
import datetime
import os
import numpy as np
import multiprocessing
import matplotlib.pyplot as plt
import QueueNetworkSimulation as qns


def poolInit(q):
    singleRun.q = q


def singleRun(args):
    (simObj, arrivalRate, effectiveServiceRate, result_num) = args
    try:
        return [result_num, arrivalRate, simObj[0].sims[result_num].singleRun(arrivalRate, effectiveServiceRate)]
    except Exception:
        print('arrivalRate, result_num = %f, %d' % (arrivalRate, result_num))


class parSim(qns.QueueNetworkSimulation):

    def __init__(self, size, dispatchPolicyStrategy, convergenceConditionStrategy, plotStrategy=None, services=[],
                 workloads=[], historyWindowSize=10000, numOfRounds=100, verbose=False, T_min=0, T_max=10000000,
                 guess=False):
        qns.QueueNetworkSimulation.__init__(self, size, dispatchPolicyStrategy, convergenceConditionStrategy,
                                            plotStrategy, services, workloads, historyWindowSize, numOfRounds, verbose,
                                            T_min, T_max, guess)
        self.size = size
        self.sims = [qns.QueueNetworkSimulation(size, dispatchPolicyStrategy, convergenceConditionStrategy,
                                     plotStrategy=plotStrategy, services=services, workloads=workloads,
                                     historyWindowSize=historyWindowSize, numOfRounds=numOfRounds, verbose=verbose,
                                     T_min=T_min, T_max=T_max, guess=guess)
                     for k in range(numOfRounds)]
        self.results = [[0.0] * self.numOfRounds for i in range(2)]

    def reset(self):
        for simu in self.sims:
            simu.reset()
        self.results = [[0.0] * self.numOfRounds for i in range(2)]

    def parRun(self):
        if __name__ == '__main__':
            result_queue = multiprocessing.Queue()
            starttime = time.time()
            start_time = datetime.datetime.now()

            numOfRounds = len(self.sims)
            effectiveServiceRate = self.sims[0].getEffectiveServiceRate()
            arrivalRate = [0.0] * numOfRounds
            if effectiveServiceRate != 0:
                arrivalRate = np.arange(0, effectiveServiceRate, float(effectiveServiceRate) / float(numOfRounds))
            # self.results[0] = arrivalRate

            args = [([self], arrivalRate[i], effectiveServiceRate, i) for i in range(numOfRounds-1, -1, -1)]

            pool = multiprocessing.Pool(processes=8, initializer=poolInit, initargs=[result_queue])
            res = pool.imap(singleRun, args)
            pool.close()
            pool.join()
            # print res.get()
            r = res.next()
            while r:
                # print r
                self.results[0][r[0]] = r[1]
                self.results[1][r[0]] = r[2]
                try:
                    r = res.next()
                except:
                    break

            # print self.results

            # processes = []
            # for i in range(numOfRounds-1, -1, -1):
            #     sim = self.sims[i]
            #     p = multiprocessing.Process(target=sim.singleRun, args=(arrivalRate[i],
            #                                                             effectiveServiceRate, result_queue, i))
            #     processes.append(p)
            #     p.start()
            #
            # for process in processes:
            #     process.join()

            print "DONE"

            # while not result_queue.empty():
            #     result = result_queue.get()
            #     self.results[1][result[0]] = result[1]

            end_time = datetime.datetime.now()
            if self.verbose:
                print "INFO:    Simulation ended at:"
                print "INFO:        time                            :   " + str(end_time)

            # Save results to file.
            if self.verbose:
                print "INFO:    Saving results to file [ " + datetime.datetime.now().strftime(
                    "%Y%m%d-%H%M%S") + "_queue_net_sim.dump ]"
            fd = open(datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + '_queue_net_sim.dump', 'w')
            for val in self.results[0]:
                fd.write(str(val) + ",")
            fd.write("\n")
            for val in self.results[1]:
                fd.write(str(val) + ",")
            fd.write("\n")
            fd.write("\n")
            fd.write("INFO:        time started                    :   " + str(start_time) + "\n")
            fd.write("INFO:        time ended                      :   " + str(end_time) + "\n")
            fd.write("INFO:        number of servers               :   " + str(self.size) + "\n")
            fd.write("INFO:        dispatch policy                 :   " +
                     self.dispatchPolicyStrategy.getName() + "\n")
            fd.write("INFO:        redundancy                      :   " +
                     str(self.dispatchPolicyStrategy.getRedundancy()) + "\n")
            fd.write("INFO:        params                          :   " +
                     self.dispatchPolicyStrategy.getParamStr() + "\n")
            fd.write("INFO:        convergence condition           :   " +
                     self.convergenceConditionStrategy.getName() + "\n")
            fd.write("INFO:        convergence precision           :   " +
                     str(self.convergenceConditionStrategy.getPrecision()) + "\n")
            fd.close()
            print('overall it took {} seconds'.format(time.time() - starttime))

    def plot(self, x=None, y=None, plotStrategy=None):
        self.plotStrategy.plot(self.results[0], self.results[1])


if __name__ == '__main__':
    rounds = 30
    # sim = parSim(3, qns.DispatchPolicyStrategy.RandomDStrategy(alpha=10, beta=1000, p=0.95, d=2, bias=2.0),
    #              qns.ConvergenceConditionStrategy.VarianceConvergenceStrategy(epsilon=0.00005), verbose=True,
    #              numOfRounds=rounds, historyWindowSize=20000, T_min=500000, T_max=1000000000, plotStrategy=qns.PLOT())
    # sim = parSim(4, qns.DispatchPolicyStrategy.FixedSubsetsStrategy(alpha=10, beta=1000, p=0.95, redundancy=2),
    #              qns.ConvergenceConditionStrategy.VarianceConvergenceStrategy(epsilon=0.00005), verbose=True,
    #              numOfRounds=rounds, historyWindowSize=20000, T_min=500000, T_max=1000000000, plotStrategy=qns.PLOT())
    # sim = parSim(4, qns.DispatchPolicyStrategy.FixedSubsetsStrategy(alpha=10, beta=2000, p=0.43, redundancy=1),
    #              qns.ConvergenceConditionStrategy.VarianceConvergenceStrategy(epsilon=0.00005), verbose=True,
    #              numOfRounds=rounds, historyWindowSize=20000, T_min=500000, T_max=1000000000, plotStrategy=qns.PLOT())
    # sim.parRun()
    # # sim.plot()
    # sim = parSim(4, qns.DispatchPolicyStrategy.FixedSubsetsStrategy(alpha=10, beta=2000, p=0.43, redundancy=2),
    #              qns.ConvergenceConditionStrategy.VarianceConvergenceStrategy(epsilon=0.00005), verbose=True,
    #              numOfRounds=rounds, historyWindowSize=20000, T_min=500000, T_max=1000000000, plotStrategy=qns.PLOT())
    # sim.parRun()
    # # sim.plot()
    # sim = parSim(4, qns.DispatchPolicyStrategy.FixedSubsetsStrategy(alpha=10, beta=2000, p=0.43, redundancy=4),
    #              qns.ConvergenceConditionStrategy.VarianceConvergenceStrategy(epsilon=0.00005), verbose=True,
    #              numOfRounds=rounds, historyWindowSize=20000, T_min=500000, T_max=1000000000, plotStrategy=qns.PLOT())
    # sim.parRun()
    # # sim.plot()

    #sim = parSim(3, qns.DispatchPolicyStrategy.RandomDStrategy(alpha=10, beta=2000, p=0.8, d=2, bias=0.225*2),
    #             qns.ConvergenceConditionStrategy.VarianceConvergenceStrategy(epsilon=0.0001), verbose=True,
    #             numOfRounds=rounds, historyWindowSize=20000, T_min=500000, T_max=1000000000, plotStrategy=qns.PLOT())
    sim1 = parSim(3, qns.DispatchPolicyStrategy.RandomQueueStrategy(alpha=10, beta=2000, p=0.8),
                 qns.ConvergenceConditionStrategy.VarianceConvergenceStrategy(epsilon=0.0001), verbose=True,
                 numOfRounds=rounds, historyWindowSize=20000, T_min=500000, T_max=1000000000, plotStrategy=qns.PLOT())
    sim1.parRun()
    sim = parSim(3, qns.DispatchPolicyStrategy.RouteToIdleQueuesStrategy(alpha=10, beta=2000, p=0.8),
                 qns.ConvergenceConditionStrategy.VarianceConvergenceStrategy(epsilon=0.0001), verbose=True,
                 numOfRounds=rounds, historyWindowSize=20000, T_min=500000, T_max=1000000000, plotStrategy=qns.PLOT())
    sim.parRun()
    sim1.plot()
    sim.plot()
