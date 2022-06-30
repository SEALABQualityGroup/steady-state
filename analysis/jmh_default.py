import pandas as pd
from scipy.stats import wilcoxon

from rq4 import a12, interpret


def arpc(ci):
    lb, ub = ci
    if lb <= 1 <= ub:
        return 0
    center = (lb + ub)/2
    return abs(center - 1)

def load_devdata():
    df = pd.read_csv('../data/cfg_assessment.csv')
    df['ci'] = df.interval
    return df[(df.classification == 'steady state') & (df.technique == 'Dev')]

def load_defaultdata():
    return pd.read_csv('../data/default_cfg_assessment.csv')

def prepare(df):
    df.set_index(['benchmark', 'fork'], inplace=True)

    df['ARPC'] = df.ci.map(eval).map(arpc)
    df['ARPC'] = df['ARPC'].map(lambda x: x if x >= 0.05 else 0.0)

    df['WEE'] = df['timewaste'].map(abs)
    df['WEE'] = df['WEE'].map(lambda x: x if x >= 5 else 0)

    df['wt'] = df['timewaste']


def compare(default_data, dev_data, score):
    default_scores = default_data[score].tolist()
    dev_scores = dev_data[score].tolist()

    _, p = wilcoxon(default_scores, dev_scores)
    A = a12(default_scores, dev_scores)
    return p, A


if __name__ == '__main__':
    dev_data = load_devdata()
    default_data = load_defaultdata()

    prepare(dev_data)
    prepare(default_data)
    
    for score in ['WEE']: #, 'ARPC', 'wt']:
        # Developer configurations perform better than default configurations if p<0.05 and  A > 0.5
        p, A = compare(default_data, dev_data, score)
        print('Metric:', score)
        print("p-value={}, A={}, interpretation={}\n".format(p, A, interpret(A)))
        print('\nDefaults stats:')
        print(default_data['WEE'].describe())
        print('\nDevs stats:')
        print(dev_data['WEE'].describe())



