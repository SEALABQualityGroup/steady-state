from json import JSONDecodeError

from dyre_util import transform_json
from glob import glob
import os
import re


JMH_DATA = './data/jmh'
LAABER_DATA_DIR = './data/jmh_dyre'

if not os.path.exists(LAABER_DATA_DIR):
    os.mkdir(LAABER_DATA_DIR)

for path in glob('{}/*.json'.format(JMH_DATA)):
    filename = re.sub(r'\.json$', '.csv', path.split('/')[-1])
    out_file = '{}/{}'.format(LAABER_DATA_DIR, filename)
    if not os.path.exists(out_file):
        try:
            print('Executing ', path, '...')
            transform_json(path, out_file)
        except JSONDecodeError:
            print('Skipped', path.split('/')[-1], 'for JSONDecodeError')
    else:
        print(out_file, ' already exists')
