import numpy as np
import random

BOOTSTRAP_ITERATIONS = 10000

def simulated_mean(measurements):
    sim_measurements = [x for sim_fork in random.choices(measurements, k=len(measurements))
                          for x in random.choices(sim_fork, k=len(sim_fork))]
    return np.mean(sim_measurements)

def interval_benchmark(m1, m2, significance=0.05):
    means = [simulated_mean(m1)/simulated_mean(m2) for _ in range(BOOTSTRAP_ITERATIONS)]
    return np.quantile(means, significance/2), np.quantile(means, 1-significance/2)


def interval_fork(m1, m2, significance=0.05):
    means = [np.mean(random.choices(m1, k=len(m1)))/np.mean(random.choices(m2, k=len(m2)))
             for _ in range(BOOTSTRAP_ITERATIONS)]
    return np.quantile(means, significance/2), np.quantile(means, 1-significance/2)


def test(m1, m2, es=0.05, significance=0.05):
    ci = interval_fork(m1, m2, significance)
    return ci[1] <= 1 - es or ci[0] >= 1 + es

