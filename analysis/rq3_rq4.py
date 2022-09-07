#!/usr/bin/env python
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os

FIGURE_DIR = '../figures'

if not os.path.exists(FIGURE_DIR):
    os.mkdir(FIGURE_DIR)

def lb_effect(ci):
    res = 0
    if ci[1] < 1:
        res = abs(ci[1] - 1)
    elif ci[0] > 1:
        res = ci[0] - 1
    return res * 100

def effect(ci):
    res = 0
    if ci[1] < 1:
        res = abs((ci[1] + ci[0])/2 - 1)
    elif ci[0] > 1:
        res = (ci[1] + ci[0])/2 - 1
    return res * 100

def change_width(ax, new_value):
    for patch in ax.patches:
        current_width = patch.get_width()
        diff = current_width - new_value

        # we change the bar width
        patch.set_width(new_value)

        # we recenter the bar
        patch.set_x(patch.get_x() + diff * .5)

def change_height(ax, new_value):
    for patch in ax.patches:
        current_width = patch.get_height()
        diff = current_width - new_value

        # we change the bar width
        patch.set_height(new_value)

        # we recenter the bar
        patch.set_y(patch.get_y() + diff * .5)



df = pd.read_csv('../data/cfg_assessment.csv')
df = df[(df.classification == "steady state")]
df["type"] = df.timewaste.apply(lambda x: "overestimated" if x >= 5 else "underestimated" if x <= -5 else "exact")
df["time"] = abs(df.timewaste)
df['effect'] = df.interval.map(eval).map(effect)
df['lb_effect'] = df.interval.map(eval).map(lb_effect)


def viz_warmup_estimation_old(df, technique, filename):
    sns.set(style="whitegrid")
    df = df[(df.technique == technique)]

    fig, axs = plt.subplots(ncols=2, gridspec_kw={'width_ratios': [1, 1.5]})

    palette = ["whitesmoke", "silver"]
    types = ["underestimated", "overestimated"]

    sns.barplot(x=types,
                y=[(len(df[df.type == t]) / len(df)) * 100 for t in types],
                ax=axs[0],
                palette=palette,
                edgecolor="gray")

    sns.boxplot(x="type", y="time", width=0.3, data=df[df.type != "exact"], ax=axs[1],
                palette=palette,
                meanprops={"marker": "D", "markerfacecolor": "white", "markeredgecolor": "black"},
                showmeans=True,  # whis=[5, 95],
                showfliers=True)

    xlim = 600
    axs[1].text(y=10, x=-0.33, s='n={}'.format(len(df[df.type == types[0]])), rotation='vertical')
    axs[1].text(y=10, x=1 - 0.33, s='n={}'.format(len(df[df.type == types[1]])), rotation='vertical')

    no_fliers_underestimated = len(df[(df.type == types[0]) & (df.time > xlim)])
    no_fliers_overestimated = len(df[(df.type == types[1]) & (df.time > xlim)])
    axs[1].text(y=xlim - 50, x=-0.1,
                s='> {}'.format(no_fliers_underestimated) if no_fliers_underestimated else '', rotation='vertical')
    axs[1].text(y=xlim - 50, x=0.9,
                s='> {}'.format(no_fliers_overestimated) if no_fliers_overestimated else '', rotation='vertical')

    axs[0].set_ylabel('Percentage of steady state forks (%)')
    axs[0].set_ylim(top=101)
    axs[0].xaxis.set_tick_params(rotation=15)
    change_width(axs[0], 0.45)

    axs[1].set_ylim(bottom=-10, top=xlim  # df[df.type=="underestimated"].time.quantile(0.97)
                    )
    axs[1].set_xticklabels(['underestimated\n(time saved)', 'overestimated\n(time waste)'])
    axs[1].set_ylabel('Time (secs)')
    axs[1].set_xlabel('')

    plt.tight_layout()
    plt.subplots_adjust(wspace=0.25)
    plt.savefig(filename)
    plt.close('all')

def viz_warmup_estimation(df, technique, filename):
    sns.set(font_scale=1.1, style="whitegrid")
    plt.figure(figsize=(6, 6.2))

    df = df[(df.technique == technique)]

    fig, axs = plt.subplots(ncols=2, gridspec_kw={'width_ratios': [1.1, 1]})

    sns.boxplot(y='time', data=df,
                showmeans=True,  # whis=[5, 95],
                meanprops={"marker": "D", "markerfacecolor": "white", "markeredgecolor": "black"},
                palette=['gainsboro'],
                width=0.25,
                ax=axs[0])

    ylim = 150
    axs[0].set_ylim(-5, ylim)
    no_fliers = len(df[df.time > ylim])
    axs[0].text(y=ylim - 20, x=-0.2, s='> {}'.format(no_fliers) if no_fliers else '', rotation='vertical')
    axs[0].text(y=20, x=-0.33, s='n={}'.format(len(df)), rotation='vertical')
    axs[0].set_ylabel('Warmup Estimation Error (sec)')

    palette = ["whitesmoke", "silver"]
    types = ["underestimated", "overestimated"]

    sns.barplot(x=types,
                y=[(len(df[df.type == t]) / len(df)) * 100 for t in types],
                palette=palette,
                edgecolor="gray",
                ax=axs[1])

    patches = [mpatches.Patch(facecolor=c, label=l, edgecolor='gray') for l, c in zip(types, palette)]
    axs[1].legend(loc='upper left', handles=patches)

    axs[1].set_ylabel('Percentage of steady state forks (%)')
    axs[1].set_ylim(top=90)

    axs[1].xaxis.set_tick_params(labelcolor='white', rotation=10)#ax.set_xticks([])
    change_width(axs[1], 0.4)

    plt.tight_layout()
    plt.savefig(filename)
    plt.close('all')

