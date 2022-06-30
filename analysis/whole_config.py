import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from util import arpc

def load_dataframe(filename):
    df = pd.read_csv(filename)
    df['arpc'] = df['ci'].map(eval).map(arpc) * 100
    return df

def dev_plot(df, filename):
    sns.set(style="whitegrid")
    df = df[df.technique == 'Dev']
    fig, axs = plt.subplots(ncols=2)
    meanprops = {"marker": "D", "markerfacecolor": "white", "markeredgecolor": "black"}
    sns.boxplot(data=df, y='arpc', showmeans=True, ax=axs[0], color='gainsboro', width=0.25, meanprops=meanprops)

    ## add no. datapoints
    #axs[0].text(y=df['arpc'].median(), x=-0.33, s='n={}'.format(len(df)), rotation='vertical')

    ## set ylim
    ylim = 50  # df['arpc'].quantile(0.99)
    axs[0].set_ylim(top=ylim, bottom=-5)

    ## add no. fliers
    no_fliers = len(df[df['arpc'] > ylim])
    axs[0].text(y=ylim - 5, x=-0.2, s='> {}'.format(no_fliers) if no_fliers else '', rotation='vertical')

    ## set ylabel
    axs[0].set_ylabel('Performance change (%)')

    ## Second boxplot
    sns.boxplot(data=df, y='exectime', showmeans=True, ax=axs[1], color='gainsboro', width=0.25, meanprops=meanprops)

    ## set ylabel
    axs[1].set_ylabel('Execution time (sec)')

    ## add no. datapoints
    #axs[1].text(y=df['exectime'].median(), x=-0.33, s='n={}'.format(len(df)), rotation='vertical')

    plt.tight_layout()
    plt.savefig(filename)


def dyn_plot(df, filename):
    sns.set(style="whitegrid")
    df = df[df.technique != 'Dev']
    fig, axs = plt.subplots(ncols=2, figsize=[8.6, 4.8])

    width = 0.35
    order = ['Cov', 'Ci', 'Divergence']
    meanprops = {"marker": "D", "markerfacecolor": "white", "markeredgecolor": "black"}

    sns.boxplot(data=df, x='technique', y='arpc', showmeans=True, ax=axs[0],
                color='gainsboro', meanprops=meanprops, width=width, order=order)

    ## add no. datapoints
    # axs[0].text(y=df['arpc'].median(), x=-0.33, s='n={}'.format(len(df)), rotation='vertical')

    ## set ylim
    ylim = 50  # df['arpc'].quantile(0.99)
    axs[0].set_ylim(top=ylim, bottom=-5)

    ## add no. fliers
    for i, label in enumerate(axs[0].get_xticklabels()):
        t = label.get_text()
        df_ = df[df['technique'] == t]
        no_fliers = len(df_[df_['arpc'] > ylim])
        axs[0].text(y=ylim - 6, x=i - 0.2, s='> {}'.format(no_fliers) if no_fliers else '', rotation='vertical')

    ## set labels
    axs[0].set_ylabel('Performance change (%)')
    axs[0].set_xlabel('')

    ## Second boxplot
    sns.boxplot(data=df, x='technique', y='exectime', showmeans=True, ax=axs[1],
                color='gainsboro', meanprops=meanprops, width=width, order=order)

    ## set labels
    axs[1].set_ylabel('Execution time (sec)')
    axs[1].set_xlabel('')

    ## add no. datapoints
    # axs[1].text(y=df['exectime'].median(), x=-0.33, s='n={}'.format(len(df)), rotation='vertical')

    ## set ylim
    ylim = 999  # df['arpc'].quantile(0.99)
    axs[1].set_ylim(top=ylim, bottom=-5)

    ## add no. fliers
    for i, label in enumerate(axs[1].get_xticklabels()):
        t = label.get_text()
        df_ = df[df['technique'] == t]
        no_fliers = len(df_[df_['exectime'] > ylim])
        axs[1].text(y=ylim - 70, x=i - 0.2, s='> {}'.format(no_fliers) if no_fliers else '', rotation='vertical')

    for ax in axs:
        labels = {'Cov': 'CV', 'Ci': 'RCIW', 'Divergence': 'KLD'}
        techniques = [l.get_text() for l in ax.get_xticklabels()]
        # ax.set_xticks(range(len(techniques)), labels=[labels[t] for t in techniques] )
        ax.set_xticklabels([labels[t] for t in techniques])
    plt.tight_layout()
    plt.savefig(filename)


if __name__ == '__main__':
    df = load_dataframe('../data/whole_cfg_assessment.csv')
    dev_plot(df, '../figures/wholeconfig_dev.pdf')
    dyn_plot(df, '../figures/wholeconfig_dyn.pdf')

    pd.set_option('display.max_columns', None)
    print(df.groupby('technique').describe().round(1))

    print(pd.read_csv('../data/subjects.csv'))

