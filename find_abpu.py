import numpy as np
import matplotlib.pyplot as plt

########################################################################################################################
# The purpose of this file is to try and find parameters that display different behaviours under different redundancy
# levels for a system with 4 servers and the redundancy-d (level) is in [1, 2, 4]. The method used is scanning the
# probability (@p) for a usual workload (@alpha) job and plot the constraining formulas dictated by @alpha, @p, @mu
# (while @mu is the service rate of each server) and the level of redundancy used. We assume that servers have the same
# @mu.
# Here, we specifically look for a certain @mu and @alpha, what are the @p and betas that give us a change for the
# better with d=2 and a change for the worse with d=4 (all compared to d=1).
########################################################################################################################

########################################################################################################################
#   CONSTANTS
########################################################################################################################
# alpha = 10
# mu = 0.001
# p_resolution = 1000

########################################################################################################################
#   LAMBDAS
########################################################################################################################
# These are actually the formulas that constrain the value of beta (unusual big workload job).
# d = 1
# f = lambda p: ((1.0 / mu) - float(alpha) * p) / (1.0 - p)
# # d = 2
# g = lambda p: ((1.0 / (2.0 * mu)) - float(alpha) * (1.0 - (1.0 - p) ** 2)) / ((1.0 - p) ** 2)
# # d = 4
# h = lambda p: ((1.0 / (4.0 * mu)) - float(alpha) * (1.0 - (1.0 - p) ** 2)) / ((1.0 - p) ** 4)


########################################################################################################################
#   MAIN
########################################################################################################################
# The '30' is there to provide better scaling for relevant plot.
# px = [float(x)/p_resolution for x in range(1, p_resolution-30)]
# fp = [f(p) for p in px]
# gp = [g(p) for p in px]
# hp = [h(p) for p in px]

########################################################################################################################
#   PLOTS
########################################################################################################################
# for y in range(90, 121):
#     plt.plot(px, [y for x in px], linestyle='dashed', color='grey')
# plt.plot(px, fp, 'red', label=r'$f(p)$')
# plt.plot(px, gp, 'green', label=r'$g(p)$')
# plt.plot(px, hp, 'blue', label=r'$h(p)$')

# plt.semilogy(px, fp, 'red', label=r'$f(p)$')
# plt.semilogy(px, gp, 'green', label=r'$g(p)$')
# plt.semilogy(px, hp, 'blue', label=r'$h(p)$')
# # plt.fill_between(px, gp, hp, where=(gp >= hp), facecolor='lightgreen', interpolate=True)
# plt.xlabel(r'$p$')
# plt.ylabel(r'$\beta$')
# plt.legend()
# plt.xlim(0.1)
# # plt.ylim(0.0, 1.0 / miu)
# # plt.savefig('alpha=' + str(alpha) + ',mu=' + str(miu) + '.png')
# plt.show()


plt.rcParams.update({'font.size': 16})
alpha = 10.0
beta = 2000.0
f_p_d = lambda p, d: 1.0 / (d*(alpha*(1.0-(1.0-p)**d) + beta*(1.0-p)**d))
px = np.arange(0, 1.00001, 0.00001)
d1 = [f_p_d(p, 1) for p in px]
d2 = [f_p_d(p, 2) for p in px]
d4 = [f_p_d(p, 4) for p in px]
maximas = [0 for i in range(len(px)+1)]
for x in range(len(px)):
    maximas[x] = 1
    if d1[x] < d2[x]:
        maximas[x] = 2
        if d2[x] < d4[x]: maximas[x] = 4
    elif d1[x] < d4[x]:
        maximas[x] = 4
        if d4[x] < d2[x]: maximas[x] = 2
low = 0
high = 0
val = maximas[0]
for x in range(len(px)+1):
    if val == maximas[x]: continue
    color = ('lightcoral' if val == 1 else ('lightgreen' if val == 2 else 'skyblue'))
    high = x-1
    plt.axvspan(px[low], px[high], facecolor=color, alpha=0.5)
    low = x-1
    val = maximas[x]
p_12 = 0.5050766708
p_21 = 0.9949
p_14 = 0.3751469735
p_41 = 0.9849
p_24 = 0.2964921257
p_42 = 0.9287
plt.semilogy(px, d1, 'red', label=r'$d=1$')
plt.semilogy(px, d2, 'green', label=r'$d=2$')
plt.semilogy(px, d4, 'blue', label=r'$d=4$')
plt.axvline(p_12, linestyle='--')
plt.axvline(p_21, linestyle='--')
plt.axvline(p_14, linestyle='--')
plt.axvline(p_41, linestyle='--')
plt.axvline(p_24, linestyle='--')
plt.axvline(p_42, linestyle='--')
plt.xlabel(r'$p$')
plt.ylabel(r'$\dfrac{1}{d\mathbb{E}[b_{1} \wedge ... \wedge b_{d}]}$')
plt.legend()
plt.grid(True, which="both")
plt.title(r'The throughput of a system of 4 queues for different redundancy levels',
          wrap=True)
# plt.figtext(0.5, 0.03, r'$\alpha=$' + str(int(alpha)) + r', $\beta=$' + str(int(beta)) + r', $n=4$', wrap=True,
#             horizontalalignment='center', fontsize=8)
plt.show()
