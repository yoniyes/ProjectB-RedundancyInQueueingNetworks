import numpy as np
import matplotlib.pyplot as plt

########################################################################################################################
# The purpose of this file is to try and find parameters that display different behaviours under different redundancy
# levels for a system with 4 servers and the redundancy-d (level) is in [1, 2, 4]. The method used is scanning the
# probability (@p) for a usual workload (@alpha) job and plot the constraining formulas dictated by @alpha, @p, @miu
# (while @miu is the service rate of each server) and the level of redundancy used. We assume that servers have the same
# @miu.
# Here, we specifically look for a certain @miu and @alpha, what are the @p and betas that give us a change for the
# better with d=2 and a change for the worse with d=4 (all compared to d=1).
########################################################################################################################

########################################################################################################################
#   CONSTANTS
########################################################################################################################
alpha = 10
miu = 0.001
p_resolution = 1000

########################################################################################################################
#   LAMBDAS
########################################################################################################################
# These are actually the formulas that constrain the value of beta (unusual big workload job).
# d = 1
f = lambda p: ((1.0 / miu) - float(alpha) * p) / (1.0 - p)
# d = 2
g = lambda p: ((1.0 / (2.0 * miu)) - float(alpha) * (1.0 - (1.0 - p) ** 2)) / ((1.0 - p) ** 2)
# d = 4
h = lambda p: ((1.0 / (4.0 * miu)) - float(alpha) * (1.0 - (1.0 - p) ** 2)) / ((1.0 - p) ** 4)


########################################################################################################################
#   MAIN
########################################################################################################################
# The '100' is there to provide better scaling for relevant plot.
px = [float(x)/p_resolution for x in range(1, p_resolution-30)]
fp = [f(p) for p in px]
gp = [g(p) for p in px]
hp = [h(p) for p in px]

########################################################################################################################
#   PLOTS
########################################################################################################################
# for y in range(90, 121):
#     plt.plot(px, [y for x in px], linestyle='dashed', color='grey')
# plt.plot(px, fp, 'red', label=r'$f(p)$')
# plt.plot(px, gp, 'green', label=r'$g(p)$')
# plt.plot(px, hp, 'blue', label=r'$h(p)$')

plt.semilogy(px, fp, 'red', label=r'$f(p)$')
plt.semilogy(px, gp, 'green', label=r'$g(p)$')
plt.semilogy(px, hp, 'blue', label=r'$h(p)$')
# plt.fill_between(px, gp, hp, where=(gp >= hp), facecolor='lightgreen', interpolate=True)
plt.xlabel(r'$p$')
plt.ylabel(r'$\beta$')
plt.legend()
plt.xlim(0.1)
# plt.ylim(0.0, 1.0 / miu)
# plt.savefig('alpha=' + str(alpha) + ',miu=' + str(miu) + '.png')
plt.show()
