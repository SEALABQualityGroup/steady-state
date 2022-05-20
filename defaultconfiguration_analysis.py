import json
from multiprocessing import Pool

import pandas as pd

import kalibera
from util import foreach_benchmark


def load_config(benchmark):
    cfg_dir = "./data/default_config"
    filename = "{}/{}.json".format(cfg_dir, benchmark)
    with open(filename) as f:
        return json.load(f)


def compute_interval(bench_fork_meas_stable):
    b, i, measurements, stable = bench_fork_meas_stable
    print("Running fork {} of {}".format(b, i))
    return b, i, kalibera.interval_fork(measurements, stable)


def foreach_steady_fork():
    for b, timeseries, classification in foreach_benchmark():
        steady_state_starts = classification['steady_state_starts']
        classes = classification['forks']
        cfg = load_config(b)
        for i, ts in enumerate(timeseries):
            if classes[i] == 'steady state':
                s = steady_state_starts[i]
                last_warmup_it, last_measure_it = cfg[i]
                measurements = ts[last_warmup_it + 1: last_measure_it + 1]
                stable = ts[s + 1:]
                yield b, i, stable, measurements


if __name__ == '__main__':
    with Pool() as pool:
        results = pool.map(compute_interval, foreach_steady_fork())
        df = pd.DataFrame(results, columns=['benchmark', 'fork', 'ci'])
        df.to_csv('./data/default_cfg_assessment.csv', index=False)