#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import json
from glob import glob
import seaborn as sns
import matplotlib.pyplot as plt
import os

CLASS_DIR = '../data/classification'
FIGURE_DIR = '../figures'

if not os.path.exists(FIGURE_DIR):
    os.mkdir(FIGURE_DIR)

def create_frame():
    rows = []
    for path in glob('{}/*.json'.format(CLASS_DIR)):
        project = path.split('/')[-1].split('#')[0].split('__')[-1]
        with open(path) as f:
            data = json.load(f)
            no_steady_state = len([None for clas in data['forks'] if clas=='no steady state'])
            perc = (no_steady_state/len(data['forks']))*100
            rows.append([project, perc])
            rows.append(['Total', perc])
                

    df = pd.DataFrame(rows, columns=['project', 'no steady state'])

    return df


df = create_frame()


sns.set(rc={'figure.figsize':(30, 15)}, font_scale=3, style='whitegrid')

palette = {x:'whitesmoke' for x in df.project.unique()}
palette['Total'] = 'grey'

order = [p for p in df.project.unique() if p!='Total'] + ['Total']
ax = sns.boxplot(x='project', y='no steady state', data=df,
            palette=palette, order=order, width=0.7,
            showmeans=True,  meanprops={"marker": "D", "markerfacecolor": "white", "markeredgecolor": "black", "markersize":15})

ax.xaxis.set_tick_params(rotation=90)

plt.xlabel('')
plt.ylabel('Percentages of no steady state forks (%)')
plt.tight_layout()
plt.savefig( FIGURE_DIR + '/perc_no_steady_state.pdf')




