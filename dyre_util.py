import json
from analysis.util import mean, tosec
from math import ceil
import sys
import re
import pandas as pd


class HistUtil:
    def __init__(self):
        self.dict = {}

    def add(self, hist):
        for value, occ in hist:
            if value in self.dict:
                self.dict[value] += occ
            else:
                self.dict[value] = occ

    def tohist(self):
        keys = sorted(self.dict.keys())
        return [[value, self.dict[value]] for value in keys]

    def clear(self):
        self.dict = {}

def _parse(path):
    path = re.sub(r'\.json$', '', path)
    project, benchmark, params = (path.split('/')[-1]
                                  .replace('__', '/')
                                  .split('#'))
    return project, benchmark, params


def _load(path):
    with open(path) as f:
        data = json.load(f)
        return data

def _create_rows(data):
    rawDataHistogram = data[0]['primaryMetric']['rawDataHistogram']
    rows = []
    for f, fork in enumerate(rawDataHistogram, start=1):
        for i, hist in enumerate(fork, start=1):
            for value, occ in hist:
                row = [f, i, value, occ]
                rows.append(row)
    return rows

def _to_csv(project, benchmark, params, data, out_filename):
    columns = ["project", "commit", "benchmark", "params", "instance",
               "trial", "fork", "iteration", "mode", "unit", "value_count", "value"]
    rows = _create_rows(data)

    df = pd.DataFrame(rows, columns=["fork", "iteration", "value", "value_count"])
    df["project"] = project
    df["commit"] = ''
    df["benchmark"] = benchmark
    df["params"] = params
    df["instance"] = ''
    df["trial"] = 0
    df["mode"] = data[0]['mode']
    df["unit"] = data[0]['primaryMetric']['scoreUnit']

    df[columns].to_csv(out_filename, index=False, sep=';')


def _compute_iterations(fork, scoreUnit):
    time = 0
    newfork = []
    histutil = HistUtil()
    for hist in fork:
        histutil.add(hist)
        mean_ = tosec(mean(hist), scoreUnit)
        no_ops = ceil(0.1 / mean_)
        time += no_ops * mean_
        if time >= 1:
            newfork.append(histutil.tohist())
            histutil.clear()
            time = 0
    return newfork


def _compute(rawDataHistogram, scoreUnit):
    newRawDataHistogram = []
    for fork in rawDataHistogram:
        newfork = _compute_iterations(fork, scoreUnit)
        newRawDataHistogram.append(newfork)
    return newRawDataHistogram


def transform_json(path, out_filename):
    project, benchmark, params = _parse(path)
    data = _load(path)
    rawDataHistogram = data[0]['primaryMetric']['rawDataHistogram']
    scoreUnit = data[0]['primaryMetric']['scoreUnit']
    newRawDataHistogram = _compute(rawDataHistogram, scoreUnit)
    data[0]['primaryMetric']['rawDataHistogram'] = newRawDataHistogram
    data[0]["measurementTime"] = "1 s"
    _to_csv(project, benchmark, params, data, out_filename)


if __name__ == '__main__':
    in_filename = sys.argv[1]
    out_filename = sys.argv[2]
    transform_json(in_filename, out_filename)
