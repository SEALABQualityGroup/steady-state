import os
import json

from util import foreach_benchmark
from devconfig import estimate_iterations


## create if directory does not exist
def init_dir(res_dir):
    if not os.path.exists(res_dir):
        os.mkdir(res_dir)

## write benchmark default configs
def write_results(res_dir, b, res):
    with open("{}/{}.json".format(res_dir, b), mode='w') as f:
        json.dump(res, f)


if __name__ == '__main__':
    # JMH default version >= 1.21
    wt = 10
    wi = 5
    mt = 10
    mi = 5

    ## default config directory
    res_dir = "./data/default_config"
    init_dir(res_dir)

    ## compute and write default configs
    for b, timeseries, _ in foreach_benchmark():
        res = [estimate_iterations(ts, wt, wi, mt, mi) for ts in timeseries]
        write_results(res_dir, b, res)

