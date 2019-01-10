import time
import os
import numpy as np
import multiprocessing
import matplotlib.pyplot as plt
import QueueNetworkSimulation as qns


def singleRun(args):
    (simObj, arrivalRate, effectiveServiceRate, result_num) = args
    singleRun.q.put([result_num, simObj.sims[result_num].singleRun(arrivalRate, effectiveServiceRate)])


def poolInit(q):
    singleRun.q = q


class parSim:

    def __init__(self, size, dispatchPolicyStrategy, convergenceConditionStrategy, plotStrategy=None, services=[],
                 workloads=[], historyWindowSize=10000, numOfRounds=100,
                 verbose=False, T_min=0, T_max=10000000, guess=False):
        self.sims = [qns.QueueNetworkSimulation(size, dispatchPolicyStrategy, convergenceConditionStrategy,
                                     plotStrategy=plotStrategy, services=services, workloads=workloads,
                                     historyWindowSize=historyWindowSize, numOfRounds=numOfRounds, verbose=verbose,
                                     T_min=T_min, T_max=T_max, guess=guess)
                     for k in range(numOfRounds)]
        self.results = [0.0] * (numOfRounds)

    def reset(self):
        for simu in self.sims:
            simu.reset()

    def parRun(self):
        if __name__ == '__main__':
            result_queue = multiprocessing.Queue()
            starttime = time.time()

            numOfRounds = len(self.sims)
            effectiveServiceRate = self.sims[0].getEffectiveServiceRate()
            arrivalRate = [0.0] * numOfRounds
            if effectiveServiceRate != 0:
                arrivalRate = np.arange(0, effectiveServiceRate, float(effectiveServiceRate) / float(numOfRounds))

            args = [(self, arrivalRate[i], effectiveServiceRate, i) for i in range(numOfRounds-1, -1, -1)]
            pool = multiprocessing.Pool(processes=8, initializer=poolInit, initargs=[result_queue])
            pool.imap(singleRun, args)
            pool.close()
            pool.join()

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

            while not result_queue.empty():
                result = result_queue.get()
                self.results[result[0]] = result[1]

            print self.results
            print('overall it took {} seconds'.format(time.time() - starttime))
            plt.plot(arrivalRate, self.results)
            plt.show()


rounds = 100
sim = parSim(3, qns.DispatchPolicyStrategy.RandomDStrategy(alpha=10, beta=1000, p=0.95, d=2),
             qns.ConvergenceConditionStrategy.VarianceConvergenceStrategy(epsilon=0.0001), verbose=True,
             numOfRounds=rounds, historyWindowSize=20000, T_min=500000, T_max=1000000000)
sim.parRun()
