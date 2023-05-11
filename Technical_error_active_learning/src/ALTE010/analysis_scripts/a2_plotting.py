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


## time course
plot_timecourse_mean(fdbkp_experiment)

## bar plot

bar_plot_data = fdbkp_experiment[fdbkp_experiment["Time"] == 300]
# round data 
bar_plot_data.loc[:, "GFP_uM"] = bar_plot_data.loc[:, "GFP_uM"].round(2)

endpoint_barplot(bar_plot_data)