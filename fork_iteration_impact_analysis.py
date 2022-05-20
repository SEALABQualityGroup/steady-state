import random
from multiprocessing import Pool

import pandas as pd

import kalibera
from util import foreach_benchmark

def foreach_inconsistent_benchmark():
    for b, timeseries, classification in foreach_benchmark():
        if classification['run'] == 'inconsistent':
            yield b, timeseries, classification

def foreach_steady_benchmark():
    for b, timeseries, classification in foreach_benchmark():
        if classification['run'] == 'steady state':
            yield b, timeseries, classification


def foreach_iteration():
    for b, timeseries, classification in foreach_inconsistent_benchmark():
        steady = random.choice([ts for ts, c in zip(timeseries, classification['forks']) if c == 'steady state'])
        nosteady = random.choice([ts for ts, c in zip(timeseries, classification['forks']) if c == 'no steady state'])
        s = classification['steady_state_starts'][timeseries.index(steady)]
        stable = steady[s+1:]
        for i in range(0, 3000,50):
            unstable = nosteady[i:i+50]
            yield i, b, stable, unstable

def foreach_fork():
    for b, timeseries, classification in foreach_steady_benchmark():
        stable = [ts[s+1:] for ts, s in zip(timeseries, classification['steady_state_starts'])]
        unstable = [ts[:s+1] for ts, s in zip(timeseries, classification['steady_state_starts'])]
        for i in range(0, 10):
            yield i, b, stable, unstable[:i+1]

def foreach_fork_2():
    for b, timeseries, classification in foreach_inconsistent_benchmark():
        forks = classification['forks']
        steady_state_starts = classification['steady_state_starts']
        stable = [ts[s+1:] for ts, c, s in zip(timeseries, forks, steady_state_starts) if c=='steady state']
        unstable = []

        for ts, c, s in zip(timeseries, forks, steady_state_starts):
            ts = ts[s+1:] if c == 'steady state' else ts
            unstable.append(random.sample(ts, k=50))

        for i in range(0, 10):
            yield i, b, stable, unstable[:i+1]


def confidence_interval_iteration(it_bench_stable_unstable):
    i, b, stable, unstable = it_bench_stable_unstable
    print('Running iteration {} of benchmark'.format(i), b)
    return b, i, kalibera.interval_fork(unstable, stable)


def confidence_interval_fork(fork_bench_stable_unstable):
    f, b, stable, unstable = fork_bench_stable_unstable
    print('Running benchmark {} with {} forks'.format( b, f))
    return b, f, kalibera.interval_benchmark(unstable, stable)



def iteration_impact():
    with Pool() as pool:
        results = pool.map(confidence_interval_iteration, foreach_iteration())
        return pd.DataFrame(results, columns=['benchmark', 'iteration', 'ci'])

def fork_impact():
    with Pool() as pool:
        results = pool.map(confidence_interval_fork, foreach_fork())
        return pd.DataFrame(results, columns=['benchmark', 'fork', 'ci'])


def fork_impact_2():
    with Pool() as pool:
        results = pool.map(confidence_interval_fork, foreach_fork_2())
        return pd.DataFrame(results, columns=['benchmark', 'fork', 'ci'])


### Main
if __name__ == '__main__':
    res_iteration_impact = iteration_impact()
    res_iteration_impact.to_csv('./data/iteration-impact.csv', index=False)

    res_fork_impact = fork_impact()
    res_fork_impact.to_csv('./data/fork-impact.csv', index=False)

    res_fork_impact = fork_impact_2()
    res_fork_impact.to_csv('./data/fork-impact-2.csv', index=False)
