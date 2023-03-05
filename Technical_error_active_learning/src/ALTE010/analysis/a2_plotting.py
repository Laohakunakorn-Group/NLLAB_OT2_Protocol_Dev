"""
This script cleans and tidys the rawdata set and returns a csv ready for plotting.
It determines what type of plate reader etc to correctly process the data
"""
### import

import json
import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


# import experimental design parameters
with open("./settings/design_parameters.json") as json_file:
    design_parameters = json.load(json_file)


### read in the tidy dataset
print()
print("Reading in ./output/Datasets/tidy_data.csv")

tidy_data = pd.read_csv("./output/Datasets/tidy_data.csv")

# drop TempC Column
if design_parameters["Plot_Temperature"] == False:
    tidy_data = tidy_data.drop('TempC', axis=1)
else:
    pass


print(tidy_data)


## first plot all the wells

# get all the well names - Time
wells = list(tidy_data.columns)
wells.remove("Time")

#save_path = "./output/plots/"

fig = plt.figure(figsize=(10,5))

for well in wells:
    
    ax = sns.lineplot(x="Time", y=well, data=tidy_data)

fig.suptitle("Average MAE over rounds")
fig.tight_layout()


plt.savefig("test.png")
##### Save fig



# make directory for sticking the output in
#if os.path.isdir(save_path) == False:
#    os.mkdir(save_path, mode=0o777)


#navigate to tidy_data_files
#os.chdir(save_path)


#
