import random
from multiprocessing import Pool

import pandas as pd

import kalibera
from util import foreach_benchmark

######### Fork impact

def foreach_steady_fork():
    for b, timeseries, classification in foreach_benchmark():
        for f in range(len(timeseries)):
            if classification['forks'][f] == 'steady state':
                yield b, f, timeseries[f], classification['steady_state_starts'][f]


def confidence_interval_within_fork(bench_fork_ts_start):
    b, f, ts, steady_state_starts = bench_fork_ts_start
    print('Running fork {} of benchmark'.format(f), b)
    stable = ts[steady_state_starts + 1:]
    unstable = ts[:steady_state_starts + 1]
    ci = kalibera.interval_fork(unstable, stable)
    return b, f, ci


def steadystate_impact_within_fork():
    with Pool() as pool:
        results = pool.map(confidence_interval_within_fork, foreach_steady_fork())
        return pd.DataFrame(results, columns=['benchmark', 'fork', 'ci'])


######### Benchmark impact
def foreach_inconsistent_benchmark():
    for b, timeseries, classification in foreach_benchmark():
        if classification['run'] == 'inconsistent':
            yield b, timeseries, classification


def confidence_interval_across_forks(bench_ts_class):
    b, timeseries, classification = bench_ts_class
    print('Running benchmark', b)
    steady = random.choice( [ts for ts, c in zip(timeseries, classification['forks']) if c == 'steady state'])
    nosteady = random.choice( [ts for ts, c in zip(timeseries, classification['forks']) if c == 'no steady state'])
    s = classification['steady_state_starts'][timeseries.index(steady)]
    stable = steady[s+1:]
    unstable = nosteady[s+1:]

    return b, kalibera.interval_fork(unstable, stable)


def steadystate_impact_across_forks():
    with Pool() as pool:
        results = pool.map(confidence_interval_across_forks, foreach_inconsistent_benchmark())
        return pd.DataFrame(results, columns=['benchmark', 'ci'])


### Main
if __name__ == '__main__':
    res_impact_fork = steadystate_impact_within_fork()
    res_impact_fork.to_csv('./data/steady-impact-within-fork.csv', index=False)

    res_impact_benchmark = steadystate_impact_across_forks()
    res_impact_benchmark.to_csv('./data/steady-impact-across-forks.csv', index=False)
