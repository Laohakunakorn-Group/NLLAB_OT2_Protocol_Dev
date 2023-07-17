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

product_name = "Darpin-GFP"


## Initial trimming.
# drop negative control
plotting_data = tidy_data[tidy_data["Time"] <= 250]

## time course
plot_timecourse_mean(plotting_data, product_name=product_name)

## bar plot
bar_plot_data = tidy_data[tidy_data["Time"] == 100]

# round data 
bar_plot_data.loc[:, "RFUs"] = bar_plot_data.loc[:, "RFUs"].round(2)

endpoint_barplot(bar_plot_data, product_name=product_name)