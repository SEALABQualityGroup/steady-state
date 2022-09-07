import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from util import arpc

#pd.options.display.float_format = '{:,}'.format
#pd.options.display.int_format = '{:,}'.format


def boxplot(df, filename, yscale='linear', ylim=None):
    sns.set( style="whitegrid")
    fig, ax = plt.subplots(figsize=(3.2, 4.8))
    meanprops = {"marker": "D", "markerfacecolor": "white", "markeredgecolor": "black"}
    sns.boxplot(data=df, y='arpc',
                meanprops=meanprops,
                palette=['gainsboro'],
                width=0.25,
                showmeans=True,
                ax=ax)
    ax.text(y=df['arpc'].median(), x=-0.33, s='n={}'.format(len(df)), rotation='vertical')
    plt.yscale(yscale)
    plt.ylabel("Performance change (%)")
    if ylim:
        plt.ylim(top=ylim)
        no_fliers = len(df[df['arpc'] > ylim])
        ax.text(y=ylim - 5, x=-0.2, s='> {}'.format(no_fliers) if no_fliers else '', rotation='vertical')

    plt.tight_layout()
    plt.savefig(filename)

def table(df, filename):
    df = df.copy()
    df.style.format('{:,}')

    df['project']  = df['project'].map(lambda p: p.split('__')[1])

    g = df[['project', 'arpc']].groupby('project').agg(['count', 'mean', 'std', 'median'])
    g.columns = g.columns.droplevel()
    g = g.iloc[g.index.str.lower().argsort()]
    g.rename(columns={'count':'n'}, inplace=True)
    g = g[g['n'] > 5]

    df_others = df[~df['project'].isin(g.index)]
    if not df_others.empty:
        g.loc['others', 'mean'] = df_others.arpc.mean()
        g.loc['others', 'median'] = df_others.arpc.median()
        g.loc['others', 'std'] = df_others.arpc.std()
        g.loc['others', 'n'] = len(df_others)

    g.loc['Total', 'mean'] = df.arpc.mean()
    g.loc['Total', 'median'] = df.arpc.median()
    g.loc['Total', 'std'] = df.arpc.std()
    g.loc['Total', 'n'] = len(df)

    g['n'] = g['n'].map(int)

    for c in g.columns:
        g[c] = g[c].round(1).map('{:,}'.format)

    g.round(1).reset_index().to_latex(filename, index=False)



def load_dataframe(filename):
    df = pd.read_csv(filename)
    df['arpc'] = df['ci'].map(eval).map(arpc) * 100
    df['project'] = df.benchmark.map(lambda b: b.split('#')[0])
    return df


def within_fork_analysis():
    df = load_dataframe('../data/steady-impact-within-fork.csv')
    fig_filename = '../figures/steady-impact-within-fork.pdf'
    tab_filename = '../tables/steady-impact-within-fork.tex'
    boxplot(df, fig_filename, yscale='symlog')
    table(df, tab_filename)
    print("within_fork_analysis")
    print("mean:", df['arpc'].mean())
    print("q1:", df['arpc'].quantile(0.25))
    print("median:", df['arpc'].median())
    print("q3:", df['arpc'].quantile(0.75))


def across_fork_analysis():
    df = load_dataframe('../data/steady-impact-across-forks.csv')
    fig_filename = '../figures/steady-impact-across-fork.pdf'
    tab_filename = '../tables/steady-impact-across-fork.tex'
    boxplot(df, fig_filename, ylim=60)
    table(df, tab_filename)
    print("across_fork_analysis")
    print("mean:", df['arpc'].mean())
    print("q1:", df['arpc'].quantile(0.25))
    print("median:", df['arpc'].median())
    print("q3:", df['arpc'].quantile(0.75))


def main():
    within_fork_analysis()
    across_fork_analysis()

if __name__ == '__main__':
    main()