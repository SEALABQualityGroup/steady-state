from bisect import bisect_left, bisect_right

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.patches import Rectangle
from scipy.stats import wilcoxon, rankdata
import os

from util import arpc

FIGURE_DIR = '../figures'
TABLE_DIR = '../tables'

for dir_ in [FIGURE_DIR, TABLE_DIR]:
    if not os.path.exists(dir_):
        os.mkdir(dir_)

def perfscore(ci):
    res = 0
    if ci[1] < 1:
        res = (ci[1] + ci[0]) / 2 - 1
    elif ci[0] > 1:
        res = (ci[1] + ci[0]) / 2 - 1
    return abs(res)

def a12(treatment, control):
    m = len(treatment)
    n = len(control)

    r = rankdata(treatment + control)
    r1 = sum(r[0:m])

    # Compute the measure
    return (r1 / m - (m + 1) / 2) / n  # formula (14) in Vargha and Delaney, 2000


def create_transf_frame(df, techniques):
    df_trasf = df.copy()
    ## apply transformation
    # for t in techniques + ['Dev']:
    #     df_trasf['timescore'][t] = df_trasf['timescore'][t].map(lambda x: x if x >= 5 else 0)
    #     df_trasf['perfscore'][t] = df_trasf['perfscore'][t].map(lambda x: x if x >= 0.05 else 0.0)
    return df_trasf

def interpret(A):
    assert (0 <= A <= 1)

    magnitude = ["N", "S", "M", "L"]
    if A >= 0.5:
        levels = [0.56, 0.64, 0.71]
        i = bisect_right(levels, A)
    else:
        levels = [0.29, 0.34, 0.44]
        magnitude.reverse()
        i = bisect_left(levels, A)

    return magnitude[i]

def create_value_latex(row):
    p = '$<$0.001' if row['p-value'] < 0.001 else round(row['p-value'], 3)
    A = round(row['A'], 2) if row['p-value'] <= 0.05 else '-'
    value = "{}({})".format(p, A)
    cell = "\textbf{" + value + "}" if row['A'] > 0.5 and row['p-value'] <= 0.05 else value
    subscripts = {"N": "\textcolor{white}{***}",
                  "S": "*\textcolor{white}{**}",
                  "M": "**\textcolor{white}{*}",
                  "L": "***"}

    if row['p-value'] <= 0.05:
        subscript = subscripts[interpret(row['A'])]
    else:
        subscript = subscripts['N']

    return cell + "\tiny{$^{^{" + subscript + "}}$}"


def create_value(row):
    p = '<0.001' if row['p-value'] < 0.001 else round(row['p-value'], 3)
    A = round(row['A'], 2)
    return "{}({})".format(p, A)

def create_frame(df):
    techniques = ['Cov', 'Ci', 'Divergence']
    #df = df[df.classification == 'steady state']

    df['arpc'] = df.ci.map(eval).map(arpc)

    scores = ['arpc', 'exectime']

    df = df.pivot(['benchmark'], columns='technique', values=scores)
    df_trasf = create_transf_frame(df, techniques)

    rows = []
    for score in scores:
        for technique in techniques:
            df_ = df[score][['Dev', technique]].dropna()
            df_trasf_ = df_trasf[score][['Dev', technique]].dropna()

            dev_scores = df_['Dev'].to_list()
            technique_scores = df_[technique].to_list()

            statistic, p = wilcoxon(dev_scores, technique_scores)

            dev_scores = df_trasf_['Dev'].to_list()
            technique_scores = df_trasf_[technique].to_list()

            A = a12(dev_scores, technique_scores)
            rows.append([score, technique, p, A])

    return pd.DataFrame(rows, columns=['score', 'technique', 'p-value', 'A'])


def create_results(df):
    results = pd.DataFrame()
    for proj in df['project'].unique():
        df_ = df[df['project'] == proj]
        res = create_frame(df_)
        res['project'] = proj
        results = results.append(res, ignore_index=True)

    res = create_frame(df)
    res['project'] = 'Total'
    results = results.append(res, ignore_index=True)

    #results['value'] = results.apply(create_value, axis=1)
    results['value'] = results.apply(create_value_latex, axis=1)

    results['ES'] = results.apply(lambda row: interpret(row['A']) if row['p-value'] <= 0.05 else '-', axis=1)
    return results

def write_detailed_results(results, score):
    pd.options.display.max_colwidth = -1
    results_ = results[results.score == score].pivot(index='project', columns='technique', values='value')
    index = list(sorted( [idx for idx in results_.index if idx !='Total'], key=lambda s: s.lower()))
    index.append('Total')
    results_ = results_.reindex(index)

    #results_[['Cov', 'Ci', 'Divergence']].to_csv('./{}/wholeconfig_{}.csv'.format(TABLE_DIR, score))
    results_[['Cov', 'Ci', 'Divergence']].to_latex('{}/rq4_{}.tex'.format(TABLE_DIR, score), escape=False)

def write_summary_results(results, score):
    techniques = ['Cov', 'Ci', 'Divergence']
    techniques_labels = ['CV', 'RCIW', 'KLD']
    effect_sizes = ['N', 'S', 'M', 'L']
    a12_thresholds = [0.29, 0.34, 0.44, 0.5, 0.56, 0.64, 0.71]

    results_ = results[results.score == score]
    results_['ES'] = results_.apply(lambda row: interpret(row['A']) if row['p-value'] <= 0.05 else '-', axis=1)

    rows = []
    for t in techniques:
        row = []
        for es in effect_sizes[::-1]:
            count = results_[(results_.technique == t) & (results_.ES == es) & (results_.A < 0.5)].shape[0]
            row.append(count) #/ results_[(results_.technique == t)].shape[0])

        for es in effect_sizes:
            count = results_[(results_.technique == t) & (results_.ES == es) & (results_.A >= 0.5)].shape[0]
            row.append(count) #/ results_[(results_.technique == t)].shape[0])

        rows.append(row)

    columns = [es+'<' for es in effect_sizes[::-1]] + [es+'>' for es in effect_sizes]

    sns.set(font_scale=2.4)
    fig, ax = plt.subplots(figsize=[15.4, 6])
    sns.heatmap(pd.DataFrame(rows, columns=columns, index=techniques_labels),
                annot=True, cmap='Greys', cbar=False, vmin=0, vmax=18, linewidths=0.05, linecolor='gray',
                ax=ax)

    ax.add_patch(Rectangle((0,0), 4, 3, ec='dimgray', fc='none', lw=2))
    ax.add_patch(Rectangle((4, 0), 4, 3, ec='dimgray', fc='none', lw=2))

    ax.set_yticks([y - 0.2 for y in ax.get_yticks()])
    ax.set_yticklabels([item.get_text() for item in ax.get_yticklabels()])

    for x, t in enumerate(a12_thresholds, start=1):
        ax.text(x - 0.2, 3.3, t)

    ax.xaxis.tick_top()
    ax.set_xticklabels([item.get_text().replace('<', '').replace('>', '') for item in ax.get_xticklabels()])

    plt.xlabel('Vargha-Delanay\'s $\hat{A}_{12}$', labelpad=35)
    plt.tight_layout()
    plt.savefig('./{}/wholeconfig_{}.pdf'.format(FIGURE_DIR, score))


if __name__ == '__main__':
    df = pd.read_csv('../data/whole_cfg_assessment.csv')
    df['project'] = df.benchmark.map(lambda b: b.split('#')[0].split('__')[1])

    results = create_results(df)

    print(results)

    for score in results.score.unique():
        write_detailed_results(results, score)
        write_summary_results(results, score)
