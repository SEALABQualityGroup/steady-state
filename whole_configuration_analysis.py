import math
import os.path
from multiprocessing import Pool
import json

import pandas as pd

from util import foreach_benchmark, create_fullname_column
import kalibera


def load_timeseries(benchmark):
    filename = './data/timeseries/all/{}.json'.format(benchmark)
    with open(filename) as f:
        return json.load(f)

def load_devconfig(benchmark):
    df = pd.read_csv('./data/subjects.csv')
    df['name'] = create_fullname_column(df)
    df.set_index('name', inplace=True)
    forks = df.loc[benchmark, 'forks']

    with open("./data/devconfig/{}.json".format(benchmark)) as f:
        return json.load(f)[:forks]

def load_dynconfig(technique, benchmark):
    with open("./data/dynconfig/{}/{}.json".format(technique,benchmark)) as f:
        return json.load(f)

def get_measurements(timeseries, cfg):
    measurements = []
    for ts, (last_warmup_it, last_measure_it) in zip(timeseries, cfg):
        measurements.append(ts[last_warmup_it + 1: last_measure_it + 1])
    return measurements

def foreach_technique():
    for b, timeseries, classification in foreach_benchmark():
        forks = classification['forks']
        steady_state_starts = classification['steady_state_starts']
        stable = [ts[s + 1:] for ts, c, s in zip(timeseries, forks, steady_state_starts) if c == 'steady state']

        cfg = load_devconfig(b)
        yield b, 'Dev', stable, get_measurements(timeseries, cfg)

        for technique in ['Ci', 'Cov', 'Divergence']:
            cfg = load_dynconfig(technique, b)
            yield b, technique, stable, get_measurements(timeseries, cfg)


def confidence_interval(bench_technique_stable_measur):
    b, technique, stable, measurements = bench_technique_stable_measur
    print('Running benchmark {} for technique {}'.format(b, technique))
    return b, technique, kalibera.interval_benchmark(measurements, stable)

def init_whole_cfg_assessment(pool):
    results = pool.map(confidence_interval, foreach_technique())
    return  pd.DataFrame(results, columns=['benchmark', 'technique', 'ci'])


def _compute_exectime(timeseries, cfg):
    cumulative_time = 0
    for ts, (_, last_measure_it) in zip(timeseries, cfg):
        for m in ts[: last_measure_it + 1]:
            no_invocations = math.ceil(0.1/m)
            cumulative_time += no_invocations*m
    return cumulative_time


def compute_exectime(bench_tech):
    benchmark, technique = bench_tech
    timeseries = load_timeseries(benchmark)

    if technique == 'Dev':
        cfg = load_devconfig(benchmark)
    else:
        cfg = load_dynconfig(technique, benchmark)

    return _compute_exectime(timeseries, cfg)


if __name__ == '__main__':
    with Pool(30) as pool:
        filename = './data/whole_cfg_assessment.csv'
        if not os.path.exists(filename):
            df = init_whole_cfg_assessment(pool)
        else:
            df = pd.read_csv(filename)

        df['exectime'] = pool.map(compute_exectime, zip(df.benchmark,df.technique))
        df.to_csv(filename, index=False)
