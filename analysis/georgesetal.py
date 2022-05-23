from glob import glob
import json

def percentage_halted():
    count = 0
    halted = 0
    for path in glob('../data/georgesconfig/*.json'):
        with open(path) as f:
            cfg = json.load(f)
            for (last_warmup_it, last_meas_it) in cfg:
                count += 1
                if last_meas_it != -1:
                    halted += 1
    prop = halted / count

    return round(prop * 100, 2)


if __name__ == '__main__':
    perc = percentage_halted()
    print('{}% of forks are halted by Georges et al.\'s technique'.format(perc) )