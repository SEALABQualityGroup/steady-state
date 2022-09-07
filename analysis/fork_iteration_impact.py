import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

from util import arpc

def load_dataframe(filename):
    df = pd.read_csv(filename)
    df['arpc'] = df['ci'].map(eval).map(arpc) * 100
    return df


def iteration_analysis(filename, stats=False):
    df = load_dataframe('../data/iteration-impact.csv')

    if stats:
        g = df.groupby('iteration').agg({'arpc': ['mean', 'median']}).reset_index()
        g = g[g['iteration']>=300]

        print("Mean ARPC - min={}, max={}".format(g['arpc']['mean'].min(), g['arpc']['mean'].max()))
        print("Median ARPC - min={}, max={}".format(g['arpc']['median'].min(), g['arpc']['median'].max()))

    fig, axs = plt.subplots(2, 2, figsize=(11, 8))

    sns.lineplot(data=df, x='iteration', y='arpc', ax=axs[0, 0], color='gray')
    sns.lineplot(data=df, x='iteration', y='arpc', estimator=np.median, ax=axs[0, 1], color='gray')

    sns.lineplot(data=df[df.iteration <= 500], x='iteration', y='arpc', ax=axs[1, 0], color='gray')
    sns.lineplot(data=df[df.iteration <= 500], x='iteration', y='arpc', estimator=np.median, ax=axs[1, 1], color='gray')

    axs[0, 0].set_ylabel('Mean Performance change (%)')
    axs[0, 1].set_ylabel('Median Performance change (%)')
    axs[0, 0].set_xlabel('')
    axs[0, 1].set_xlabel('')

    axs[1, 0].set_title('')
    axs[1, 1].set_title('')
    axs[1, 0].set_ylabel('Mean Performance change (%)')
    axs[1, 1].set_ylabel('Median Performance change (%)')
    axs[1, 0].set_xlabel('Warmup Iterations')
    axs[1, 1].set_xlabel('Warmup Iterations')


    plt.tight_layout()
    plt.savefig(filename)


def fork_analysis(filename, stats=False):
    df = load_dataframe('../data/fork-impact.csv')
    df['fork'] += 1
    fig, axs = plt.subplots(1,2, figsize=(11, 4))

    if stats:
        print(df.groupby('fork').agg({'arpc':['mean', 'median']}))

    sns.lineplot(data=df, x='fork', y='arpc', ax=axs[0], color='gray')
    sns.lineplot(data=df, x='fork', y='arpc', estimator=np.median, ax=axs[1], color='gray')

    axs[0].set_ylabel('Mean Performance change (%)')
    axs[1].set_ylabel('Median Performance change (%)')
    axs[0].set_xlabel('Forks')
    axs[1].set_xlabel('Forks')

    plt.xlim(right=10.5)

    plt.tight_layout()
    plt.savefig(filename)


def main():
    sns.set(font_scale=1.1, style='white')
    iteration_analysis('../figures/iteration-impact.pdf')
    fork_analysis('../figures/fork-impact.pdf', stats=True)


if __name__ == '__main__':
    main()
