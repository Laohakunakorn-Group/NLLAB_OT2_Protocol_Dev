import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


# Time course all
def plot_timecourse_mean(fdbkp_experiment):
    
    fig = plt.figure(figsize=(10,5))

    sns.lineplot(x="Time", y= "GFP_uM", hue = "DNA_Template", data = fdbkp_experiment)

    fig.suptitle("Timecourse PoI-GFP Expression")
    fig.tight_layout()

    plt.savefig("/app/analysis_output/plots/timecourse_mean.png")


# bar plot
def show_values(axs, orient="v", space=.05):
    def _single(ax):
        if orient == "v":
            for p in ax.patches:
                _x = p.get_x() + p.get_width() / 2
                _y = p.get_y() + p.get_height() + (p.get_height()*0.01)
                value = '{:.1f}'.format(p.get_height())
                ax.text(_x, _y, value, ha="center") 
        elif orient == "h":
            for p in ax.patches:
                _x = p.get_x() + p.get_width() + float(space)
                _y = p.get_y() + p.get_height() - (p.get_height()*0.5)
                value = '{:.1f}'.format(p.get_width())
                ax.text(_x, _y, value, ha="left")

    if isinstance(axs, np.ndarray):
        for idx, ax in np.ndenumerate(axs):
            _single(ax)
    else:
        _single(axs)


def endpoint_barplot(bar_plot_data):
    
    fig_barplot = plt.figure(figsize=(10,5))

    ax = sns.barplot(x="DNA_Template", y= "GFP_uM", data = bar_plot_data)
    # show values above 
    show_values(ax, orient="v", space=0.05)

    fig_barplot.suptitle("PoI-GFP Expression at 300 mins")
    fig_barplot.tight_layout()

    plt.savefig("/app/analysis_output/plots/barplot_endpoint.png")