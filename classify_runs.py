import json
import os
from glob import glob
from kalibera import test

STEADY_STATE = "steady state"
NO_STEADY_STATE = "no steady state"
INCONSISTENT = "inconsistent"


def load(path):
    with open(path) as f:
        data = json.load(f)
    return data


def write(data, path):
    with open(path, 'w') as f:
        json.dump(data, f)


def steady_state_starts(ts, cpts):
    cpts = [0] + cpts
    i = -2
    last_segment = ts[cpts[i] + 1:]
    while cpts[i] > 0:
        cpt = cpts[i]
        i -= 1
        prev_cpt = cpts[i]

        start = prev_cpt + 1 if prev_cpt > 0 else prev_cpt
        stop = cpt + 1
        current_segment = ts[start:stop]

        if test(last_segment, current_segment):
            return cpt

    return 0


def _classify_benchmark(forks):
    if STEADY_STATE not in forks:
        return NO_STEADY_STATE
    elif NO_STEADY_STATE in forks:
        return INCONSISTENT
    else:
        return STEADY_STATE


def classify_fork(ts, cpts):
    steady_state_starts_at = steady_state_starts(ts, cpts)
    if steady_state_starts_at <= 2499:
        classification = STEADY_STATE
    else:
        classification = NO_STEADY_STATE
        steady_state_starts_at = -1
    return classification, steady_state_starts_at


def classify_benchmark(ts_list, cpts_list):
    forks = []
    steady_state_starts_at = []
    for ts, cpts in zip(ts_list, cpts_list):
        fork_class, steady_state_starts_ = classify_fork(ts, cpts)
        forks.append(fork_class)
        steady_state_starts_at.append(steady_state_starts_)

    classification = _classify_benchmark(forks)
    return {"run": classification, "forks": forks, "steady_state_starts": steady_state_starts_at}


def classify_runs():
    root_dir = './data'
    measurements_dir = '{}/timeseries/all'.format(root_dir)
    changepoints_dir = '{}/changepoints'.format(root_dir)
    classification_dir = '{}/classification'.format(root_dir)

    if not os.path.exists(classification_dir):
        os.mkdir(classification_dir)

    for path in glob('{}/*.json'.format(measurements_dir)):
        filename = path.split('/')[-1]
        changepoints_path = '{}/{}'.format(changepoints_dir, filename)
        classification_path = '{}/{}'.format(classification_dir, filename)

        if not os.path.exists(classification_path):
            print("Executing {}".format(filename))
            ts_list = load(path)
            cpts_list = load(changepoints_path)

            classification = classify_benchmark(ts_list, cpts_list)
            write(classification, classification_path)
        else:
            print('Skipped: {} already exists'.format(classification_path))


if __name__ == '__main__':
    classify_runs()
