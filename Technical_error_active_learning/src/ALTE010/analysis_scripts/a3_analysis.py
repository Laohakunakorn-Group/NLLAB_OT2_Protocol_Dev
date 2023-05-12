"""
This script cleans and tidys the rawdata set and returns a csv ready for plotting.
It determines what type of plate reader etc to correctly process the data
"""
### import

import json
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from sub_scripts.plotting_functions import *


# import experimental design parameters
#with open("./settings/design_parameters.json") as json_file:
#    design_parameters = json.load(json_file)

# Import
tidy_data = pd.read_csv("/app/analysis_output/tidy_dataset.csv")

## Initial trimming.
# drop negative control
tidy_data = tidy_data[tidy_data["DNA_Template"] != "None"]
fdbkp_experiment = tidy_data[tidy_data["Energy_Solution"] == "ES_ET_NTP"]
fdbkp_experiment = fdbkp_experiment[fdbkp_experiment["Time"] <= 300]
bar_plot_data = fdbkp_experiment[fdbkp_experiment["Time"] == 300]
# round data 
bar_plot_data.loc[:, "GFP_uM"] = bar_plot_data.loc[:, "GFP_uM"].round(2)

bar_plot_data = bar_plot_data.sort_values(by='GFP_uM', ascending=False)
print(bar_plot_data)
print(bar_plot_data.columns)

fig = plt.figure(figsize=(10,5))
fig.suptitle("GFP Signal vs ORF Length")
sns.scatterplot(data = bar_plot_data, y = "GFP_uM", x = "ORF_Length", hue = "DNA_Template")
plt.savefig("/app/analysis_output/plots/GFP Signal_vs_ORF_Length.png")


fig = plt.figure(figsize=(10,5))
fig.suptitle("GFP Signal vs Pre-GFP GC%")
sns.scatterplot(data = bar_plot_data, x = "GFP_uM", y = "ORF_GC%", hue = "DNA_Template")
plt.savefig("/app/analysis_output/plots/GFP_Signal_vs_Pre_GFP_GC%.png")


## just peg

peg_data = tidy_data[tidy_data["DNA_Template"] == "T7_GFP"]
print(peg_data["Energy_Solution"].unique())
print(peg_data["DNA_Template"].unique())

fig = plt.figure(figsize=(10,5))
fig.suptitle("PEG_8000% vs GFP_Signal")
ax = sns.barplot(data = peg_data, x = "Energy_Solution", y = "GFP_uM")
ax.set(xlabel='PEG-8000', ylabel='GFP_uM')
ax.set_xticklabels(["4%", "2%" ])
plt.savefig("/app/analysis_output/plots/PEG_8000%_vs_GFP_Signal.png")