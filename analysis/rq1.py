import json
from glob import glob
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

CLASS_DIR = '../data/classification'
FIGURE_DIR = '../figures'

if not os.path.exists(FIGURE_DIR):
    os.mkdir(FIGURE_DIR)


def transform_frame(df):
    series = df.groupby(['project', 'classification']).size() / df.groupby('project').size()
    series.name = "prop"

    df_ = series.to_frame().reset_index().pivot('project', 'classification', 'prop').fillna(0.0)
    df_ = df_.iloc[df_.index.str.lower().argsort()]
    df_.loc['Total'] = df.groupby('classification').size() / df.shape[0]

    #if 'no steady state' not in df_.columns:
    #    df_['no steady state'] = 0.0

    return df_[sorted(df_.columns)]

def heatmap(df, fname):
    df_ = transform_frame(df)

    sns.set(rc={'figure.figsize':(7, 15)}, font_scale=1.5)
    sns.heatmap(df_, annot=True, cmap='Greys', cbar=False, fmt=".1%", vmin=0, vmax=1.25)
    plt.ylabel('')
    plt.xlabel('')
    plt.tight_layout()
    plt.savefig(fname)
    plt.close('all')


def load_frames():
    rows_bench = []
    rows_forks = []
    for path in glob('{}/*.json'.format(CLASS_DIR)):
        project = path.split('/')[-1].split('#')[0].split('__')[-1]
        with open(path) as f:
            data = json.load(f)
            rows_bench.append([project, data['run']])
            rows_forks += [[project, clas] for clas in data['forks']]

    df_bench = pd.DataFrame(rows_bench, columns=['project', 'classification'])
    df_forks = pd.DataFrame(rows_forks, columns=['project', 'classification'])

    return df_bench, df_forks



if __name__ == '__main__':
    df_bench, df_forks = load_frames()

    heatmap(df_bench, FIGURE_DIR + '/rq1_benchmarks_heatmap.pdf')
    heatmap(df_forks, FIGURE_DIR + '/rq1_forks_heatmap.pdf')
