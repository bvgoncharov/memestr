import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

log_bfs = np.array([])
snrs = np.array([])
trials = np.array([])

for i in range(32):
    data = np.loadtxt('Injection_log_bfs_snr_60_{}.txt'.format(i))
    snrs = np.append(snrs, data[:, 0])
    trials = np.append(trials, data[:, 1])
    memory_log_bfs = np.append(log_bfs, data[:, 2])


# for i in range(32, 97):
#     data = np.loadtxt('Injection_log_bfs/Injection_log_bfs_{}.txt'.format(i))
#     log_bfs = np.append(log_bfs, data[:, 0])
#     trials = np.append(trials, data[:, 1])

plt.plot(np.cumsum(log_bfs))
plt.xlabel('Number of events')
plt.ylabel('Cumulative log BF')
plt.show()
plt.clf()

plt.hist(log_bfs, bins=int(np.sqrt(len(log_bfs))))
plt.xlabel('log BFs')
plt.show()
plt.clf()

plt.hist(snrs, bins=int(np.sqrt(len(snrs))))
plt.xlabel('SNRs')
plt.show()
plt.clf()

plt.hist(trials, bins=int(np.sqrt(len(trials))))
plt.xlabel('trials')
plt.show()
plt.clf()
import sys
sys.exit(0)

#
# minimums = []
#
# for i in range(10000):
#     print(i)
#     np.random.shuffle(log_bfs)
#     minimums.append(np.min(np.cumsum(log_bfs)))
# minimums = np.loadtxt('minimums.txt')
# percentiles = np.percentile(minimums, [100*(1-0.9999994), 100*(1-0.99994), 0.3, 5, 32])
# plt.hist(minimums, alpha=0.5, bins=100)
# plt.xlim(15, -5)
# colors = ['red', 'orange', 'cyan', 'black', 'green']
# for i in range(len(percentiles)):
#     plt.axvline(percentiles[i], label='${}\sigma$'.format(5 - i), color=colors[i])
# plt.legend()
# plt.xlabel('Minimum log BF')
# plt.ylabel('Count')
# plt.semilogy()
# plt.show()
# plt.clf()
# maximums = []

# for i in range(1000000):
#     print(i)
#     np.random.shuffle(log_bfs)
#     maximums.append(np.max(np.cumsum(log_bfs)))
# maximums = np.loadtxt('maximums.txt')
maximums = np.loadtxt('maximums.txt')
# pcs = [99.99994, 99.994, 99.7, 95, 68]
pcs = 100*(-1/np.linspace(1/.50, 1/.9999994, 100) + 1.4999994)
percentiles = np.percentile(maximums, pcs)
for percentage, log_bf in zip(pcs, percentiles):
    print(str(1 - percentage/100) + '\t' + str(1/np.exp(log_bf)))
# plt.semilogy()
plt.plot(1 - pcs/100, 1/np.exp(percentiles))
plt.plot([0, 0.5], [0, 0.5])
plt.show()
plt.clf()
# plt.hist(maximums, alpha=0.5, bins=1000)
# plt.xlim(-5, 15)
# colors = ['red', 'orange', 'cyan', 'black', 'green']
# for i in range(len(percentiles)):
#     plt.axvline(percentiles[i], label='${}\sigma$'.format(5 - i), color=colors[i])
# plt.legend()
# plt.xlabel('Maximum log BF')
# plt.ylabel('Count')
# plt.semilogy()
# plt.show()
# plt.clf()

