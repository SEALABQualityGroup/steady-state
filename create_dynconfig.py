from json import JSONDecodeError

from dynconfig import compute_config
from glob import glob
import os


TIMESERIES = './data/timeseries/all'
LAABERCONFIG_DIR = './data/dynconfig'

techniques = ['Cov', 'Ci', 'Divergence']

if not os.path.exists(LAABERCONFIG_DIR):
    os.mkdir(LAABERCONFIG_DIR)

for technique in techniques:
    dir_ = '{}/{}'.format(LAABERCONFIG_DIR, technique)
    if not os.path.exists(dir_):
        os.mkdir(dir_)

    for path in glob('{}/*.json'.format(TIMESERIES)):
        filename = path.split('/')[-1]
        out_file = '{}/{}'.format(dir_, filename)
        if not os.path.exists(out_file):
            try:
                print('Executing ', path, '...')
                compute_config(path, out_file, technique)
            except JSONDecodeError:
                print('Skipped', filename, 'for JSONDecodeError')
        else:
            print(out_file, ' already exists')
