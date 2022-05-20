import json
import pandas as pd
from math import ceil
import sys
import re

def _get_warmup_and_measurement_info(project, benchmark, params):
    params = params.replace('(', '\\(').replace(')', '\\)').replace('|', '\\|')
    df = pd.read_csv('data/subjects.csv')
    row = df[(df.project == project) & (df.benchmark == benchmark) & (df.params.fillna('') == params)].iloc[0]
    return row['warmupTimeSec'], row['warmupIterations'], row['measurementTimeSec'], row['measurementIterations']


def _parse(path):
    path = re.sub(r'\.json$', '', path)
    project, benchmark, params = (path.split('/')[-1]
                                  .replace('__', '/')
                                  .split('#'))
    return project, benchmark, params

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

def _compute(timeseries, wt, wi, mt, mi):
    res = []
    for fork in timeseries:
        cfg = estimate_iterations(fork, wt, wi, mt, mi)
        res.append(cfg)

    return res

def estimate_iterations(fork,  wt, wi, mt, mi):
    warmup_iterations = _count_iterations(fork, wt, wi)
    measurement_iterations = _count_iterations(fork[warmup_iterations:], mt, mi)
    return [warmup_iterations - 1, warmup_iterations + measurement_iterations - 1]

def compute_config(path, out_filename):
    project, benchmark, params = _parse(path)
    wt, wi, mt, mi = _get_warmup_and_measurement_info(project, benchmark, params)
    timeseries = _load(path)

    res = _compute(timeseries, wt, wi, mt, mi)
    _dump(res, out_filename)


if __name__ == '__main__':
    in_filename = sys.argv[1]
    out_filename = sys.argv[2]
    compute_config(in_filename, out_filename)
