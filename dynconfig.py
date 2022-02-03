import json
import pandas as pd
from math import ceil
import sys
import re

def _get_warmup_list(benchmark, params, technique):
    df = pd.read_csv('data/results_dyre/output{}Total.csv'.format(technique), sep=';')
    row = df[(df.benchmark == benchmark) & (df.params.fillna('') == params)].iloc[0]
    forks = row['reachedForks'] if row['reachedForks'] < 5 else 5
    warmup_list = [row['reachedF{}'.format(i)] for i in range(1, forks+1)]

    return [w if w < 50 else 50 for w in warmup_list]


def _parse(path):
    path = re.sub(r'\.json$', '', path)
    _, benchmark, params = (path.split('/')[-1]
                                  .split('#'))
    return benchmark, params

def _load(path):
    with open(path) as f:
        timeseries = json.load(f)
        return timeseries


def _dump(res, out_filename):
    with open(out_filename, mode='w') as f:
        json.dump(res, f)


def _count_iterations(fork, iteration_time, num_iterations):
    time = 0
    sim_iteration = 0
    for it, avgt in enumerate(fork, start=1):
        no_ops = ceil(0.1 / avgt)
        time += no_ops * avgt
        if time >= iteration_time:
            sim_iteration += 1
            time = 0
        if sim_iteration >= num_iterations:
            return it

    return len(fork)

def _compute(timeseries, warmup_list):
    res = []
    for fork, wi in zip(timeseries, warmup_list):
        wt = mt = 1
        mi = 10
        warmup_iterations = _count_iterations(fork, wt, wi)
        measurement_iterations = _count_iterations(fork[warmup_iterations:], mt, mi)
        res.append([warmup_iterations - 1,
                    warmup_iterations + measurement_iterations - 1])

    return res


def compute_config(path, out_filename, technique):
    benchmark, params = _parse(path)
    timeseries = _load(path)
    warmup_list = _get_warmup_list(benchmark, params, technique)
    res = _compute(timeseries, warmup_list)
    _dump(res, out_filename)

if __name__ == '__main__':
    in_filename = sys.argv[1]
    out_filename = sys.argv[2]
    technique = sys.argv[3]
    compute_config(in_filename, out_filename, technique)