def viz_underestimation_effect(df, technique, filename):
    sns.set(style="whitegrid")
    df = df[(df.technique == technique)]
    fig, axs = plt.subplots(ncols=2, gridspec_kw={'width_ratios': [1.75, 1]})

    effects = [5, 10, 25, 50]
    sns.barplot(x=["> {}%".format(e) for e in effects],
                y=[len(df[df.effect >= e]) / len(df) * 100 for e in effects],
                palette=['snow', 'whitesmoke', 'gainsboro', 'lightgrey'],
                edgecolor="gray",
                ax=axs[0])

    axs[0].set_ylabel('Percentage of underestimated forks (%)')
    axs[0].set_xlabel('Percentage change (%)')
    axs[0].set_ylim(top=80)
    change_width(axs[0], 0.6)

    sns.boxplot(y="effect", width=0.3, data=df,
                showmeans=True,  # whis=[5, 95],
                meanprops={"marker": "D", "markerfacecolor": "white", "markeredgecolor": "black"},
                palette=['whitesmoke'],
                showfliers=True, ax=axs[1])

    axs[1].text(y=2.5, x=-0.33, s='n={}'.format(len(df)), rotation='vertical')

    xlim = 59
    no_fliers = len(df[df.effect > xlim])
    axs[1].text(y=xlim - 7, x=-0.2, s='> {}'.format(no_fliers) if no_fliers else '', rotation='vertical')

    axs[1].set_ylim(top=xlim, bottom=-5)
    #axs[1].yaxis.set_label_position("right")
    axs[1].set_ylabel('Performance change (%)')
    axs[1].set_xlabel('Underestimated forks')

    plt.tight_layout()
    plt.subplots_adjust(wspace=0.35)

    plt.savefig(filename)
    plt.close('all')

def viz_overestimation_effect(df, technique, filename):
    sns.set(style="whitegrid")
    df = df[(df.technique == technique)]
    fig, axs = plt.subplots(ncols=2, gridspec_kw={'width_ratios': [1.75, 1]})

    effects = [10, 25, 50, 100]
    sns.barplot(x=["> {}".format(e) for e in effects],
                y=[len(df[df.time >= e]) / len(df) * 100 for e in effects],
                palette=['gainsboro', 'silver', 'darkgray', 'grey'],
                edgecolor="gray",
                ax=axs[0])

    axs[0].set_ylabel('Percentage of overestimated forks (%)')
    axs[0].set_xlabel('Time waste (sec)')
    axs[0].set_ylim(top=100)
    change_width(axs[0], 0.6)

    sns.boxplot(y="time", width=0.3, data=df,
                showmeans=True,  # whis=[5, 95],
                meanprops={"marker": "D", "markerfacecolor": "white", "markeredgecolor": "black"},
                palette=['silver'],
                showfliers=True, ax=axs[1])

    axs[1].text(y=2.5, x=-0.33, s='n={}'.format(len(df)), rotation='vertical')

    xlim = 100
    no_fliers = len(df[df.time > xlim])
    axs[1].text(y=xlim - 9, x=-0.2, s='> {}'.format(no_fliers) if no_fliers else '', rotation='vertical')

    axs[1].set_ylim(top=xlim, bottom=-5)
    #axs[1].yaxis.set_label_position("right")
    axs[1].set_ylabel('Time waste (sec)')
    axs[1].set_xlabel('Overestimated forks')


    plt.tight_layout()
    plt.subplots_adjust(wspace=0.35)

    plt.savefig(filename)
    plt.close('all')


for technique in ['Dev', 'Cov', 'Ci', 'Divergence']:
    viz_warmup_estimation(df, technique, "{}/warmup_estimation_{}.pdf".format(FIGURE_DIR, technique))
    viz_underestimation_effect(df[df.type == 'underestimated'],
                               technique,
                               "{}/underestimation_effect_{}.pdf".format(FIGURE_DIR, technique))
    viz_overestimation_effect(df[df.type == 'overestimated'],
                               technique,
                               "{}/overestimation_effect_{}.pdf".format(FIGURE_DIR, technique))




