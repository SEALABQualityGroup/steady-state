import json
import os
from multiprocessing import Pool
from operator import itemgetter

from dyre_util import HistUtil
from analysis.util import count, cov
from util import foreach_benchmark, load_jmhresult

no_measurements = 30
cov_threshold = 0.02


def get_benchmarks():
    return list(set(map(itemgetter(0), foreach_benchmark())))


# def foreach_fork():
#     for benchmark, jmhdata in foreach_jmhresult():
#         for i, fork_data in enumerate(jmhdata):
#             yield benchmark, i, fork_data


def create_config(fork):
    histutil = HistUtil()
    wi = -1
    for i, hist_ in enumerate(fork):
        histutil.add(hist_)
        hist = histutil.tohist()
        if count(hist) >= no_measurements:
            if cov(hist) < cov_threshold:
                return [wi, wi+no_measurements]
            else:
                wi = i + 1
                histutil.clear()

    return [-1, -1]


def process_benchmark(benchmark):
    data = load_jmhresult(benchmark)
    res = []
    for no_fork, fork in enumerate(data):
        print('Running', benchmark, 'fork', no_fork)
        cfg = create_config(fork)
        res.append(cfg)
    return res


def init_dir(dir_):
    if not os.path.exists(dir_):
        os.mkdir(dir_)


def write_results(benchmark, res_dir, cfg):
    filename = '{}/{}.json'.format(res_dir, benchmark)
    with open(filename, mode='w') as f:
        json.dump(cfg, f)


if __name__ == '__main__':
    res_dir = './data/georgesconfig'
    init_dir(res_dir)

    benchmarks = get_benchmarks()
    with Pool() as pool:
        results = pool.map(process_benchmark, benchmarks)
        for benchmark, cfg in zip(benchmarks, results):
            write_results(benchmark, res_dir, cfg)
