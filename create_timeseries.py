import json
import os
from analysis.util import mean, tosec
from glob import glob

folder_path = './data/jmh'
root_folder = './data/timeseries'
timeseries_folder = '{}/all'.format(root_folder)

for dir_ in [root_folder, timeseries_folder]:
    if not os.path.exists(dir_):
        os.mkdir(dir_)


def toseries(fork, scoreUnit):
    series = map(mean, fork)
    series = map(lambda x: tosec(x, scoreUnit), series)
    return list(series)


def create_timeseries():
    for path in glob("{}/*.json".format(folder_path)):
        out_path = "{}/{}".format(timeseries_folder, path.split('/')[-1])
        if os.path.exists(out_path):
            print('Skipped:', out_path, 'already exists')
            continue

        try:
            with open(path) as f:
                data = json.load(f)
                rawDataHistogram = data[0]['primaryMetric']['rawDataHistogram']
                scoreUnit = data[0]['primaryMetric']['scoreUnit']
                timeseries = [toseries(fork, scoreUnit) for fork in rawDataHistogram]

            with open(out_path, mode='w') as f:
                json.dump(timeseries, f)

        except json.JSONDecodeError:
            print('Skipped', path, 'for JSONDecodeError')

if __name__ == '__main__':
    create_timeseries()