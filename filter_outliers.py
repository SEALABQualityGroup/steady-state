from glob import glob
import json
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view as sliding_window
import os


def create_isoutlier(series, window):
    series_ = series[window]
    median = np.median(series_)
    p1, p99 = [np.quantile(series_, q) for q in [0.01, 0.99]]

    def _isoutlier(i):
        value = series[i]
        return value > (median + 3 * (p99 - p1)) or value < (median - 3 * (p99 - p1))

    return _isoutlier


def find_outliers(fork):
    series = np.array(fork)
    window_size = 200
    noops = np.ceil(0.1 / np.mean(series))
    skip = int(np.ceil(window_size / np.log1p(noops)))

    indexes = list(range(skip, len(series)))

    outliers = []
    for window in sliding_window(indexes, window_size):
        isoutlier = create_isoutlier(series, window)
        outliers += [i for i in window if isoutlier(i)]

    return np.unique(outliers)


def filter_(fork):
    outliers = find_outliers(fork)
    indexes = np.arange(len(fork))
    return np.setdiff1d(indexes, outliers).tolist()


def _filter_outliers(data_dir, filtered_dir):
    for path in glob('{}/*.json'.format(data_dir)):
        filename = path.split('/')[-1]
        filtered_path = '{}/{}'.format(filtered_dir, filename)

        if os.path.exists(filtered_path):
            print('Skipped:', filtered_path, 'already exists')
            continue

        with open(path) as f1, open(filtered_path, 'w') as f2:
            try:
                data = json.load(f1)
                print('Executing {}'.format(path))
                filtered = [filter_(fork) for fork in data]
                json.dump(filtered, f2)
            except json.JSONDecodeError:
                print('Skipped {}'.format(path))

def filter_outliers():
    root_dir = './data/timeseries'
    data_dir = '{}/all'.format(root_dir)
    filtered_dir = '{}/filtered'.format(root_dir)

    if not os.path.exists(filtered_dir):
        os.mkdir(filtered_dir)

    _filter_outliers(data_dir, filtered_dir)

if __name__ == '__main__':
    filter_outliers()