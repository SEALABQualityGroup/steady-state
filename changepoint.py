import json
from math import log

import numpy as np
import rpy2
import rpy2.interactive.packages
import rpy2.robjects
from kneed import KneeLocator


def crops(measurements):
    cpt = rpy2.interactive.packages.importr('changepoint')
    ts = rpy2.robjects.FloatVector(measurements)
    pen_value = tuple(float(m * log(len(measurements))) for m in [4, 100000])
    crops_ = cpt.cpt_meanvar(ts, method='PELT', penalty='CROPS',
                             pen_value=rpy2.robjects.FloatVector(pen_value))
    crops_full = cpt.cpts_full(crops_)
    ncpts = []

    for i in range(1, crops_full.nrow + 1):
        ncpts.append(len([x for x in map(int, crops_full.rx(i, True)) if x > 0]))

    penalties = [x for x in cpt.pen_value_full(crops_)]
    if len(penalties) == len(ncpts) + 1:
        ncpts.append(0)

    assert (len(penalties) == len(ncpts))
    return penalties, ncpts

def find_penalty(measurements):
    penalties, ncpts = crops(measurements)
    default_pen = 15 * log(len(measurements))

    if len(penalties) < 2 or len(ncpts) < 2:
        return penalties[0]

    try:
        kneedle = KneeLocator(penalties[::-1], ncpts[::-1], S=1.0, curve="convex", direction="decreasing")
        penalty = kneedle.elbow if kneedle.elbow else default_pen
    except IndexError:
         penalty = default_pen

    return float(penalty)


def pelt(ts):
    penalty = find_penalty(ts)
    cpt = rpy2.interactive.packages.importr('changepoint')
    measurements = rpy2.robjects.FloatVector(ts)
    changepoints = cpt.cpt_meanvar(measurements, method='PELT', penalty='Manual',
                                   pen_value=penalty)
    # List indices in R start at 1.
    return [int(cpoint - 1) for cpoint in changepoints.slots['cpts']]


def changepoint(ts_path, filtered_path, changepoints_path):
    with open(ts_path) as f_ts,  open(filtered_path) as f_filtered, open(changepoints_path, 'w') as f_cpts:
        ts_list = json.load(f_ts)
        filtered = json.load(f_filtered)
        results = []

        for ts, indexes in zip(ts_list, filtered):
            ts = np.array(ts)[indexes].tolist()
            # detect changepoints indexes
            cpts_ = pelt(ts)
            # lead back indexes to series without outliers
            cpts_ = np.array(indexes)[cpts_].tolist()

            results.append(cpts_)

        json.dump(results, f_cpts)

