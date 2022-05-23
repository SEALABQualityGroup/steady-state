import json
from multiprocessing import Pool

import pandas as pd

import kalibera
from util import foreach_benchmark
from configuration_analysis import estimate_time


def load_config(benchmark):
    cfg_dir = "./data/default_config"
    filename = "{}/{}.json".format(cfg_dir, benchmark)
    with open(filename) as f:
        return json.load(f)


def process(bench_fork_ts_s_cfg):
    b, i, ts, s, (last_warmup_it, last_measure_it) = bench_fork_ts_s_cfg
    print("Running fork {} of {}".format(b, i))

    # Computing confidence interval
    measurements = ts[last_warmup_it+1: last_measure_it+1]
    stable = ts[s+1:]
    ci = kalibera.interval_fork(measurements, stable)

    # Computing (non-absolute) warmup estimation error
    warmup_time = estimate_time(ts[:last_warmup_it + 1])
    steady_state_time = estimate_time(ts[:s + 1])
    wee = warmup_time - steady_state_time

    return b, i, ci, wee


def foreach_steady_fork():
    for b, timeseries, classification in foreach_benchmark():
        steady_state_starts = classification['steady_state_starts']
        classes = classification['forks']
        cfg = load_config(b)
        for i, ts in enumerate(timeseries):
            if classes[i] == 'steady state':
                yield b, i, ts, steady_state_starts[i], cfg[i]


if __name__ == '__main__':
    with Pool() as pool:
        results = pool.map(process, foreach_steady_fork())
        df = pd.DataFrame(results, columns=['benchmark', 'fork', 'ci', 'timewaste'])
        df.to_csv('./data/default_cfg_assessment.csv', index=False)