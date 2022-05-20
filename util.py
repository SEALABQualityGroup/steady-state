import os
import json

import pandas as pd

TS_DIR = './data/timeseries/all'
CLASS_DIR = './data/classification'
JMH_DIR = './data/jmh'

def create_fullname_column(df):
    return df.project.map(lambda s: s.replace('/', '__')) + '#' + df.benchmark + '#' + df.params.fillna('')

def foreach_benchmark():
    df = pd.read_csv('./data/subjects.csv')
    benchmarks = create_fullname_column(df)

    for b in benchmarks:
        pt = "{}/{}.json".format(TS_DIR, b)
        pc = "{}/{}.json".format(CLASS_DIR, b)

        if not os.path.exists(pt):
            continue
        with open(pt) as ft, open(pc) as fc:
            timeseries = json.load(ft)
            classification = json.load(fc)
            yield b, timeseries, classification

def load_jmhresult(benchmark):
    path = "{}/{}.json".format(JMH_DIR, benchmark)
    try:
        with open(path) as f:
            data = json.load(f)
            return data[0]['primaryMetric']['rawDataHistogram']

    except (KeyError, FileNotFoundError, json.JSONDecodeError):
        print('Skipped', benchmark)
