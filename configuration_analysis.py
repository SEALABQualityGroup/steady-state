import json
import re
from glob import glob
from math import ceil

import pandas as pd

import kalibera

CLASS_DIR = 'data/classification'
TS_DIR = 'data/timeseries/all'
DEVCFG_DIR = 'data/devconfig'
CICFG_DIR = 'data/dynconfig/Ci'
COVCFG_DIR = 'data/dynconfig/Cov'
DIVCFG_DIR = 'data/dynconfig/Divergence'


def foreach(cfg_dir):
    for ts_path in glob(TS_DIR + '/*.json'):
        fname = ts_path.split('/')[-1]
        benchmark = re.sub(r'\.json$', '', fname)
        clas_path = '{}/{}'.format(CLASS_DIR, fname)
        cfg_path = '{}/{}'.format(cfg_dir, fname)
        with open(ts_path) as fts, open(clas_path) as fclass, open(cfg_path) as fcfg:
            ts_list = json.load(fts)
            classification = json.load(fclass)
            cfg_list = json.load(fcfg)
            for fork, cfg in enumerate(cfg_list):
                    yield benchmark, fork, classification['forks'][fork], ts_list[fork],\
                          cfg, classification['steady_state_starts'][fork]


def estimate_time(measurements):
    time = 0
    for avgt in measurements:
        no_ops = ceil(0.1 / avgt)
        time += no_ops * avgt
    return time

def compute_timewaste(ts, cfg, steady_state_starts):
    last_warmup_it, _ = cfg
    warmup_time = estimate_time(ts[:last_warmup_it + 1])
    steady_state_time = estimate_time(ts[:steady_state_starts + 1])
    return warmup_time - steady_state_time

def compute_interval(ts, cfg, steady_state_starts):
    last_warmup_it, last_measure_it = cfg
    dev = ts[last_warmup_it + 1: last_measure_it + 1]
    stable = ts[steady_state_starts + 1:]
    return kalibera.interval_fork(dev, stable)


if __name__ == '__main__':
    techniques = ['Dev', 'Ci', 'Cov', 'Divergence']
    cfg_dirs = [DEVCFG_DIR, CICFG_DIR, COVCFG_DIR, DIVCFG_DIR]
    rows = []

    for technique, cfg_dir in zip(techniques, cfg_dirs):
        for benchmark, fork, clas, ts, cfg, steady_state_starts in foreach(cfg_dir):
            print("Starting assessment...")
            print("benchmark", benchmark)
            print("fork:", fork)
            print("technique", technique, '\n')

            last_warmup_it, last_measure_it = cfg

            timewaste = compute_timewaste(ts, cfg, steady_state_starts)
            interval = compute_interval(ts, cfg, steady_state_starts)

            row = [benchmark, fork, clas, steady_state_starts,
                   technique, last_warmup_it, last_measure_it, timewaste, interval]
            rows.append(row)

    df = pd.DataFrame(rows, columns=["benchmark", "fork", "classification", "steady_state_starts",
                                     "technique", "last_warmup_it", "last_measure_it", "timewaste", "interval"])
    df.to_csv('./data/cfg_assessment.csv', index=False)
