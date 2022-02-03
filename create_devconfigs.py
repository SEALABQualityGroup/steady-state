from json import JSONDecodeError

from devconfig import compute_config
from glob import glob
import os


TIMESERIES = './data/timeseries/all'
DEVCONFIG_DIR = './data/devconfig'

if not os.path.exists(DEVCONFIG_DIR):
    os.mkdir(DEVCONFIG_DIR)

for path in glob('{}/*.json'.format(TIMESERIES)):
    filename = path.split('/')[-1]
    out_file = '{}/{}'.format(DEVCONFIG_DIR, filename)
    if not os.path.exists(out_file):
        try:
            print('Executing ', path, '...')
            compute_config(path, out_file)
        except JSONDecodeError:
            print('Skipped', filename, 'for JSONDecodeError')
    else:
        print(out_file, ' already exists')
